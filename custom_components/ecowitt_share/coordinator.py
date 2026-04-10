"""DataUpdateCoordinator for Ecowitt Share integration."""

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_LIST_URL,
    DEVICE_DATA_URL,
)

_LOGGER = logging.getLogger(__name__)

MPH_TO_MS = 0.44704


async def async_validate_authorize(authorize: str) -> dict[str, Any]:
    """Validate the authorize code and return device info. Used by config flow."""
    async with aiohttp.ClientSession() as session:
        url = f"{DEVICE_LIST_URL}?authorize={authorize}"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    if data.get("errcode") != "0":
        raise ValueError(data.get("errmsg", "Unknown error"))

    devices = data.get("list", [])
    if not devices:
        raise ValueError("No devices found for this authorize code.")

    return devices[0]  # {"device_id": ..., "name": ..., "type": ...}


def _get_nested(data: dict, path: str) -> Any:
    """Traverse a dot-separated path in a nested dict. Returns None if any key is missing."""
    current = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _apply_transform(raw: Any, transform: str | None) -> float | None:
    """Convert a raw string value to float, applying an optional transform."""
    if raw is None:
        return None
    try:
        if transform == "strip_commas":
            value = float(str(raw).replace(",", ""))
        elif transform == "mph_to_ms":
            value = round(float(raw) * MPH_TO_MS, 2)
        else:
            value = float(raw)
        return value
    except (ValueError, TypeError):
        # Non-numeric value (e.g. winddir.direction = "ESE") — return as-is
        return raw


class EcowittShareCoordinator(DataUpdateCoordinator):
    """Coordinator that polls the Ecowitt share endpoint every minute."""

    def __init__(
        self,
        hass: HomeAssistant,
        authorize: str,
        device_id: str,
        station_name: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.authorize = authorize
        self.device_id = device_id
        self.station_name = station_name
        self._first_fetch = True

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch live data from the Ecowitt share endpoint."""
        url = (
            f"{DEVICE_DATA_URL}"
            f"?device_id={self.device_id}"
            f"&authorize={self.authorize}"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    resp.raise_for_status()
                    raw = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Ecowitt: {err}") from err

        # Log full response on first successful fetch to aid debugging
        if self._first_fetch:
            _LOGGER.info(
                "Ecowitt first-fetch raw response for '%s': %s",
                self.station_name,
                raw,
            )
            self._first_fetch = False
        else:
            _LOGGER.debug("Ecowitt raw response: %s", raw)

        if raw.get("errcode") != "0":
            raise UpdateFailed(
                f"Ecowitt API error: {raw.get('errmsg', 'unknown')}"
            )

        # Unwrap the "data" envelope
        data = raw.get("data")
        if not isinstance(data, dict) or not data:
            raise UpdateFailed(
                "Ecowitt returned an empty or unexpected data payload. "
                "Enable debug logging to inspect the raw response."
            )

        return data

    def get_value(self, path: str, transform: str | None) -> Any:
        """Return a sensor value by dot-path, with optional transform applied."""
        if self.data is None:
            return None
        raw = _get_nested(self.data, path)
        return _apply_transform(raw, transform)
