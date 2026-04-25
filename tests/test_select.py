"""Tests for TESmart KVM select entities."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.const import CONF_MODEL, DISPLAY_TIMEOUT_OPTIONS, DOMAIN
from custom_components.tesmart_kvm.coordinator import TesmartKvmCoordinator
from custom_components.tesmart_kvm.select import (
    TesmartActiveInputSelect,
    TesmartDisplayTimeoutSelect,
)


@pytest.fixture
def coordinator(hass: HomeAssistant) -> TesmartKvmCoordinator:
    """Create a coordinator for select tests."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="TESmart HKS801-EB23",
        data={
            CONF_MODEL: "HKS801-EB23",
            "host": "192.168.1.10",
            "port": 5000,
        },
        unique_id="192.168.1.10:5000",
    )
    entry.add_to_hass(hass)
    client = AsyncMock()
    return TesmartKvmCoordinator(hass, entry, client)


def test_active_input_select_options(coordinator: TesmartKvmCoordinator) -> None:
    """Test active input select options match model ports."""
    entity = TesmartActiveInputSelect(coordinator)

    assert entity.unique_id == f"{coordinator.entry.entry_id}_active_input"
    assert entity.options == ["1", "2", "3", "4", "5", "6", "7", "8"]


def test_active_input_current_option(coordinator: TesmartKvmCoordinator) -> None:
    """Test active input current option."""
    entity = TesmartActiveInputSelect(coordinator)

    assert entity.current_option is None
    coordinator.async_set_updated_data({"active_input": 3})
    assert entity.current_option == "3"


async def test_active_input_select_option(coordinator: TesmartKvmCoordinator) -> None:
    """Test selecting an active input delegates to the coordinator."""
    entity = TesmartActiveInputSelect(coordinator)
    coordinator.async_set_active_input = AsyncMock()

    await entity.async_select_option("5")

    coordinator.async_set_active_input.assert_awaited_once_with(5)


def test_display_timeout_select_options(coordinator: TesmartKvmCoordinator) -> None:
    """Test display timeout select options."""
    entity = TesmartDisplayTimeoutSelect(coordinator)

    assert entity.unique_id == f"{coordinator.entry.entry_id}_display_timeout"
    assert entity.options == list(DISPLAY_TIMEOUT_OPTIONS.values())


def test_display_timeout_current_option(coordinator: TesmartKvmCoordinator) -> None:
    """Test display timeout current option."""
    entity = TesmartDisplayTimeoutSelect(coordinator)

    assert entity.current_option is None
    coordinator.display_timeout = 0x1E
    assert entity.current_option == "30 Seconds"


async def test_display_timeout_select_option(coordinator: TesmartKvmCoordinator) -> None:
    """Test selecting display timeout delegates to the coordinator."""
    entity = TesmartDisplayTimeoutSelect(coordinator)
    coordinator.async_set_display_timeout = AsyncMock()

    await entity.async_select_option("10 Seconds")

    coordinator.async_set_display_timeout.assert_awaited_once_with(0x0A)
