from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from typing import Any


def encode_password(password: str) -> str:
    if len(password) >= 64:
        return password
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_read_request(command: str, password: str) -> str:
    if command not in {"get.device.qrcode", "get.device.attachInfo"}:
        raise ValueError("only read-only commands are permitted")
    encoded = encode_password(password)
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<envelope><header>"
        f"<password>{encoded}</password><passwordencode>1</passwordencode>"
        "<security>username</security><username>adminapp2</username>"
        "</header><body>"
        f"<command>{command}</command><content></content>"
        "</body></envelope>"
    )


def parse_response(xml_text: str) -> dict[str, Any]:
    clean = xml_text.strip()
    if "<envelope" in clean:
        clean = clean[clean.index("<envelope") :]
    try:
        root = ET.fromstring(clean)
    except ET.ParseError as error:
        raise ValueError(f"invalid Fermvision XML response: {error}") from error
    if root.tag != "envelope":
        raise ValueError("unexpected Fermvision response root")
    command = root.findtext(".//command")
    content_node = root.find(".//content")
    content = ""
    if content_node is not None:
        content = content_node.text or ""
        if not content.strip():
            content = "".join(ET.tostring(child, encoding="unicode") for child in content_node)
    error_text = root.findtext(".//error")
    error_code: int | None = None
    if error_text and error_text.strip().lstrip("-").isdigit():
        error_code = int(error_text.strip())
    json_data = None
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            json_data = json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    if error_code is None and isinstance(json_data, dict):
        value = json_data.get("error")
        if isinstance(value, int) and not isinstance(value, bool):
            error_code = value
    return {
        "command": command.strip() if command else None,
        "error": error_code,
        "success": error_code == 0,
        "content": content,
        "json": json_data,
    }
