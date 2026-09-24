"""ui.common: extracted application components."""

import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel


class Error:
    class FileError:
        @staticmethod
        def ExtractionError():
            pass


class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        print("Working:", self.command)

    def run(self):
        subprocess.run(self.command,
                       creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP, close_fds=True)
        self.finished.emit()


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        # leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)
