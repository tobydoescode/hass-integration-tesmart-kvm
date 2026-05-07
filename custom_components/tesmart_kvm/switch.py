"""Switch platform for the TESmart KVM integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from propcache.api import cached_property

from .const import DOMAIN
from .coordinator import TesmartKvmCoordinator
from .entity import TesmartKvmEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TESmart KVM switch entities from a config entry."""
    coordinator: TesmartKvmCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            TesmartBuzzerSwitch(coordinator),
            TesmartInputDetectionSwitch(coordinator),
        ]
    )


class TesmartBuzzerSwitch(TesmartKvmEntity, SwitchEntity):  # type: ignore[reportIncompatibleVariableOverride]
    """Switch entity for the buzzer."""

    _attr_translation_key = "buzzer"
    _attr_icon = "mdi:volume-high"
    _cached_property_keys = {"is_on"}

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_buzzer"

    @cached_property
    def is_on(self) -> bool | None:
        """Return True if the buzzer is enabled."""
        return self.coordinator.buzzer_enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the buzzer."""
        await self.coordinator.async_set_buzzer(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the buzzer."""
        await self.coordinator.async_set_buzzer(False)


class TesmartInputDetectionSwitch(TesmartKvmEntity, SwitchEntity):  # type: ignore[reportIncompatibleVariableOverride]
    """Switch entity for auto input detection."""

    _attr_translation_key = "input_detection"
    _attr_icon = "mdi:auto-fix"
    _cached_property_keys = {"is_on"}

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_input_detection"

    @cached_property
    def is_on(self) -> bool | None:
        """Return True if input detection is enabled."""
        return self.coordinator.input_detection_enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable input detection."""
        await self.coordinator.async_set_input_detection(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable input detection."""
        await self.coordinator.async_set_input_detection(False)
