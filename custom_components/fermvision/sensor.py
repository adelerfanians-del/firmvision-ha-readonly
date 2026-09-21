from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FermvisionCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FermvisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        FermvisionDeviceSensor(coordinator, entry),
        FermvisionChannelsSensor(coordinator, entry),
    ])


class FermvisionDeviceSensor(CoordinatorEntity[FermvisionCoordinator], SensorEntity):
    _attr_name = "Device information"
    _attr_icon = "mdi:doorbell-video"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_device_info"

    @property
    def native_value(self):
        data = self.coordinator.data["qrcode"].get("json") or {}
        return data.get("u") or "online"


class FermvisionChannelsSensor(CoordinatorEntity[FermvisionCoordinator], SensorEntity):
    _attr_name = "Configured channels"
    _attr_icon = "mdi:connection"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_channels"

    @property
    def native_value(self):
        content = self.coordinator.data["attach"].get("content", "")
        marker = "<channel-num>"
        if marker not in content:
            return None
        return content.split(marker, 1)[1].split("</channel-num>", 1)[0]
