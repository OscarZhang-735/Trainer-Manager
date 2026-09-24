"""Data helpers, extracted without changing behavior."""

import json
import re


class Data:
    def __init__(self):

        self.init_json = {
            "config": {
                "download": {
                    "path": ".\\trainers\\",
                    "extract": True
                },
                "cache": {
                    "detail_image": True
                },
                "resources": {
                    "detail_img": ".\\resource\\img_cache\\image.jpg",
                    "blank_img": ".\\resource\\original\\blank.png",
                    "avatar_img": ".\\resource\\icons\\avatar.png",
                    "cover_folder": ".\\resource\\game_covers"
                },
                "library": {
                    "filter": "REGISTERED_ONLY"
                },
                "save_backup": {
                    "max_number": 10,
                    "auto_clean": False
                },
                "program": {
                    "username": "Rinne",
                    "user_avatar": "resource/icons/avatar.png",
                    "icon": "resource/icons/icon3.png",
                    "title": "TrainerManager",
                    "connection_allow": True
                }
            },
            "files": {
                "save_file": [],
                "downloaded": [],
                "game_cats": [
                    "ALL",
                    "UNCATEGORIZED",
                ],
                "games": []
            }
        }

    @staticmethod
    def json_read(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    @staticmethod
    def json_write(path, data):
        with open(path, "w") as f:
            json.dump(data, f)

    @staticmethod
    def json_convert(json_string):
        pattern = r'(?<!")(\b\w+\b)(?!")\s*:'

        def add_quotes(match):
            return f'"{match.group(1)}":'

        return re.sub(pattern, add_quotes, json_string)
