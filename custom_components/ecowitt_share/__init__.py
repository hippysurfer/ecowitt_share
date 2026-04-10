"""Ecowitt Share integration for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_AUTHORIZE
from .coordinator import EcowittShareCoordinator, async_get_device_id
import aiohttp

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ecowitt Share from a config entry."""
    authorize = entry.data[CONF_AUTHORIZE]
    device_id = entry.data["device_id"]
    station_name = entry.data.get("station_name", "Ecowitt Station")

    coordinator = EcowittShareCoordinator(
        hass,
        authorize=authorize,
        device_id=device_id,
        station_name=station_name,
    )

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
