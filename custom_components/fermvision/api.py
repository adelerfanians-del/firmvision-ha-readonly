from __future__ import annotations

from typing import Any

import aiohttp

from .safe_xml import build_read_request, parse_response


class FermvisionApiError(Exception):
    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


class FermvisionApi:
    def __init__(self, session: aiohttp.ClientSession, host: str, port: int, password: str) -> None:
        self._session = session
        self._url = f"http://{host}:{port}/tdkcgi"
        self._password = password

    async def read(self, command: str) -> dict[str, Any]:
        try:
            async with self._session.post(
                self._url,
                data=build_read_request(command, self._password),
                headers={"Content-Type": "application/xml"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                body = await response.text()
        except (aiohttp.ClientError, TimeoutError) as error:
            raise FermvisionApiError("Fermvision device is unreachable") from error
        if response.status >= 500:
            raise FermvisionApiError(f"Fermvision HTTP error {response.status}")
        try:
            result = parse_response(body)
        except ValueError as error:
            raise FermvisionApiError("Fermvision returned an invalid response") from error
        if result["error"] not in (None, 0):
            raise FermvisionApiError(
                f"Fermvision read rejected with error {result['error']}",
                result["error"],
            )
        return result

    async def read_all(self) -> dict[str, Any]:
        qrcode = await self.read("get.device.qrcode")
        try:
            attach = await self.read("get.device.attachInfo")
        except FermvisionApiError as error:
            # Some firmware rejects attachInfo while still supporting qrcode.
            # Keep the device online and expose channel count as unavailable.
            attach = {"error": error.code, "content": "", "unsupported": True}
        try:
            ability = await self.read("get.system.ability")
        except FermvisionApiError as error:
            ability = {"error": error.code, "content": "", "unsupported": True}
        try:
            network = await self.read("get.network.config")
        except FermvisionApiError as error:
            network = {"error": error.code, "content": "", "unsupported": True}
        return {"qrcode": qrcode, "attach": attach, "ability": ability, "network": network}
