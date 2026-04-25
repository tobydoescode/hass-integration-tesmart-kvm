"""Tests for the TESmart KVM config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with (
        patch(
            "custom_components.tesmart_kvm.config_flow.TesmartClient",
        ) as mock_cls,
        patch(
            "custom_components.tesmart_kvm.async_setup_entry",
            return_value=True,
        ),
    ):
        mock_cls.return_value.test_connection = AsyncMock(return_value=True)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MODEL: "HKS801-EB23",
                CONF_HOST: "192.168.1.10",
                CONF_PORT: 5000,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "TESmart HKS801-EB23"
    assert result["data"] == {
        CONF_MODEL: "HKS801-EB23",
        CONF_HOST: "192.168.1.10",
        CONF_PORT: 5000,
    }


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test config flow when device is unreachable."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.tesmart_kvm.config_flow.TesmartClient",
    ) as mock_cls:
        mock_cls.return_value.test_connection = AsyncMock(return_value=False)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MODEL: "HKS801-EB23",
                CONF_HOST: "192.168.1.10",
                CONF_PORT: 5000,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_already_configured(hass: HomeAssistant) -> None:
    """Test config flow aborts when device is already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="TESmart HKS801-EB23",
        data={
            CONF_MODEL: "HKS801-EB23",
            CONF_HOST: "192.168.1.10",
            CONF_PORT: 5000,
        },
        unique_id="192.168.1.10:5000",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.tesmart_kvm.config_flow.TesmartClient",
    ) as mock_cls:
        mock_cls.return_value.test_connection = AsyncMock(return_value=True)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MODEL: "HKS801-EB23",
                CONF_HOST: "192.168.1.10",
                CONF_PORT: 5000,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_rejects_port_below_range(hass: HomeAssistant) -> None:
    """Test config flow rejects ports below the TCP range."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MODEL: "HKS801-EB23",
                CONF_HOST: "192.168.1.10",
                CONF_PORT: 0,
            },
        )


async def test_user_flow_rejects_port_above_range(hass: HomeAssistant) -> None:
    """Test config flow rejects ports above the TCP range."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MODEL: "HKS801-EB23",
                CONF_HOST: "192.168.1.10",
                CONF_PORT: 65536,
            },
        )
