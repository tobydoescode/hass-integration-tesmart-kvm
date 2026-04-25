"""Tests for TESmart KVM setup and unload lifecycle."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm import PLATFORMS, async_setup_entry, async_unload_entry
from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN


def make_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
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
    return entry


async def test_async_setup_entry_success(hass: HomeAssistant) -> None:
    """Test setup stores coordinator and forwards platforms."""
    entry = make_entry(hass)

    with (
        patch("custom_components.tesmart_kvm.TesmartClient") as mock_client_cls,
        patch("custom_components.tesmart_kvm.TesmartKvmCoordinator") as mock_coordinator_cls,
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            AsyncMock(),
        ) as mock_forward,
    ):
        client = mock_client_cls.return_value
        coordinator = mock_coordinator_cls.return_value
        coordinator.async_config_entry_first_refresh = AsyncMock()

        result = await async_setup_entry(hass, entry)

    assert result is True
    mock_client_cls.assert_called_once_with("192.168.1.10", 5000)
    mock_coordinator_cls.assert_called_once_with(hass, entry, client)
    coordinator.async_config_entry_first_refresh.assert_awaited_once()
    assert hass.data[DOMAIN][entry.entry_id] is coordinator
    mock_forward.assert_awaited_once_with(entry, PLATFORMS)


async def test_async_setup_entry_disconnects_on_first_refresh_failure(
    hass: HomeAssistant,
) -> None:
    """Test setup disconnects the client when first refresh fails."""
    entry = make_entry(hass)

    with (
        patch("custom_components.tesmart_kvm.TesmartClient") as mock_client_cls,
        patch("custom_components.tesmart_kvm.TesmartKvmCoordinator") as mock_coordinator_cls,
    ):
        client = mock_client_cls.return_value
        client.disconnect = AsyncMock()
        coordinator = mock_coordinator_cls.return_value
        coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=RuntimeError("refresh failed")
        )

        with pytest.raises(RuntimeError, match="refresh failed"):
            await async_setup_entry(hass, entry)

    client.disconnect.assert_awaited_once()
    assert DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]


async def test_async_unload_entry_disconnects_client(hass: HomeAssistant) -> None:
    """Test unload removes coordinator data and disconnects the client."""
    entry = make_entry(hass)
    coordinator = AsyncMock()
    coordinator.client.disconnect = AsyncMock()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        AsyncMock(return_value=True),
    ) as mock_unload:
        result = await async_unload_entry(hass, entry)

    assert result is True
    mock_unload.assert_awaited_once_with(entry, PLATFORMS)
    coordinator.client.disconnect.assert_awaited_once()
    assert entry.entry_id not in hass.data[DOMAIN]
