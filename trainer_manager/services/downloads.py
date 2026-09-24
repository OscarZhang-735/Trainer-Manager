"""Download helpers, extracted without changing behavior."""

from urllib.request import urlretrieve
import zipfile
import rarfile
from trainer_manager.services.data import Data


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
