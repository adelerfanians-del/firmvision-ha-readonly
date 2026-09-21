from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FermvisionApi
from .const import CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import FermvisionCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = FermvisionApi(
        async_get_clientsession(hass),
        entry.data["host"],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data["password"],
    )
    coordinator = FermvisionCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "binary_sensor", "camera"]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor", "camera"]
    )
    if unload:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload
