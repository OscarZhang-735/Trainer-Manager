import json
import requests
from urllib.request import urlretrieve
import zipfile
import rarfile
from urllib.parse import quote
import os


class Data:
    @staticmethod
    def json_read(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    @staticmethod
    def json_write(path, data):
        with open(path, "w") as f:
            json.dump(data, f)


class Download:
    @staticmethod
    def download_file(url, file_name):
        urlretrieve(url.replace(" ", "%20"), file_name)

    @staticmethod
    def extract_file(file_name):
        downloaded = Data.json_read("data\\data.json")["files"]["downloaded"]
        if ".zip" in file_name:
            zipFile = zipfile.ZipFile(file_name, "r")
            for file in zipFile.namelist():
                if ".exe" in file:
                    zipFile.extract(file, Data.json_read("data\\data.json")["config"]["download"]["path"])
                    downloaded.append([])
            zipFile.close()
        elif ".rar" in file_name:
            rarFile = rarfile.RarFile(file_name, "r")
            for file in rarFile.namelist():
                print(file)
                if ".exe" in file:
                    try:
                        rarFile.extract(file, Data.json_read("data\\data.json")["config"]["download"]["path"])
                    except rarfile.RarCannotExec:
                        return -1
            rarFile.close()

        return 0


class File:
    @staticmethod
    def list_files(path):
        files = os.listdir(path)
        downloaded = Data.json_read("data\\data.json")["files"]["downloaded"]
        print(files)
        print(downloaded)
