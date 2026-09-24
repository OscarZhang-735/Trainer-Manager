"""Help helpers, extracted without changing behavior."""

import requests
from PyQt5.QtWidgets import QMessageBox


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
