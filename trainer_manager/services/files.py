"""File helpers, extracted without changing behavior."""

import os
from trainer_manager.services.data import Data


class File:
    @staticmethod
    def list_files(path):
        files = os.listdir(path)
        downloaded = Data.json_read("data/data.json")["files"]["trainers"]
        print(files)
        print(downloaded)

    @staticmethod
    def string_valid(string):
        invalid = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
        for char in string:
            if char in invalid:
                string = string.replace(char, " ")
        return string
