"""The TESmart KVM integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .client import TesmartClient
from .const import DOMAIN
from .coordinator import TesmartKvmCoordinator

PLATFORMS = [Platform.SELECT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TESmart KVM from a config entry."""
    client = TesmartClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = TesmartKvmCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.disconnect()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: TesmartKvmCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.disconnect()
    return unload_ok
