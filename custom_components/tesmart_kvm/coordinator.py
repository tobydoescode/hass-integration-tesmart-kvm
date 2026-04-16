"""DataUpdateCoordinator for the TESmart KVM integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import TesmartClient, TesmartError
from .const import CONF_MODEL, DEFAULT_SCAN_INTERVAL, DOMAIN, MODELS

_LOGGER = logging.getLogger(__name__)

type CoordinatorData = dict[str, Any]


class TesmartKvmCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinator to poll TESmart KVM state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: TesmartClient,
    ) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.client = client

        model_id = entry.data[CONF_MODEL]
        self.model_info = MODELS[model_id]

        # Assumed state for write-only settings (None = unknown)
        self.buzzer_enabled: bool | None = None
        self.display_timeout: int | None = None
        self.input_detection_enabled: bool | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )

    async def _async_update_data(self) -> CoordinatorData:
        """Fetch the current active input from the device."""
        try:
            if not self.client.connected:
                await self.client.connect()
            active_input = await self.client.get_active_input()
        except TesmartError as err:
            raise UpdateFailed(f"Error communicating with TESmart KVM: {err}") from err

        return {"active_input": active_input}

    async def async_set_active_input(self, port: int) -> None:
        """Switch to the specified input port."""
        try:
            await self.client.set_active_input(port)
        except TesmartError as err:
            raise UpdateFailed(f"Error switching input: {err}") from err
        await self.async_request_refresh()

    async def async_set_buzzer(self, enabled: bool) -> None:
        """Enable or disable the buzzer."""
        try:
            await self.client.set_buzzer(enabled)
        except TesmartError as err:
            raise UpdateFailed(f"Error setting buzzer: {err}") from err
        self.buzzer_enabled = enabled
        self.async_update_listeners()

    async def async_set_display_timeout(self, value: int) -> None:
        """Set the display timeout."""
        try:
            await self.client.set_display_timeout(value)
        except TesmartError as err:
            raise UpdateFailed(f"Error setting display timeout: {err}") from err
        self.display_timeout = value
        self.async_update_listeners()

    async def async_set_input_detection(self, enabled: bool) -> None:
        """Enable or disable auto input detection."""
        try:
            await self.client.set_input_detection(enabled)
        except TesmartError as err:
            raise UpdateFailed(f"Error setting input detection: {err}") from err
        self.input_detection_enabled = enabled
        self.async_update_listeners()
