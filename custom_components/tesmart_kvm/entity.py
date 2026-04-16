"""Base entity for the TESmart KVM integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TesmartKvmCoordinator


class TesmartKvmEntity(CoordinatorEntity[TesmartKvmCoordinator]):
    """Base class for TESmart KVM entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name=f"TESmart {self.coordinator.model_info.name}",
            manufacturer="TESmart",
            model=self.coordinator.model_info.name,
        )
