"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# TODO: The setup of the sensor is still unclear how it should work
# async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
#     """Set up entry."""
#     async_add_entities(
#         [LastAnalyzed()], "sensor.last_analyzed", "async_setup_entry"
#     )  # TODO: Verify if this works


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    add_entities([LastAnalyzed()])  # TODO: Unclear how and if this works


class LastAnalyzed(SensorEntity):
    """Completion time of last analyzis"""

    _attr_name = "Last Analyzed"
    _attr_icon = "mdi:shield-half-full"
    _attr_should_poll = False

    def __init__(self, name, state) -> None:
        self._name = name
        self._state = state

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._attr_native_value

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
