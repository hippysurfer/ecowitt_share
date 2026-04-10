"""Config flow for Ecowitt Share integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_AUTHORIZE
from .coordinator import async_validate_authorize

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AUTHORIZE): str,
    }
)


class EcowittShareConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Ecowitt Share."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            authorize = user_input[CONF_AUTHORIZE].strip()

            try:
                device_info = await async_validate_authorize(authorize)
            except ValueError as err:
                _LOGGER.warning("Ecowitt authorize validation failed: %s", err)
                errors["base"] = "invalid_authorize"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Ecowitt authorize code")
                errors["base"] = "cannot_connect"
            else:
                # Use device_id as unique ID so the same station can't be added twice
                await self.async_set_unique_id(device_info["device_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=device_info.get("name", f"Ecowitt {authorize}"),
                    data={
                        CONF_AUTHORIZE: authorize,
                        "device_id": device_info["device_id"],
                        "station_name": device_info.get("name", "Ecowitt Station"),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "authorize_help": (
                    "Find your authorize code in the share URL on ecowitt.net: "
                    "https://www.ecowitt.net/home/share?authorize=XXXXXX"
                )
            },
        )
