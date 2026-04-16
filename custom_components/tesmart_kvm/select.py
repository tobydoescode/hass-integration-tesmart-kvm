"""Select platform for the TESmart KVM integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DISPLAY_TIMEOUT_OPTIONS, DOMAIN
from .coordinator import TesmartKvmCoordinator
from .entity import TesmartKvmEntity

TIMEOUT_VALUE_TO_LABEL = DISPLAY_TIMEOUT_OPTIONS
TIMEOUT_LABEL_TO_VALUE = {v: k for k, v in DISPLAY_TIMEOUT_OPTIONS.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TESmart KVM select entities from a config entry."""
    coordinator: TesmartKvmCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            TesmartActiveInputSelect(coordinator),
            TesmartDisplayTimeoutSelect(coordinator),
        ]
    )


class TesmartActiveInputSelect(TesmartKvmEntity, SelectEntity):
    """Select entity for the active input port."""

    _attr_translation_key = "active_input"
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_active_input"
        self._attr_options = [str(i) for i in range(1, coordinator.model_info.port_count + 1)]

    @property
    def current_option(self) -> str | None:
        """Return the currently active input."""
        if self.coordinator.data is None:
            return None
        return str(self.coordinator.data["active_input"])

    async def async_select_option(self, option: str) -> None:
        """Switch to the selected input port."""
        await self.coordinator.async_set_active_input(int(option))


class TesmartDisplayTimeoutSelect(TesmartKvmEntity, SelectEntity):
    """Select entity for the display timeout."""

    _attr_translation_key = "display_timeout"
    _attr_icon = "mdi:monitor-shimmer"

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_display_timeout"
        self._attr_options = list(TIMEOUT_VALUE_TO_LABEL.values())

    @property
    def current_option(self) -> str | None:
        """Return the current display timeout."""
        if self.coordinator.display_timeout is None:
            return None
        return TIMEOUT_VALUE_TO_LABEL.get(self.coordinator.display_timeout)

    async def async_select_option(self, option: str) -> None:
        """Set the display timeout."""
        value = TIMEOUT_LABEL_TO_VALUE[option]
        await self.coordinator.async_set_display_timeout(value)
