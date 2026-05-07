"""Base entity for the TESmart KVM integration."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TesmartKvmCoordinator


class TesmartKvmEntity(CoordinatorEntity[TesmartKvmCoordinator]):
    """Base class for TESmart KVM entities."""

    _attr_has_entity_name = True

    # Cached property keys to invalidate on coordinator updates.
    _cached_property_keys: set[str] = set()

    def __init__(self, coordinator: TesmartKvmCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Invalidate cached properties and notify HA of update."""
        instance_dict: dict[str, object] = self.__dict__  # type: ignore[assignment]
        for key in self._cached_property_keys:
            instance_dict.pop(key, None)
        super()._handle_coordinator_update()

    @property
    def device_info(self) -> DeviceInfo:  # type: ignore[reportIncompatibleVariableOverride]
        """Return device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.coordinator.entry.unique_id or self.coordinator.entry.entry_id)
            },
            name=f"TESmart {self.coordinator.model_info.name}",
            manufacturer="TESmart",
            model=self.coordinator.model_info.name,
        )
