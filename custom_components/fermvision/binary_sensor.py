from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
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
    async_add_entities([FermvisionReachable(coordinator, entry)])


class FermvisionReachable(CoordinatorEntity[FermvisionCoordinator], BinarySensorEntity):
    _attr_name = "LAN reachable"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_reachable"

    @property
    def is_on(self):
        return self.coordinator.last_update_success
