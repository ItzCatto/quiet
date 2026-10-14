"""The weekly AdGuard DNS check builds a correct query and reads replies correctly. No network is used."""

import importlib.util
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("check_resolvers", ROOT / "scripts" / "check_resolvers.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


class ResolverCheckTests(unittest.TestCase):
    def test_query_asks_for_the_ipv4_address_of_a_name(self):
        query = check.query("example.com")
        # 12-byte header, then the name as labels, then type A (1) and class IN (1)
        self.assertEqual(query[12:], b"\x07example\x03com\x00\x00\x01\x00\x01")

    def test_query_asks_for_recursion(self):
        flags = struct.unpack(">H", check.query("example.com")[2:4])[0]
        self.assertTrue(flags & 0x0100)

    def test_reply_with_an_answer_passes(self):
        reply = struct.pack(">HHHHHH", 0, 0x8180, 1, 1, 0, 0) + b"\x00" * 16
        self.assertIsNone(check.check_reply(reply))

    def test_error_reply_fails_with_its_code(self):
        reply = struct.pack(">HHHHHH", 0, 0x8183, 1, 0, 0, 0)  # RCODE 3 (name does not exist)
        self.assertEqual(check.check_reply(reply), "error code 3")

    def test_reply_without_an_answer_fails(self):
        reply = struct.pack(">HHHHHH", 0, 0x8180, 1, 0, 0, 0)
        self.assertEqual(check.check_reply(reply), "no answer")

    def test_a_question_is_not_taken_for_a_reply(self):
        question = struct.pack(">HHHHHH", 0, 0x0100, 1, 0, 0, 0)
        self.assertEqual(check.check_reply(question), "not a reply")

    def test_a_short_reply_fails(self):
        self.assertEqual(check.check_reply(b"\x00\x01"), "reply too short")


if __name__ == "__main__":
    unittest.main()
