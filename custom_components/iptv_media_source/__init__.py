"""The IPTV Media Source integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    # This component does not need to do anything specific on setup,
    # as the config flow will handle the configuration.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IPTV Media Source from a config entry."""
    # Forward the setup to the media_source platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "media_source")
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unload to the media_source platform.
    return await hass.config_entries.async_forward_entry_unload(entry, "media_source")
