# coding:utf-8
import json
import requests
from urllib.request import urlretrieve
import zipfile
import rarfile
from PyQt5.QtGui import QFont
import os
import re

from PyQt5.QtWidgets import QMessageBox


# rarfile.RarFile.UNRAR_TOOL = r'D:\WinRAR\UnRAR.exe'
PROGRAM_NAME = "Rinne Toolkit"

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


class Download:
    @staticmethod
    def download_file(url, file_name):
        urlretrieve(url.replace(" ", "%20"), file_name)

    @staticmethod
    def extract_file(file_name):
        downloaded = Data.json_read("data/data.json")["files"]["trainers"]
        extracted_file = None
        if ".zip" in file_name:
            zipFile = zipfile.ZipFile(file_name, "r")
            for file in zipFile.namelist():
                if ".exe" in file:
                    zipFile.extract(file, Data.json_read("data/data.json")["config"]["download"]["trainer"])
                    downloaded.append([])
                    extracted_file = file
                    break
            zipFile.close()
        elif ".rar" in file_name:
            rarFile = rarfile.RarFile(file_name, "r")
            for file in rarFile.namelist():
                print(file)
                if ".exe" in file:
                    try:
                        rarFile.extract(file, Data.json_read("data/data.json")["config"]["download"]["trainer"])
                        extracted_file = file
                    except rarfile.RarCannotExec:
                        return -1
            rarFile.close()
        return extracted_file


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


class Help:
    @staticmethod
    def anonymous_report(title, content, time):
        # Temporally abandoned
        api_url = "https://api.guerrillamail.com/ajax.php"
        receiver = "2778940377@qq.com"
        params = {
            "f": "send",
            "body": f"Report Time: {time}\nIssue Description:\n{content}",
            "to": receiver,
            "subject": title,
            "from": "noreply@guerrillamail.com"
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            print("Report successfully")
        else:
            print(f"Failed to report. Status code: {response.status_code}")

    @staticmethod
    def report(title, content, time):
        # Temporally abandoned
        pass

    @staticmethod
    def warning(title, content, terminate=False):
        QMessageBox.warning(None, title, content, QMessageBox.Yes)
        if terminate:
            exit(1)

    @staticmethod
    def info(title, content):
        QMessageBox.about(None, title, content)


class Font:
    def __init__(self):
        self.STANDARD_FONT = QFont()
        self.STANDARD_FONT.setFamily("Segoe UI")
        self.STANDARD_FONT.setPointSize(10)
        self.STANDARD_MIDDLE_FONT = QFont()
        self.STANDARD_MIDDLE_FONT.setFamily("Segoe UI")
        self.STANDARD_MIDDLE_FONT.setPointSize(12)
        self.STANDARD_HUGE_FONT = QFont()
        self.STANDARD_HUGE_FONT.setFamily("Segoe UI")
        self.STANDARD_HUGE_FONT.setPointSize(18)
