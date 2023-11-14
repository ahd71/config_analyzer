from homeassistant.core import HomeAssistant, ServiceCall, callback

import logging
import asyncio

from homeassistant.helpers import (
    config_validation as cv,
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

_LOGGER = logging.getLogger(__name__)

class PluginClass:
    def get_name(self):
        return "Hello World"

    def get_release(self):
        return "0.1"

    async def execute(self, hass: HomeAssistant, argument1):
        return "Successful"
