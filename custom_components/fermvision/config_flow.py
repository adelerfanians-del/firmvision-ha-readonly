from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FermvisionApi, FermvisionApiError
from .const import CONF_PORT, DEFAULT_PORT, DOMAIN


class FermvisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            api = FermvisionApi(
                async_get_clientsession(self.hass),
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_PASSWORD],
            )
            try:
                await api.read("get.device.qrcode")
            except FermvisionApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Fermvision {user_input[CONF_HOST]}",
                    data=user_input,
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PASSWORD): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
