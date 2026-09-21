from __future__ import annotations

import re
from urllib.parse import urlparse

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FermvisionCoordinator


def _reported_rtsp_url(content: str, host: str) -> str | None:
    """Extract a firmware-reported RTSP URL without inventing one."""
    match = re.search(
        r"(?:rtspurl|rtsp-url)\s*[=:>\"]+\s*(rtsp://[^\s<\"]+)",
        content,
        re.I,
    )
    if match:
        return match.group(1).rstrip("/&")
    port = re.search(r"(?:rtspport|rtsp-port)\s*[=:>\"]+\s*(\d{2,5})", content, re.I)
    if port:
        return f"rtsp://{host}:{port.group(1)}"
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FermvisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    content = coordinator.data.get("network", {}).get("content", "")
    url = _reported_rtsp_url(content, entry.data["host"])
    if url:
        async_add_entities([FermvisionCamera(coordinator, entry, url)])


class FermvisionCamera(CoordinatorEntity[FermvisionCoordinator], Camera):
    _attr_name = "Fermvision camera"
    _attr_icon = "mdi:camera-wireless"

    def __init__(self, coordinator: FermvisionCoordinator, entry: ConfigEntry, url: str) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry.entry_id}_camera"
        self._url = url

    @property
    def stream_source(self) -> str:
        return self._url

    @property
    def extra_state_attributes(self):
        parsed = urlparse(self._url)
        return {"stream_host": parsed.hostname, "stream_port": parsed.port}
