"""Config flow for the TESmart KVM integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .client import TesmartClient
from .const import CONF_MODEL, DEFAULT_PORT, DOMAIN, MODELS

_LOGGER = logging.getLogger(__name__)

MODEL_OPTIONS = [{"value": key, "label": info.name} for key, info in MODELS.items()]

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODEL, default="HKS801-EB23"): SelectSelector(
            SelectSelectorConfig(options=MODEL_OPTIONS, mode=SelectSelectorMode.DROPDOWN)
        ),
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


class TesmartKvmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TESmart KVM."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            client = TesmartClient(host, port)
            if not await client.test_connection():
                errors["base"] = "cannot_connect"
            else:
                unique_id = f"{host}:{port}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"TESmart {MODELS[user_input[CONF_MODEL]].name}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
