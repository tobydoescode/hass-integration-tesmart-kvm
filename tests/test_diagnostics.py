"""Tests for TESmart KVM diagnostics."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN
from custom_components.tesmart_kvm.coordinator import TesmartKvmCoordinator
from custom_components.tesmart_kvm.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics(hass: HomeAssistant) -> None:
    """Test diagnostics returns expected structure."""
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

    client = AsyncMock()
    client.connected = True
    client.get_active_input = AsyncMock(return_value=3)

    coordinator = TesmartKvmCoordinator(hass, entry, client)
    await coordinator.async_refresh()

    # Set some assumed state
    coordinator.buzzer_enabled = True
    coordinator.display_timeout = 0x1E
    coordinator.input_detection_enabled = False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result == {
        "config": {
            "host": "192.168.1.10",
            "port": 5000,
            "model": "HKS801-EB23",
        },
        "connection": {
            "connected": True,
        },
        "state": {
            "active_input": 3,
            "buzzer_enabled": True,
            "display_timeout": 0x1E,
            "input_detection_enabled": False,
        },
    }
