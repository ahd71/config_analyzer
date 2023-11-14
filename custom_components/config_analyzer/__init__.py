"""config_analyzer"""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN

import os
import datetime

import json
import yaml

import importlib
from .sensor import LastAnalyzed

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, (Platform.SENSOR,))


# Load all plugins  from the specified folder
async def load_plugins(hass: HomeAssistant):
    plugin_folder = hass.config.path() + "/custom_components/" + DOMAIN + "/plugins"
    plugins = []
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            plugin_file = os.path.splitext(filename)[0]
            plugin_module = importlib.import_module(
                f"custom_components.config_analyzer.plugins.{plugin_file}"
            )
            importlib.reload(
                plugin_module
            )  # in case it has been updated since previous run (no in-between restart of Home Assistant when developing in production ;-)

            plugins.append(plugin_module)
    return plugins


# Execute a function from a loaded plugin
async def execute_plugin_function(plugin, function_name, *args, **kwargs):
    if hasattr(plugin, function_name) and callable(getattr(plugin, function_name)):
        function = getattr(plugin, function_name)
        return await function(*args, **kwargs)
    else:
        return None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the the async service."""

    @callback
    async def config_analyzer(call: ServiceCall) -> None:
        """My first service."""
        arg1 = call.data.get("arg1", "default_value")

        _LOGGER.debug(f"Invoked with {call.data}")

        results = []
        hass.states.async_set(
            "sensor.last_analyzed", "Started"
        )  # TODO: How can I avoid hard coded entity name?; and how can i get it with the correct time zone

        loaded_plugins = await load_plugins(hass)
        for plugin in loaded_plugins:
            p = plugin.PluginClass()

            plugin_name = plugin  # plugin.split("'")[1]
            plugin_friendly_name = p.get_name()
            plugin_release = p.get_release()

            _LOGGER.debug(
                f"Running Plugin '{plugin_friendly_name} v{plugin_release}'"
            )  # TODO: I would like to show the file name of the plugin too in case there is a copy/paste issue with the plugins configuration, but where filename always would be unique
            result = await p.execute(hass, arg1)
            results.append({plugin_friendly_name: result})
            _LOGGER.debug(result)

        hass.states.async_set(
            "sensor.last_analyzed",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            {"results": results},
        )  # TODO: How can I get it with the user's correct time zone?

        _LOGGER.debug(result)

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "run", config_analyzer)

    # Register the sensor with Home Assistant
    # TODO: Haven't figured out how to do that, but once setting a state the sensor works but have no internal ID

    # Return boolean to indicate that initialization was successfully.
    return True
