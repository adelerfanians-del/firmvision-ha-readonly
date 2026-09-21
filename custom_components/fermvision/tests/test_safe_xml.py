from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safe_xml import build_read_request, parse_response  # noqa: E402


class SafeXmlTests(unittest.TestCase):
    def test_only_read_commands_can_be_built(self):
        with self.assertRaises(ValueError):
            build_read_request("set.device.opendoor", "synthetic")

    def test_error_response_is_not_success(self):
        parsed = parse_response(
            "<envelope><body><command>get.device.qrcode</command>"
            "<content><error>401</error></content></body></envelope>"
        )
        self.assertFalse(parsed["success"])
        self.assertEqual(parsed["error"], 401)

    def test_nested_content_is_preserved_for_read_only_status(self):
        parsed = parse_response(
            "<envelope><body><command>get.device.attachInfo</command>"
            "<content><channel-num>2</channel-num><error>0</error></content>"
            "</body></envelope>"
        )
        self.assertTrue(parsed["success"])
        self.assertIn("<channel-num>2</channel-num>", parsed["content"])


if __name__ == "__main__":
    unittest.main()
