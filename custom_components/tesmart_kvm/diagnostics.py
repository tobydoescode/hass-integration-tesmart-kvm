"""Diagnostics support for the TESmart KVM integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import TesmartKvmCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: TesmartKvmCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "config": {
            "host": entry.data.get(CONF_HOST),
            "port": entry.data.get(CONF_PORT),
            "model": entry.data.get("model"),
        },
        "connection": {
            "connected": coordinator.client.connected,
        },
        "state": {
            "active_input": (coordinator.data.get("active_input") if coordinator.data else None),
            "buzzer_enabled": coordinator.buzzer_enabled,
            "display_timeout": coordinator.display_timeout,
            "input_detection_enabled": coordinator.input_detection_enabled,
        },
    }
