"""Offline regression checks; no GUI, network, or real file writes."""

import io
import json
import unittest
from unittest.mock import mock_open, patch

from trainer_manager.services.data import Data
from trainer_manager.services.files import File


class DataTests(unittest.TestCase):
    def test_reads_existing_trainer_records_without_conversion(self):
        payload = {"files": {"trainers": [["Game", "game.exe", "REGISTERED"]]}}
        with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
            self.assertEqual(Data.json_read("data/data.json"), payload)

    def test_writes_unicode_and_nested_records(self):
        payload = {"games": [["游戏", "D:\\Games\\game.exe"]], "enabled": True}
        output = io.StringIO()
        with patch("builtins.open") as opened:
            opened.return_value.__enter__.return_value = output
            Data.json_write("data/data.json", payload)
        self.assertEqual(json.loads(output.getvalue()), payload)

    def test_invalid_json_still_raises(self):
        with patch("builtins.open", mock_open(read_data="not json")):
            with self.assertRaises(json.JSONDecodeError):
                Data.json_read("data/data.json")

    def test_legacy_unquoted_keys(self):
        self.assertEqual(json.loads(Data.json_convert('{name: "Game", count: 2}')),
                         {"name": "Game", "count": 2})


class FileTests(unittest.TestCase):
    def test_reserved_filename_characters_become_spaces(self):
        self.assertEqual(File.string_valid('a\\/:*?"<>|b'), "a         b")

    def test_valid_unicode_filename_is_unchanged(self):
        self.assertEqual(File.string_valid("游戏 - Game (2024).exe"),
                         "游戏 - Game (2024).exe")


if __name__ == "__main__":
    unittest.main()
