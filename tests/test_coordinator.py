"""Tests for the TESmart KVM coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.client import TesmartConnectionError
from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN
from custom_components.tesmart_kvm.coordinator import TesmartKvmCoordinator


@pytest.fixture
def mock_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
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
    return entry


async def test_poll_active_input(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test polling returns the active input."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=3)

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    assert coordinator.data == {"active_input": 3}


async def test_poll_reconnects_on_disconnect(
    hass: HomeAssistant, mock_entry: MockConfigEntry
) -> None:
    """Test polling reconnects if the client is disconnected."""
    client = AsyncMock()
    client.connected = False
    client.connect = AsyncMock()
    client.get_active_input = AsyncMock(return_value=1)

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    client.connect.assert_called_once()
    assert coordinator.data == {"active_input": 1}


async def test_poll_raises_update_failed(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test polling raises UpdateFailed on connection error."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(side_effect=TesmartConnectionError("timeout"))

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    assert coordinator.last_update_success is False


async def test_set_active_input(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test switching active input calls the client."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=5)
    client.set_active_input = AsyncMock()

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()
    await coordinator.async_set_active_input(5)

    client.set_active_input.assert_called_once_with(5)


async def test_set_buzzer(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test setting buzzer updates assumed state."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=1)
    client.set_buzzer = AsyncMock()

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    assert coordinator.buzzer_enabled is None
    await coordinator.async_set_buzzer(True)
    assert coordinator.buzzer_enabled is True

    await coordinator.async_set_buzzer(False)
    assert coordinator.buzzer_enabled is False


async def test_set_display_timeout(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test setting display timeout updates assumed state."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=1)
    client.set_display_timeout = AsyncMock()

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    assert coordinator.display_timeout is None
    await coordinator.async_set_display_timeout(0x1E)
    assert coordinator.display_timeout == 0x1E


async def test_set_input_detection(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    """Test setting input detection updates assumed state."""
    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=1)
    client.set_input_detection = AsyncMock()

    coordinator = TesmartKvmCoordinator(hass, mock_entry, client)
    await coordinator.async_refresh()

    assert coordinator.input_detection_enabled is None
    await coordinator.async_set_input_detection(True)
    assert coordinator.input_detection_enabled is True
