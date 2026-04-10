"""Sensor platform for Ecowitt Share integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DESCRIPTIONS
from .coordinator import EcowittShareCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt Share sensors from a config entry."""
    coordinator: EcowittShareCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        EcowittSensor(coordinator, entry, *desc)
        for desc in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class EcowittSensor(CoordinatorEntity, SensorEntity):
    """A single sensor reading from an Ecowitt shared station."""

    def __init__(
        self,
        coordinator: EcowittShareCoordinator,
        entry: ConfigEntry,
        json_path: str,
        friendly_name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str | None,
        transform: str | None,
    ) -> None:
        super().__init__(coordinator)
        self._json_path = json_path
        self._transform = transform
        self._attr_name = f"{coordinator.station_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_{json_path.replace('.', '_')}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        if icon:
            self._attr_icon = icon

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["device_id"])},
            name=coordinator.station_name,
            manufacturer="Ecowitt",
            model="Weather Station (Public Share)",
            sw_version=None,  # populated from coordinator data if available
            configuration_url=(
                f"https://www.ecowitt.net/home/share"
                f"?authorize={entry.data['authorize']}"
            ),
        )

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        return self.coordinator.get_value(self._json_path, self._transform)

    @property
    def available(self) -> bool:
        """Mark sensor unavailable if coordinator failed or path doesn't exist in data."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.get_value(self._json_path, self._transform) is not None
        )
