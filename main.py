# coding:utf-8
import shutil
import subprocess
import sys
import os
import time
import atexit
import webbrowser
import keyboard

from PyQt5.QtCore import Qt, QRect, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices, QStandardItemModel, QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QVBoxLayout, QHeaderView, \
    QTableWidgetItem, QTableWidget, QFileDialog, QGridLayout

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, qrouter, ImageLabel, BodyLabel, PushButton,
                            TableWidget, LineEdit, PrimaryPushButton, HorizontalSeparator, VerticalSeparator,
                            MessageBoxBase, SubtitleLabel, TitleLabel, SwitchButton, ComboBox)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar

import crawler
import utils

print(os.getcwd())
Font = utils.Font()
PREP = utils.Data.json_read("data/data.json")
USER_NAME = PREP["config"]["program"]["username"]
USER_AVATAR = PREP["config"]["program"]["user_avatar"]
ICON = PREP["config"]["program"]["icon"]
TITLE = PREP["config"]["program"]["title"]
NET = PREP["config"]["program"]["connection_allow"]


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


class SearchWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.resize(400, 400)
        self.name = None
        self.row = None
        self.config = utils.Data.json_read("data/data.json")["config"]
        self.data = utils.Data.json_read("data/data.json")
        self.setObjectName("Search")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMiddle = QVBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.vBoxLayoutMiddle.setSpacing(10)

        self.titleLabel = TitleLabel("Search", self)
        self.titleLabel.setFixedHeight(40)
        self.searchLine = LineEdit(self)
        self.searchLine.setAlignment(Qt.AlignCenter)
        self.searchLine.setFixedWidth(300)
        self.searchLine.setPlaceholderText("Search on FLiNG Website")
        self.searchLine.setClearButtonEnabled(True)
        self.searchButton = PrimaryPushButton(self)
        self.searchButton.setIcon(FIF.SEARCH)
        self.searchButton.setText("Search")

        self.clearButton = PushButton(self)
        self.clearButton.setIcon(FIF.CLOSE)
        self.clearButton.setText("Clear")
        self.homepageButton = PushButton(self)
        self.homepageButton.setIcon(FIF.LINK)
        self.homepageButton.setText("Visit FLiNG Website")

        self.resultLabel = BodyLabel(self)
        self.resultLabel.setText("")

        self.exampleModel = QStandardItemModel(18, 3)
        self.resultTable = TableWidget(self)
        self.resultTable.setColumnCount(2)
        self.resultTable.horizontalHeader().setVisible(False)
        self.resultTable.verticalHeader().setVisible(False)
        self.resultTable.setEditTriggers(TableWidget.NoEditTriggers)
        self.resultTable.setShowGrid(False)

        self.separator_horiz_top = HorizontalSeparator(self)
        self.separator_vertical_middle = VerticalSeparator(self)

        self.waitingWidget = BodyLabel(self)
        self.waitingWidget.setText("Input keywords to search trainers online.")
        self.waitingWidget.setFont(Font.STANDARD_HUGE_FONT)
        self.waitingWidget.setAlignment(Qt.AlignCenter)
        self.noResultWidget = BodyLabel(self)
        self.noResultWidget.setText("Oops! No results found.")
        self.noResultWidget.setFont(Font.STANDARD_HUGE_FONT)
        self.noResultWidget.setAlignment(Qt.AlignCenter)
        self.detailImage = ImageLabel(self)
        self.detailLabel = BodyLabel(self)
        self.downloadButton = PrimaryPushButton("Download", self)
        self.downloadButton.setIcon(FIF.DOWNLOAD)
        self.visitPageButton = PushButton("Visit Website", self)
        self.visitPageButton.setIcon(FIF.LINK)

        self.hBoxLayoutTop.addWidget(self.searchLine, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.searchButton, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.resultLabel, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.homepageButton, 1, Qt.AlignRight)
        self.hBoxLayoutTop.addWidget(self.clearButton, 1, Qt.AlignRight)

        self.vBoxLayoutMiddle.addWidget(self.detailImage, 1)
        self.vBoxLayoutMiddle.addWidget(self.detailLabel, 1)
        self.vBoxLayoutMiddle.addWidget(self.downloadButton)
        self.vBoxLayoutMiddle.addWidget(self.visitPageButton)
        self.detailImage.setVisible(False)
        self.detailLabel.setVisible(False)
        self.downloadButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.detailLabel.setFixedWidth(250)
        self.detailLabel.setWordWrap(True)

        self.hBoxLayoutMiddle.addWidget(self.resultTable)
        self.hBoxLayoutMiddle.addWidget(self.separator_vertical_middle)
        self.hBoxLayoutMiddle.addLayout(self.vBoxLayoutMiddle)
        self.separator_vertical_middle.setVisible(False)

        self.vBoxLayoutMain.addWidget(self.titleLabel, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop, 1)
        self.vBoxLayoutMain.addWidget(self.separator_horiz_top)
        self.vBoxLayoutMain.addWidget(self.waitingWidget, 1)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle, 1)

        self.resultTable.setVisible(False)
        self.noResultWidget.setVisible(False)

        # keyboard.add_hotkey("enter", self.search)
        self.query_result = None
        self.detail_result = None
        self.searchButton.clicked.connect(self.search)
        self.homepageButton.clicked.connect(lambda: webbrowser.open("https://flingtrainer.com/"))
        self.clearButton.clicked.connect(self.clear)
        self.resultTable.cellClicked.connect(self.show_detail)
        self.downloadButton.clicked.connect(self.download_file)
        self.visitPageButton.clicked.connect(self.open_link)

        self.searchButton.setDisabled(True)
        self.searchLine.textChanged.connect(self.check_input)

    def check_input(self):
        if self.searchLine.text() == "" or type(self.searchLine.text()) is None:
            self.searchButton.setDisabled(True)
            print("Invalid input")
            return
        else:
            self.searchButton.setEnabled(True)

    def show_detail(self, row, col):
        self.row = row
        self.separator_vertical_middle.setVisible(True)
        self.detailLabel.setVisible(True)
        self.detailImage.setVisible(True)
        self.downloadButton.setVisible(True)
        self.visitPageButton.setVisible(True)
        self.visitPageButton.setDisabled(False)
        name = self.resultTable.item(row, 0).text()
        pic = QPixmap()
        if self.query_result[row][-1] == "COMMON":
            detailObj = crawler.Spider.Download(self.query_result[row][1])
            download_result = detailObj.run()
            self.detail_result = download_result[0]
            filename = self.config["resources"]["detail_img"]
            utils.Download.download_file(self.query_result[row][2], filename)
            pic.load(filename)
        else:
            self.detail_result = [name, self.query_result[row][1], "No Info",
                                  "No Info\n**This is an archived Trainer**", "Before 2019-05"]
            pic.load(self.config["resources"]["blank_img"])
            self.visitPageButton.setDisabled(True)
        content = f"Name: {name}\nLatest File: {self.detail_result[0]}\nSize: {self.detail_result[2]}\nDate: {self.detail_result[4]}\nDownloads: {self.detail_result[3]}"
        self.detailLabel.setText(content)
        self.detailLabel.setFont(Font.STANDARD_FONT)
        self.detailImage.setImage(pic)
        self.detailImage.setFixedSize(250, 250)
        self.check_download(name)
        self.resultTable.resizeColumnsToContents()

    def download_file(self):
        print("Downloading", self.detail_result[1])
        if ".rar" in self.detail_result[1]:
            file_name = self.config["download"]["trainer"] + self.detail_result[0] + ".rar"
        else:
            file_name = self.config["download"]["trainer"] + self.detail_result[0] + ".zip"
        print(file_name)
        utils.Download.download_file(self.detail_result[1], file_name)
        print("Download Completed.")
        # if self.config["download"]["extract"]:
        # Extract downloaded trainer
        flag = utils.Download.extract_file(file_name)
        if flag == -1:
            print("WinRAR is probably not installed or added to PATH, cannot proceed extraction.")
            os.remove(file_name)
            mb = MessageBox("Error",
                            "WinRAR is probably not installed or added to PATH, cannot proceed extraction.", self)
            mb.yesButton.setText("Download WinRAR")
            mb.cancelButton.setText("Cancel")
            if mb.exec():
                webbrowser.open("https://www.win-rar.com/download.html")
            return None
        else:
            print("Extraction Completed.")
            os.remove(file_name)

        self.register_download()

    def search(self):
        if not self.searchLine.text():
            return None
        if not NET:
            utils.Help.info("Info", "You have disabled connection for the program.")
            return None
        self.noResultWidget.setVisible(False)
        self.waitingWidget.setVisible(False)
        self.resultTable.setVisible(True)
        self.detailLabel.setVisible(False)
        self.detailImage.setVisible(False)
        self.downloadButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.separator_vertical_middle.setVisible(False)
        self.status("Establishing connection.")
        queryObj = crawler.Spider.Search(self.searchLine.text())
        archivedQueryObj = crawler.Spider.ArchivedDownload(self.searchLine.text())
        search_result = queryObj.run()
        archived_search_result = archivedQueryObj.run()
        self.status("Data received.")
        self.query_result = search_result
        for sub_archived_result in archived_search_result:
            self.query_result.append(sub_archived_result)
        count = len(search_result)
        self.resultTable.setRowCount(count)
        self.resultTable.clear()
        self.status("Loading Data.")
        if count == 0:
            self.noResultWidget.setVisible(True)
            return None
        for row in range(count):
            item = QTableWidgetItem()
            item.setText(search_result[row][0])
            item.setFont(Font.STANDARD_FONT)
            if search_result[row][-1] == "ARCHIVED":
                item.setForeground(QBrush(Qt.gray))
            self.resultTable.setItem(row, 0, item)
        self.status(f"{count} result(s) found.")
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def status(self, text):
        self.resultLabel.setText(text)
        print(text)

    def clear(self):
        self.noResultWidget.setVisible(False)
        self.waitingWidget.setVisible(True)
        self.resultTable.setVisible(False)
        self.detailImage.setVisible(False)
        self.detailLabel.setVisible(False)
        self.downloadButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.separator_vertical_middle.setVisible(False)
        self.resultTable.clear()
        self.resultTable.setRowCount(0)
        self.searchLine.setText("")
        self.resultLabel.setText("")
        self.resultLabel.setText("")
        self.query_result = None
        self.detail_result = None

    def open_link(self):
        link = self.query_result[self.row][1]
        webbrowser.open(link)

    def register_download(self):
        data = self.data
        name = self.detail_result[0]
        print("VRF: NAME:", name)
        for original_file in os.listdir(self.config["download"]["trainer"]):
            name = name.replace(".", "").replace("-FLiNG", "").replace(" ", "")
            file = original_file.replace(" ", "").replace(".", "")
            if name in file:
                self.downloadButton.setIcon(FIF.COMPLETED)
                self.downloadButton.setText("Downloaded")
                self.downloadButton.setDisabled(True)
                if self.config["cache"]["detail_image"]:
                    pic_name = self.data["config"]["resources"][
                                   "trainer_cover_folder"] + "\\" + utils.File.string_valid(
                        self.resultTable.item(self.row, 0).text()) + "-image.jpg"
                    if self.query_result[self.row][-1] == "COMMON":
                        register = [self.resultTable.item(self.row, 0).text(),
                                    data["config"]["download"]["trainer"] + original_file,
                                    time.strftime('%Y-%m-%d', time.localtime()), pic_name, "COMMON",
                                    self.query_result[self.row][1],
                                    "REGISTERED"]
                        try:
                            shutil.copyfile(self.data["config"]["resources"]["detail_img"], pic_name)
                        except FileExistsError:
                            pass
                    else:
                        register = [self.resultTable.item(self.row, 0).text(),
                                    data["config"]["download"]["trainer"] + original_file,
                                    time.strftime('%Y-%m-%d', time.localtime()), "NONE",
                                    "ARCHIVED", "NONE",
                                    "REGISTERED"]
                    data["files"]["trainers"].append(register)
                    print("Registered:", register)
                    utils.Data.json_write("data/data.json", data)
                return None
        self.downloadButton.setIcon(FIF.DOWNLOAD)
        self.downloadButton.setText("Download")
        self.downloadButton.setDisabled(False)

    def check_download(self, name):
        self.data = utils.Data.json_read("data/data.json")
        for downloaded in self.data["files"]["trainers"]:
            if name == downloaded[0]:
                self.downloadButton.setIcon(FIF.COMPLETED)
                self.downloadButton.setText("Downloaded")
                self.downloadButton.setDisabled(True)
                return True
        self.downloadButton.setIcon(FIF.DOWNLOAD)
        self.downloadButton.setText("Download")
        self.downloadButton.setDisabled(False)
        return False


# Library StackedWidget
class LibraryWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.resize(400, 400)
        self.file_name_list = None
        self.row = None
        self.current_exe = None
        self.data = utils.Data.json_read("data/data.json")
        self.setObjectName("Library")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMiddle = QVBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.vBoxLayoutMiddle.setSpacing(10)

        self.titleLabel = TitleLabel("Library", self)
        self.titleLabel.setFixedHeight(40)
        """
        self.searchLine = LineEdit(self)
        self.searchLine.setAlignment(Qt.AlignCenter)
        self.searchLine.setFixedWidth(300)
        self.searchLine.setPlaceholderText("Search in Local Library")
        self.searchLine.setClearButtonEnabled(True)
        self.searchButton = PrimaryPushButton(self)
        self.searchButton.setIcon(FIF.SEARCH)
        self.searchButton.setText("Search")
        """

        self.clearButton = PushButton(self)
        self.clearButton.setIcon(FIF.UPDATE)
        self.clearButton.setText("Refresh")
        self.folderButton = PushButton(self)
        self.folderButton.setIcon(FIF.FOLDER)
        self.folderButton.setText("Browse the Folder")

        self.resultLabel = BodyLabel(self)
        self.resultLabel.setText("")
        self.resultLabel.setFont(Font.STANDARD_MIDDLE_FONT)

        self.resultTable = TableWidget(self)
        self.resultTable.setColumnCount(2)
        self.resultTable.horizontalHeader().setVisible(False)
        self.resultTable.verticalHeader().setVisible(False)
        self.resultTable.setEditTriggers(TableWidget.NoEditTriggers)
        self.resultTable.setShowGrid(False)

        self.separator_horiz_top = HorizontalSeparator(self)
        self.separator_vertical_middle = VerticalSeparator(self)

        self.waitingWidget = BodyLabel(self)
        self.waitingWidget.setText("Input a keyword to search")
        self.waitingWidget.setFont(Font.STANDARD_HUGE_FONT)
        self.waitingWidget.setAlignment(Qt.AlignCenter)
        self.noResultWidget = BodyLabel(self)
        self.noResultWidget.setText("Oops! No results found.")
        self.noResultWidget.setFont(Font.STANDARD_HUGE_FONT)
        self.noResultWidget.setAlignment(Qt.AlignCenter)
        self.detailImage = ImageLabel(self)
        self.detailLabel = BodyLabel(self)
        self.runButton = PrimaryPushButton("Launch", self)
        self.runButton.setIcon(FIF.PLAY)
        self.visitPageButton = PushButton("Visit Website", self)
        self.visitPageButton.setIcon(FIF.LINK)
        self.deleteButton = PushButton("Delete", self)
        self.deleteButton.setIcon(FIF.CLOSE)
        self.updateButton = PushButton("Update", self)
        self.updateButton.setIcon(FIF.UP)

        # self.hBoxLayoutTop.addWidget(self.searchLine, 1, Qt.AlignLeft)
        # self.hBoxLayoutTop.addWidget(self.searchButton, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.resultLabel, 5, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.folderButton, 1, Qt.AlignRight)
        self.hBoxLayoutTop.addWidget(self.clearButton, 1, Qt.AlignRight)

        self.vBoxLayoutMiddle.addWidget(self.detailImage, 1)
        self.vBoxLayoutMiddle.addWidget(self.detailLabel, 1)
        self.vBoxLayoutMiddle.addWidget(self.runButton)
        self.vBoxLayoutMiddle.addWidget(self.visitPageButton)
        self.vBoxLayoutMiddle.addWidget(self.deleteButton)
        self.vBoxLayoutMiddle.addWidget(self.updateButton)
        self.detailImage.setVisible(False)
        self.detailLabel.setVisible(False)
        self.runButton.setVisible(False)
        self.deleteButton.setVisible(False)
        self.updateButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.detailLabel.setFixedWidth(250)
        self.detailLabel.setWordWrap(True)

        self.hBoxLayoutMiddle.addWidget(self.resultTable)
        self.hBoxLayoutMiddle.addWidget(self.separator_vertical_middle)
        self.hBoxLayoutMiddle.addLayout(self.vBoxLayoutMiddle)
        self.separator_vertical_middle.setVisible(False)

        self.vBoxLayoutMain.addWidget(self.titleLabel, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop, 1)
        self.vBoxLayoutMain.addWidget(self.separator_horiz_top)
        self.vBoxLayoutMain.addWidget(self.waitingWidget, 1)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle, 1)

        self.resultTable.cellClicked.connect(self.show_detail)
        self.resultTable.cellDoubleClicked.connect(self.run_trainer)
        self.folderButton.clicked.connect(self.open_folder)
        self.clearButton.clicked.connect(self.table_default)
        self.runButton.clicked.connect(self.run_trainer)
        self.deleteButton.clicked.connect(self.remove_file)
        self.visitPageButton.clicked.connect(self.open_link)
        self.updateButton.clicked.connect(self.update_file)
        # self.resultTable.setVisible(False)
        self.table_default()
        self.noResultWidget.setVisible(False)

    def run_trainer(self):
        self.trainer_thread = WorkerThread(self.current_exe)
        self.trainer_thread.finished.connect(lambda: print("Trainer quited"))
        self.trainer_thread.start()

    def open_link(self):
        link = self.data["files"]["trainers"][self.row][4]
        if link != "NONE":
            webbrowser.open(link)

    def open_folder(self):
        path = self.data["config"]["download"]["trainer"]
        path = os.path.normpath(path)
        print(path)
        subprocess.run(f'explorer "{path}"')

    def remove_file(self):
        mbox = MessageBox("Warning", "Are you sure you want to delete this file? This operation is irreversible.", self)
        if mbox.exec():
            os.remove(self.current_exe)
            if self.file_name_list[self.row][-3] == "COMMON":
                os.remove(self.file_name_list[self.row][3])
            if self.file_name_list[self.row][-1] == "REGISTERED":
                del self.file_name_list[self.row]
                self.data["files"]["trainers"] = self.file_name_list
                utils.Data.json_write("data/data.json", self.data)
            else:
                del self.file_name_list[self.row]
            self.table_default()

    def update_file(self):
        url = self.file_name_list[self.row][5]
        root_folder = self.data["config"]["download"]["trainer"]
        queryObj = crawler.Spider.Download(url)
        res = queryObj.run()
        if res:
            print("Removing: ", self.current_exe)
            os.remove(self.file_name_list[self.row][1])  # Remove previous file
            file_name = root_folder + res[0][0] + ".zip"
            print("Downloading: ", file_name)
            utils.Download.download_file(res[0][1], file_name)  # Download new file
            exe = utils.Download.extract_file(file_name)
            if exe == -1:
                Error.FileError.ExtractionError()
            os.remove(file_name)  # Remove zip file after extraction.
            self.data["files"]["trainers"][self.row][1] = root_folder + exe  # Update new exe name.
            self.data["files"]["trainers"][self.row][2] = time.strftime('%Y-%m-%d',
                                                                        time.localtime())  # Update new download time
            utils.Data.json_write("data/data.json", self.data)
            print(f"Registration of <{self.file_name_list[self.row][0]}> updated.")
            mb = MessageBox("Notification", f"{self.file_name_list[self.row][0]} is now up to date.", self)
            mb.cancelButton.hide()
            if mb.exec():
                pass

        else:
            mb = MessageBox("Error", f"Download links of {self.file_name_list[self.row][0]} are not found.", self)
            mb.yesButton.setText('Report Issue')
            mb.cancelButton.setText('Cancel')
            if mb.exec():
                utils.Help.report("Issue Report",
                                  f"Resource Unavailable: Cannot reach download resource of <{self.file_name_list[self.row][0]}>",
                                  time.asctime())

    def table_default(self):
        self.data = utils.Data.json_read("data/data.json")
        self.separator_vertical_middle.setVisible(False)
        self.detailImage.setVisible(False)
        self.detailLabel.setVisible(False)
        self.runButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.deleteButton.setVisible(False)
        self.updateButton.setVisible(False)
        self.resultTable.setVisible(True)
        file_name_list = self.data["files"]["trainers"]
        self.file_name_list = file_name_list
        if self.data["config"]["library"]["filter"] == "REGISTERED_ONLY":
            if len(file_name_list) <= 0:
                self.resultTable.setVisible(False)
                self.waitingWidget.setVisible(True)
                self.waitingWidget.setText("No downloaded trainers found.")
                return None
        else:
            names = []
            for file_info in file_name_list:
                names.append(file_info[1].split("\\")[-1])
            for temp_file in os.listdir(self.data["config"]["download"]["trainer"]):
                if temp_file not in names:
                    file_name_list.append([
                        "[UNREGISTERED] " + temp_file,
                        self.data["config"]["download"]["trainer"] + temp_file,
                        "UNKNOWN",
                        "UNKNOWN",
                        "UNKNOWN",
                        "UNKNOWN",
                        "UNREGISTERED"
                    ])
        self.fill_table(file_name_list)

    def show_detail(self, row, col):
        self.row = row
        self.separator_vertical_middle.setVisible(True)
        self.detailLabel.setVisible(True)
        self.detailImage.setVisible(True)
        self.runButton.setVisible(True)
        self.visitPageButton.setVisible(True)
        self.visitPageButton.setDisabled(False)
        self.updateButton.setVisible(True)
        self.updateButton.setDisabled(False)
        self.deleteButton.setVisible(True)
        pic = QPixmap()
        if self.file_name_list[row][-3] == "COMMON":
            pic_file = self.file_name_list[row][3]
            pic.load(pic_file)
            content = f"Name: {self.file_name_list[row][0]}\nDownload Time: {self.file_name_list[row][2]}"
        elif self.file_name_list[row][-3] == "ARCHIVED":
            content = f"File: {self.file_name_list[row][0]}\nDownload Time: {self.file_name_list[row][2]}\n**This is an archived Trainer**"
            pic.load(self.data["config"]["resources"]["blank_img"])
            self.visitPageButton.setDisabled(True)
            self.updateButton.setDisabled(True)
        else:
            content = f"File: {self.file_name_list[row][0]} \n**This file is not registered**"
            pic.load(self.data["config"]["resources"]["blank_img"])
            self.visitPageButton.setDisabled(True)
            self.updateButton.setDisabled(True)
        self.detailLabel.setText(content)
        self.detailLabel.setFont(Font.STANDARD_FONT)
        self.detailImage.setImage(pic)
        self.detailImage.setFixedSize(250, 250)
        self.current_exe = self.file_name_list[row][1]
        self.resultTable.resizeColumnsToContents()

    def fill_table(self, table):
        count = len(table)
        self.resultLabel.setText(f"There are {count} trainer(s) in your library.")
        self.waitingWidget.setVisible(False)
        self.resultTable.setRowCount(count)
        self.resultTable.clear()
        if count == 0:
            self.noResultWidget.setVisible(True)
            return None
        for row in range(count):
            item = QTableWidgetItem()
            item.setText(table[row][0])
            item.setFont(Font.STANDARD_FONT)
            if table[row][-3] != "COMMON":
                item.setForeground(QBrush(Qt.gray))
            if table[row][-1] != "REGISTERED":
                item.setForeground(QBrush(Qt.red))
            self.resultTable.setItem(row, 0, item)
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class GameWidget(QFrame):
    class CreateNewGameMessageBox(MessageBoxBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.titleLabel = SubtitleLabel('Create New Local-Game Configuration', self)
            self.nameLineEdit = LineEdit(self)
            self.nameLineEdit.setPlaceholderText('Name')
            self.nameLineEdit.setClearButtonEnabled(True)
            self.gameLocationLineEdit = LineEdit(self)
            self.gameLocationLineEdit.setPlaceholderText('Game Location')
            self.gameLocationLineEdit.setClearButtonEnabled(True)
            self.gameLocationButton = PushButton(self)
            self.gameLocationButton.setText("Select")
            self.coverLocationLineEdit = LineEdit(self)
            self.coverLocationLineEdit.setPlaceholderText('Cover Location [optional]')
            self.coverLocationLineEdit.setClearButtonEnabled(True)
            self.coverLocationButton = PushButton(self)
            self.coverLocationButton.setText("Select")
            self.categoryCombo = ComboBox(self)
            cats = utils.Data.json_read("data/data.json")["files"]["game_cats"]
            self.categoryCombo.addItems(cats)
            self.categoryCombo.removeItem(cats.index("ALL"))
            self.infoLineEdit = LineEdit(self)
            self.infoLineEdit.setPlaceholderText('Introduction [optional]')
            self.infoLineEdit.setClearButtonEnabled(True)

            self.gameLocationLayout = QHBoxLayout(self)
            self.gameLocationLayout.addWidget(self.gameLocationLineEdit, 3)
            self.gameLocationLayout.addWidget(self.gameLocationButton, 1)
            self.coverLocationLayout = QHBoxLayout(self)
            self.coverLocationLayout.addWidget(self.coverLocationLineEdit, 3)
            self.coverLocationLayout.addWidget(self.coverLocationButton, 1)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.nameLineEdit)
            self.viewLayout.addLayout(self.gameLocationLayout)
            self.viewLayout.addLayout(self.coverLocationLayout)
            self.viewLayout.addWidget(self.infoLineEdit)
            self.viewLayout.addWidget(self.categoryCombo)

            self.yesButton.setText('Confirm')
            self.cancelButton.setText('Cancel')
            self.yesButton.setDisabled(True)
            self.widget.setMinimumWidth(350)

            self.nameLineEdit.textChanged.connect(self.check_input)
            self.gameLocationLineEdit.textChanged.connect(self.check_input)
            self.gameLocationButton.clicked.connect(self._select_game_path)
            self.coverLocationButton.clicked.connect(self._select_cover_path)

        def check_input(self):
            if self.nameLineEdit.text() != "" and self.gameLocationLineEdit.text() != "":
                self.yesButton.setEnabled(True)
            else:
                self.yesButton.setDisabled(True)

        def _select_game_path(self):
            w = QFileDialog(self)
            w.setWindowTitle("Select a file")
            w.setFileMode(QFileDialog.AnyFile)
            w.setDirectory(os.getcwd())
            w.setNameFilter("Executable File (*.exe)")
            file_path = w.exec()
            if file_path and w.selectedFiles():
                path = w.selectedFiles()[0]
                print("File:", path)
                self.gameLocationLineEdit.setText(str(path))
                self.nameLineEdit.setText(str(path).split("/")[-1].removesuffix(".exe"))

        def _select_cover_path(self):
            w = QFileDialog(self)
            w.setWindowTitle("Select a file")
            w.setFileMode(QFileDialog.AnyFile)
            w.setDirectory(os.getcwd())
            w.setNameFilter("Image File (*.*)")
            file_path = w.exec()
            if file_path and w.selectedFiles():
                path = w.selectedFiles()[0]
                print("File:", path)
                self.coverLocationLineEdit.setText(str(path))

    class ManageCategoriesMessageBox(MessageBoxBase):
        class NamingBox(MessageBoxBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.titleLabel = SubtitleLabel(self)
                self.titleLabel.setText("New Category")
                self.nameLineEdit = LineEdit(self)
                self.nameLineEdit.setPlaceholderText("Name of the category")
                self.viewLayout.addWidget(self.titleLabel)
                self.viewLayout.addWidget(self.nameLineEdit)
                self.widget.setMinimumWidth(300)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.cats = []
            self.data = utils.Data.json_read("data/data.json")
            self.titleLabel = SubtitleLabel('Manage Your Categories', self)
            self.categoryTable = TableWidget(self)
            self.categoryTable.horizontalHeader().setVisible(False)
            self.categoryTable.verticalHeader().setVisible(False)
            self.categoryTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.addNewCategoryButton = PrimaryPushButton("Add a Category")
            self.addNewCategoryButton.setIcon(FIF.FOLDER_ADD)
            self.deleteCategoryButton = PushButton("Delete a Category")
            self.deleteCategoryButton.setIcon(FIF.DELETE)
            self.yesButton.setText('OK')
            self.cancelButton.hide()

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.categoryTable)
            self.viewLayout.addWidget(self.addNewCategoryButton)
            self.viewLayout.addWidget(self.deleteCategoryButton)
            self.categoryTable.cellClicked.connect(lambda: self.deleteCategoryButton.setEnabled(True))
            self.deleteCategoryButton.clicked.connect(self.delete_category)
            self.addNewCategoryButton.clicked.connect(self.add_new_category)
            self.widget.setMinimumWidth(500)
            self.deleteCategoryButton.setDisabled(True)
            self.category_default()

        def category_default(self):
            self.cats = utils.Data.json_read("data/data.json")["files"]["game_cats"]
            self.cats.remove("ALL")
            self.cats.remove("UNCATEGORIZED")
            count = len(self.cats)
            self.categoryTable.setRowCount(count)
            self.categoryTable.setColumnCount(1)
            self.categoryTable.clear()
            for row in range(count):
                item = QTableWidgetItem()
                item.setText(self.cats[row])
                item.setFont(Font.STANDARD_FONT)
                self.categoryTable.setItem(row, 0, item)
            self.categoryTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        def delete_category(self):
            w = MessageBox("Confirmation", "Are you sure you want to delete the category?", self)
            if w.exec():
                games = self.data["files"]["games"]
                count = 0
                cat = self.categoryTable.currentItem().text()
                for game in games:
                    if game[-1] == cat:
                        self.data["files"]["games"][count][-1] = "UNCATEGORIZED"
                    count += 1
                self.data["files"]["game_cats"].remove(cat)
                utils.Data.json_write("data/data.json", self.data)
                self.category_default()

        def add_new_category(self):
            w = self.NamingBox(self)
            if w.exec():
                name = w.nameLineEdit.text()
            else:
                return None
            self.categoryTable.insertRow(self.categoryTable.rowCount())
            item = QTableWidgetItem()
            item.setText(name)
            self.categoryTable.setItem(self.categoryTable.rowCount(), 0, item)
            self.data["files"]["game_cats"].append(name)
            utils.Data.json_write("data/data.json", self.data)
            self.category_default()

    class EditGameMessageBox(MessageBoxBase):
        def __init__(self, row, parent=None):
            super().__init__(parent)
            self.data = utils.Data.json_read("data/data.json")
            self.titleLabel = SubtitleLabel('Edit Game Configuration', self)
            self.nameLineEdit = LineEdit(self)
            self.nameLineEdit.setText(self.data["files"]["games"][row][0])
            self.nameLineEdit.setClearButtonEnabled(True)
            self.gameLocationLineEdit = LineEdit(self)
            self.gameLocationLineEdit.setText(self.data["files"]["games"][row][1])
            self.gameLocationLineEdit.setClearButtonEnabled(True)
            self.gameLocationButton = PushButton(self)
            self.gameLocationButton.setText("Select")
            self.coverLocationLineEdit = LineEdit(self)
            self.coverLocationLineEdit.setPlaceholderText('New Cover Location')
            self.coverLocationLineEdit.setClearButtonEnabled(True)
            self.coverLocationButton = PushButton(self)
            self.coverLocationButton.setText("Select")
            self.coverClearButton = PushButton(self)
            self.coverClearButton.setText("Clear")
            self.categoryCombo = ComboBox(self)
            cats = utils.Data.json_read("data/data.json")["files"]["game_cats"]
            self.categoryCombo.addItems(cats)
            self.categoryCombo.removeItem(cats.index("ALL"))
            self.categoryCombo.setCurrentText(self.data["files"]["games"][row][-1])
            self.infoLineEdit = LineEdit(self)
            if self.data["files"]["games"][row][3]:
                self.infoLineEdit.setText(self.data["files"]["games"][row][3])
            else:
                self.infoLineEdit.setPlaceholderText("Introduction [optional]")
            self.infoLineEdit.setClearButtonEnabled(True)

            self.gameLocationLayout = QHBoxLayout(self)
            self.gameLocationLayout.addWidget(self.gameLocationLineEdit, 3)
            self.gameLocationLayout.addWidget(self.gameLocationButton, 1)
            self.coverLocationLayout = QHBoxLayout(self)
            self.coverLocationLayout.addWidget(self.coverLocationLineEdit, 4)
            self.coverLocationLayout.addWidget(self.coverLocationButton, 1)
            self.coverLocationLayout.addWidget(self.coverClearButton, 1)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.nameLineEdit)
            self.viewLayout.addLayout(self.gameLocationLayout)
            self.viewLayout.addLayout(self.coverLocationLayout)
            self.viewLayout.addWidget(self.infoLineEdit)
            self.viewLayout.addWidget(self.categoryCombo)

            self.yesButton.setText('Confirm')
            self.cancelButton.setText('Cancel')
            self.widget.setMinimumWidth(450)

            self.nameLineEdit.textChanged.connect(self.check_input)
            self.gameLocationLineEdit.textChanged.connect(self.check_input)
            self.gameLocationButton.clicked.connect(self._select_game_path)
            self.coverLocationButton.clicked.connect(self._select_cover_path)
            self.coverClearButton.clicked.connect(lambda: self.coverLocationLineEdit.setText("CLEAR"))

        def check_input(self, text):
            if self.nameLineEdit.text() != "" and self.gameLocationLineEdit.text() != "":
                self.yesButton.setEnabled(True)
            else:
                self.yesButton.setDisabled(True)

        def _select_game_path(self):
            w = QFileDialog(self)
            w.setWindowTitle("Select a file")
            w.setFileMode(QFileDialog.AnyFile)
            w.setDirectory(os.getcwd())
            w.setNameFilter("Executable File (*.exe)")
            file_path = w.exec()
            if file_path and w.selectedFiles():
                path = w.selectedFiles()[0]
                print("File:", path)
                self.gameLocationLineEdit.setText(str(path))
                self.nameLineEdit.setText(str(path).split("/")[-1].removesuffix(".exe"))

        def _select_cover_path(self):
            w = QFileDialog(self)
            w.setWindowTitle("Select a file")
            w.setFileMode(QFileDialog.AnyFile)
            w.setDirectory(os.getcwd())
            w.setNameFilter("Image File (*.*)")
            file_path = w.exec()
            if file_path and w.selectedFiles():
                path = w.selectedFiles()[0]
                print("File:", path)
                self.coverLocationLineEdit.setText(str(path))

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.game_list = []
        self.row = None
        self.current_exe = None
        self.data = utils.Data.json_read("data/data.json")
        self.setObjectName("Game")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMiddle = QVBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.vBoxLayoutMiddle.setSpacing(10)

        self.titleLabel = TitleLabel("Local Games", self)
        self.titleLabel.setFixedHeight(40)
        self.filter = ComboBox(self)
        self.filter.setPlaceholderText("Filter")
        self.manageCategoryButton = PrimaryPushButton(self)
        self.manageCategoryButton.setIcon(FIF.FOLDER_ADD)
        self.manageCategoryButton.setText("Manage Categories")
        self.addNewButton = PrimaryPushButton(self)
        self.addNewButton.setIcon(FIF.ADD_TO)
        self.addNewButton.setText("Add new Game")
        self.refreshButton = PushButton(self)
        self.refreshButton.setIcon(FIF.UPDATE)
        self.refreshButton.setText("Refresh")

        self.resultTable = TableWidget(self)
        self.resultTable.setColumnCount(2)
        self.resultTable.horizontalHeader().setVisible(False)
        self.resultTable.verticalHeader().setVisible(False)
        self.resultTable.setEditTriggers(TableWidget.NoEditTriggers)
        self.resultTable.setShowGrid(False)

        self.separator_horiz_top = HorizontalSeparator(self)
        self.separator_vertical_middle = VerticalSeparator(self)

        self.noResultWidget = BodyLabel(self)
        self.noResultWidget.setText("No results found.")
        self.noResultWidget.setFont(Font.STANDARD_HUGE_FONT)
        self.noResultWidget.setAlignment(Qt.AlignCenter)

        self.detailImage = ImageLabel(self)
        self.detailLabel = BodyLabel(self)
        self.runButton = PrimaryPushButton("Launch", self)
        self.runButton.setIcon(FIF.PLAY)
        self.editButton = PushButton("Edit", self)
        self.editButton.setIcon(FIF.EDIT)
        # self.deleteButton = PushButton("Delete", self)
        # self.deleteButton.setIcon(FIF.DELETE)
        self.removeButton = PushButton("Remove", self)
        self.removeButton.setIcon(FIF.CLOSE)
        self.folderButton = PushButton("Browse File", self)
        self.folderButton.setIcon(FIF.FOLDER)

        self.hBoxLayoutTop.addWidget(self.filter, 1)
        self.hBoxLayoutTop.addWidget(self.manageCategoryButton, 1)
        self.hBoxLayoutTop.addWidget(self.addNewButton, 1, )
        self.hBoxLayoutTop.addWidget(self.refreshButton, 1)

        self.vBoxLayoutMiddle.addWidget(self.detailImage, 1)
        self.vBoxLayoutMiddle.addWidget(self.detailLabel, 1)
        self.vBoxLayoutMiddle.addWidget(self.runButton)
        self.vBoxLayoutMiddle.addWidget(self.editButton)
        self.vBoxLayoutMiddle.addWidget(self.removeButton)
        self.vBoxLayoutMiddle.addWidget(self.folderButton)
        self.detail_widget_visibility(False)
        self.detailLabel.setFixedWidth(250)
        self.detailLabel.setWordWrap(True)

        self.hBoxLayoutMiddle.addWidget(self.resultTable)
        self.hBoxLayoutMiddle.addWidget(self.separator_vertical_middle)
        self.hBoxLayoutMiddle.addLayout(self.vBoxLayoutMiddle)
        self.separator_vertical_middle.setVisible(False)

        self.vBoxLayoutMain.addWidget(self.titleLabel, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop, 1)
        self.vBoxLayoutMain.addWidget(self.separator_horiz_top)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle, 1)

        self.filter.currentTextChanged.connect(lambda: self.table_default(self.filter.text()))
        self.resultTable.cellClicked.connect(self.show_detail)
        self.addNewButton.clicked.connect(self.add_new_game)
        self.manageCategoryButton.clicked.connect(self.manage_category)
        self.editButton.clicked.connect(self.edit_game)
        self.refreshButton.clicked.connect(self.refresh)
        self.removeButton.clicked.connect(lambda: self.delete_game("lib"))
        self.folderButton.clicked.connect(self.open_folder)
        self.runButton.clicked.connect(self.run_application)
        self.resultTable.cellDoubleClicked.connect(self.run_application)
        self.noResultWidget.setVisible(False)

        self.table_default("ALL")
        self.combobox_default()

    def run_application(self):
        self.current_exe = self.game_list[self.row][1]
        self.application_thread = WorkerThread(self.current_exe)
        self.application_thread.finished.connect(lambda: "Game quited")
        self.application_thread.start()

    def open_folder(self):
        path = os.path.dirname(self.game_list[self.row][1])
        path = os.path.normpath(path)
        print(path)
        subprocess.run(f'explorer "{path}"')

    def add_new_game(self):
        w = self.CreateNewGameMessageBox(self)
        if w.exec_():
            name = w.nameLineEdit.text()
            location = w.gameLocationLineEdit.text()
            cover = w.coverLocationLineEdit.text()
            if cover != "":
                shutil.copyfile(cover, os.path.normpath(
                    os.path.join(self.data["config"]["resources"]["cover_folder"], f"{name}.jpg")))
            introduction = w.infoLineEdit.text()
            category = w.categoryCombo.currentText()
            game = [name, location, time.strftime('%Y-%m-%d', time.localtime()), introduction, category]
            self.data["files"]["games"].append(game)
            utils.Data.json_write("data/data.json", self.data)
            self.refresh()

    def manage_category(self):
        w = self.ManageCategoriesMessageBox(self)
        if w.exec():
            self.refresh()

    def edit_game(self):
        w = self.EditGameMessageBox(self.resultTable.currentRow(), self)
        if w.exec():
            name = w.nameLineEdit.text()
            location = w.gameLocationLineEdit.text()
            introduction = w.infoLineEdit.text()
            category = w.categoryCombo.currentText()
            cover = w.coverLocationLineEdit.text()
            if cover != "":
                try:
                    if cover == "CLEAR":
                        os.remove(os.path.normpath(
                            os.path.join(self.data["config"]["resources"]["cover_folder"], f"{name}.jpg")))
                    else:
                        shutil.copyfile(cover,
                                        os.path.normpath(os.path.join(self.data["config"]["resources"]["cover_folder"],
                                                                      f"{name}.jpg")))
                except FileNotFoundError:
                    pass
            self.data["files"]["games"][self.resultTable.currentRow()] = [name, location,
                                                                          time.strftime('%Y-%m-%d', time.localtime()),
                                                                          introduction, category]
            utils.Data.json_write("data/data.json", self.data)
            self.refresh()

    def refresh(self):
        self.data = utils.Data.json_read("data/data.json")
        self.detail_widget_visibility(False)
        self.table_default()
        self.combobox_default()

    def delete_game(self, mode="lib"):
        if mode == "lib":
            w = MessageBox("Warning",
                           "This will permanently REMOVE the game from your library, but it will be still on your hard drive",
                           self)
        else:
            w = MessageBox("Warning",
                           "This will permanently REMOVE the game from your library, it will be also DELETED from your hard drive",
                           self)
        if w.exec():
            game = self.data["files"]["games"][self.resultTable.currentRow()]
            self.data["files"]["games"].remove(game)
            utils.Data.json_write("data/data.json", self.data)
            self.refresh()
            if mode == "all":
                try:
                    os.remove(game[1])
                except FileNotFoundError:
                    pass

    def combobox_default(self):
        cats = self.data["files"]["game_cats"]
        self.filter.clear()
        self.filter.addItems(cats)
        self.filter.setCurrentIndex(0)

    def table_default(self, key="ALL"):
        self.game_list = []
        self.resultTable.setVisible(True)
        for game in self.data["files"]["games"]:
            if game[-1] == key or key == "ALL":
                self.game_list.append(game)
        count = len(self.game_list)
        self.noResultWidget.setVisible(False)
        if count == 0:
            self.detail_widget_visibility(False)
            self.resultTable.setVisible(False)
            self.noResultWidget.setVisible(True)
            return None
        else:
            self.resultTable.setRowCount(count)
            self.resultTable.clear()
            for row in range(count):
                if self.game_list[row][-1] == key or key == "ALL":
                    item = QTableWidgetItem()
                    item.setText(self.game_list[row][0])
                    item.setFont(Font.STANDARD_FONT)
                    self.resultTable.setItem(row, 0, item)
            self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def detail_widget_visibility(self, visibility):
        self.separator_vertical_middle.setVisible(visibility)
        self.detailLabel.setVisible(visibility)
        self.detailImage.setVisible(visibility)
        self.runButton.setVisible(visibility)
        self.editButton.setVisible(visibility)
        self.folderButton.setVisible(visibility)
        self.removeButton.setVisible(visibility)

    def show_detail(self, row, col):
        self.row = row
        self.detail_widget_visibility(True)
        self.editButton.setDisabled(False)
        pic_name = self.game_list[self.row][0] + ".jpg"
        pic_name = os.path.normpath(os.path.join(self.data["config"]["resources"]["cover_folder"], pic_name))
        pic = QPixmap()
        if os.path.exists(pic_name):
            pic.load(pic_name)
        else:
            pic.load(self.data["config"]["resources"]["blank_img"])
        content = f"Name: {self.game_list[self.row][0]}\nCategory: {self.game_list[self.row][-1]}\nAdd/Edit Time: {self.game_list[self.row][2]}\nIntroduction: {self.game_list[self.row][3]}"

        self.detailLabel.setText(content)
        self.detailLabel.setFont(Font.STANDARD_FONT)
        self.detailImage.setImage(pic)
        self.detailImage.setFixedSize(250, 250)
        self.current_exe = self.game_list[row][1]
        self.resultTable.resizeColumnsToContents()


class SettingWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.resize(400, 400)
        self.data = utils.Data.json_read("data/data.json")
        # self.data = utils.Data.json_read("./data/data.json")
        self.setObjectName("Setting")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(15)

        self.titleLabel = SubtitleLabel("Settings", self)
        self.pathTitleLabel = BodyLabel("Download Path", self)
        self.pathTitleLabel.setFont(Font.STANDARD_MIDDLE_FONT)
        self.trainerLabel = BodyLabel("Trainer Download Path:", self)
        self.gameLabel = BodyLabel("Game Download Path:", self)
        self.patchLabel = BodyLabel("Patch Download Path:", self)

        self.trainerLineEdit = LineEdit(self)
        self.gameLineEdit = LineEdit(self)
        self.patchLineEdit = LineEdit(self)
        self.trainerButton = PushButton("Select", self)
        self.gameButton = PushButton("Select", self)
        self.patchButton = PushButton("Select", self)
        self.miscTitle = BodyLabel("Misc", self)
        self.miscTitle.setFont(Font.STANDARD_MIDDLE_FONT)
        self.detailImgSwitch = SwitchButton(self)
        self.detailImgSwitch.setOnText("Enable Detail Image Cache")
        self.detailImgSwitch.setOffText("Disable Detail Image Cache")
        self.trainerFilterSwitch = SwitchButton(self)
        self.trainerFilterSwitch.setOnText("Enable Library Filter: Registered Trainers Only")
        self.trainerFilterSwitch.setOffText("Disable Library Filter: All (Not Recommended)")
        self.connectionSwitch = SwitchButton(self)
        self.connectionSwitch.setOnText("Enable Internet Connection")
        self.connectionSwitch.setOffText("Disable Internet Connection")

        self.customTitle = BodyLabel("User", self)
        self.customTitle.setFont(Font.STANDARD_MIDDLE_FONT)
        self.usernameLabel = BodyLabel("Username:", self)
        self.usernameLineEdit = LineEdit(self)
        self.avatarLabel = BodyLabel("Avatar:", self)
        self.avatarLineEdit = LineEdit(self)
        self.avatarButton = PushButton("Select", self)

        self.applyButton = PrimaryPushButton("Apply", self)
        self.undoButton = PushButton("Undo", self)

        self.pathBox = QGridLayout(self)
        self.miscBox = QGridLayout(self)
        self.userBox = QGridLayout(self)
        self.operationBox = QHBoxLayout(self)

        self.pathBox.addWidget(self.trainerLabel, 1, 1)
        self.pathBox.addWidget(self.trainerLineEdit, 1, 2)
        self.pathBox.addWidget(self.trainerButton, 1, 3)
        self.pathBox.addWidget(self.gameLabel, 2, 1)
        self.pathBox.addWidget(self.gameLineEdit, 2, 2)
        self.pathBox.addWidget(self.gameButton, 2, 3)
        self.pathBox.addWidget(self.patchLabel, 3, 1)
        self.pathBox.addWidget(self.patchLineEdit, 3, 2)
        self.pathBox.addWidget(self.patchButton, 3, 3)

        self.miscBox.addWidget(self.detailImgSwitch, 1, 1)
        self.miscBox.addWidget(self.trainerFilterSwitch, 1, 2)
        self.miscBox.addWidget(self.connectionSwitch, 2, 1)

        self.userBox.addWidget(self.usernameLabel, 1, 1)
        self.userBox.addWidget(self.usernameLineEdit, 1, 2, 1, 2)
        self.userBox.addWidget(self.avatarLabel, 2, 1)
        self.userBox.addWidget(self.avatarLineEdit, 2, 2)
        self.userBox.addWidget(self.avatarButton, 2, 3)

        self.operationBox.addWidget(self.undoButton)
        self.operationBox.addWidget(self.applyButton)

        self.hSeperator_1 = HorizontalSeparator(self)
        self.hSeperator_2 = HorizontalSeparator(self)
        self.hSeperator_3 = HorizontalSeparator(self)
        self.hSeperator_4 = HorizontalSeparator(self)
        self.hSeperator_5 = HorizontalSeparator(self)

        self.vBoxLayoutMain.addWidget(self.titleLabel)
        self.vBoxLayoutMain.addWidget(self.hSeperator_1)
        self.vBoxLayoutMain.addWidget(self.pathTitleLabel)
        self.vBoxLayoutMain.addLayout(self.pathBox)
        self.vBoxLayoutMain.addWidget(self.hSeperator_2)
        self.vBoxLayoutMain.addWidget(self.miscTitle)
        self.vBoxLayoutMain.addLayout(self.miscBox)
        self.vBoxLayoutMain.addWidget(self.hSeperator_4)
        self.vBoxLayoutMain.addWidget(self.customTitle)
        self.vBoxLayoutMain.addLayout(self.userBox)
        self.vBoxLayoutMain.addWidget(self.hSeperator_5)
        self.vBoxLayoutMain.addLayout(self.operationBox)

        self.trainerButton.clicked.connect(lambda: self._select_folder("trainer"))
        self.gameButton.clicked.connect(lambda: self._select_folder("game"))
        self.patchButton.clicked.connect(lambda: self._select_folder("patch"))
        self.avatarButton.clicked.connect(self._select_file)
        self.applyButton.clicked.connect(self.save_change)
        self.undoButton.clicked.connect(self.data_init)

        self.data_init()

    def data_init(self):
        self.data = utils.Data.json_read("data/data.json")
        trainer_path = self.data["config"]["download"]["trainer"]
        game_path = self.data["config"]["download"]["games"]
        patch_path = self.data["config"]["download"]["patches"]
        username = self.data["config"]["program"]["username"]
        avatar = self.data["config"]["program"]["user_avatar"]
        bool_img_cache = self.data["config"]["cache"]["detail_image"]
        if self.data["config"]["library"]["filter"]:
            bool_library_filter = True
        else:
            bool_library_filter = False
        bool_connection = self.data["config"]["program"]["connection_allow"]

        self.trainerLineEdit.setText(trainer_path)
        self.gameLineEdit.setText(game_path)
        self.patchLineEdit.setText(patch_path)
        self.detailImgSwitch.setChecked(bool_img_cache)
        self.trainerFilterSwitch.setChecked(bool_library_filter)
        self.connectionSwitch.setChecked(bool_connection)
        self.usernameLineEdit.setText(username)
        self.avatarLineEdit.setText(avatar)

    def _select_folder(self, mode):
        dir_path = QFileDialog.getExistingDirectory(self, f'Select the {mode} download path', os.getcwd())
        if dir_path:
            if mode == "trainer":
                self.trainerLineEdit.setText(dir_path)
            elif mode == "patch":
                self.patchLineEdit.setText(dir_path)
            elif mode == "games":
                self.gameLineEdit.setText(dir_path)

    def _select_file(self):
        w = QFileDialog(self)
        w.setWindowTitle(f"Select a avatar file")
        w.setFileMode(QFileDialog.AnyFile)
        w.setDirectory(os.getcwd())
        w.setNameFilter("Image File (*.png, *.jpg)")
        file_path = w.exec()
        if file_path and w.selectedFiles():
            path = w.selectedFiles()[0]
            self.avatarLineEdit.setText(path)

    def input_validating(self):
        os.chdir(".")
        path_list = []
        invalid_list = []
        path_list.append(self.trainerLineEdit.text())
        path_list.append(self.gameLineEdit.text())
        path_list.append(self.patchLineEdit.text())
        path_list.append(self.avatarLineEdit.text())
        for path in path_list:
            if not os.path.exists(path):
                invalid_list.append(path)
        if len(invalid_list) > 0:
            w = MessageBox("Warning", f"The following paths you input are invalid:\n{invalid_list}", self)
            w.cancelButton.hide()
            if w.exec():
                self.data_init()
                return False
        if self.usernameLineEdit == "":
            w = MessageBox("Warning", "Username cannot be empty.", self)
            w.cancelButton.hide()
            if w.exec():
                self.data_init()
                return False
        return True

    def save_change(self):
        if not self.input_validating():
            return False
        self.data["config"]["download"]["trainer"] = self.trainerLineEdit.text()
        self.data["config"]["download"]["games"] = self.gameLineEdit.text()
        self.data["config"]["download"]["patches"] = self.patchLineEdit.text()
        self.data["config"]["cache"]["detail_image"] = self.detailImgSwitch.isChecked()
        if self.trainerFilterSwitch.isChecked():
            self.data["config"]["library"]["filter"] = "REGISTERED_ONLY"
        else:
            self.data["config"]["library"]["filter"] = "ALL"
        self.data["config"]["program"]["connection_allow"] = self.connectionSwitch.isChecked()
        self.data["config"]["program"]["username"] = self.usernameLineEdit.text()
        self.data["config"]["program"]["user_avatar"] = self.avatarLineEdit.text()

        print(self.data["config"])

        utils.Data.json_write("data/data.json", self.data)


# TODO: New feature: Helping widget
class HelpingWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.resize(400, 400)
        self.config = utils.Data.json_read("data/data.json")["config"]
        # self.data = utils.Data.json_read("./data/data.json")
        self.setObjectName("Help")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.hBoxLayoutTrainer = QHBoxLayout(self)
        self.hBoxLayoutPatches = QHBoxLayout(self)
        self.hBoxLayoutDev = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.hBoxLayoutPatches.setSpacing(20)
        self.hBoxLayoutDev.setSpacing(20)

        self.title_label = TitleLabel("Help", self)
        self.title_label.setFixedHeight(40)
        """self.docTitleLabel = BodyLabel(self)
        self.docTitleLabel.setFont(STANDARD_FONT)
        self.docTitleLabel.setText("Helping Document")"""
        self.docButton = PrimaryPushButton(self)
        self.docButton.setText("Read Document")
        self.docButton.setFont(Font.STANDARD_FONT)
        self.docButton.setIcon(FIF.LINK)

        self.trainerTitleLabel = SubtitleLabel("FLiNG Trainer Website", self)
        self.trainerButton = PushButton(self)
        self.trainerButton.setText("Visit Homepage")
        self.trainerButton.setFont(Font.STANDARD_FONT)
        self.trainerButton.setIcon(FIF.LINK)
        self.trainerArchivedButton = PushButton(self)
        self.trainerArchivedButton.setText("View Archived Trainers")
        self.trainerArchivedButton.setFont(Font.STANDARD_FONT)
        self.trainerArchivedButton.setIcon(FIF.LINK)

        self.patchTitleLabel = SubtitleLabel("Patch", self)
        self.nekoNyanButton = PushButton(self)
        self.nekoNyanButton.setText("NekoNyan Game Patches")
        self.nekoNyanButton.setFont(Font.STANDARD_FONT)
        self.nekoNyanButton.setIcon(FIF.LINK)
        self.kaguraButton = PushButton(self)
        self.kaguraButton.setText("Kagura Game Patches")
        self.kaguraButton.setFont(Font.STANDARD_FONT)
        self.kaguraButton.setIcon(FIF.LINK)

        self.devTitleLabel = SubtitleLabel("Developer", self)
        self.repoButton = PushButton(self)
        self.repoButton.setText("View the repository on GitHub")
        self.repoButton.setFont(Font.STANDARD_FONT)
        self.repoButton.setIcon(FIF.GITHUB)
        self.steamButton = PushButton(self)
        self.steamButton.setText("Steam Profile")
        self.steamButton.setFont(Font.STANDARD_FONT)
        self.steamButton.setIcon(FIF.LINK)

        self.hSeperator_1 = HorizontalSeparator(self)
        self.hSeperator_2 = HorizontalSeparator(self)
        self.hSeperator_3 = HorizontalSeparator(self)
        self.hSeperator_4 = HorizontalSeparator(self)
        self.hSeperator_5 = HorizontalSeparator(self)

        self.hBoxLayoutTrainer.addWidget(self.trainerTitleLabel)
        self.hBoxLayoutTrainer.addWidget(self.trainerButton)
        self.hBoxLayoutTrainer.addWidget(self.trainerArchivedButton)
        self.hBoxLayoutPatches.addWidget(self.patchTitleLabel)
        self.hBoxLayoutPatches.addWidget(self.nekoNyanButton)
        self.hBoxLayoutPatches.addWidget(self.kaguraButton)
        self.hBoxLayoutDev.addWidget(self.devTitleLabel)
        self.hBoxLayoutDev.addWidget(self.repoButton)
        self.hBoxLayoutDev.addWidget(self.steamButton)

        self.vBoxLayoutMain.addWidget(self.title_label, 1)
        self.vBoxLayoutMain.addWidget(self.hSeperator_1)
        self.vBoxLayoutMain.addWidget(self.docButton, 1)
        self.vBoxLayoutMain.addWidget(self.hSeperator_2)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTrainer, 1)
        self.vBoxLayoutMain.addWidget(self.hSeperator_3)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutPatches, 1)
        self.vBoxLayoutMain.addWidget(self.hSeperator_4)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutDev, 1)

        self.docButton.clicked.connect(
            lambda: webbrowser.open("https://github.com/OscarZhang-735/Trainer-Manager/blob/master/README.md"))
        self.trainerButton.clicked.connect(lambda: webbrowser.open("https://flingtrainer.com/"))
        self.trainerArchivedButton.clicked.connect(lambda: webbrowser.open("https://archive.flingtrainer.com/"))
        self.nekoNyanButton.clicked.connect(lambda: webbrowser.open("https://patches.nekonyansoft.com/"))
        self.kaguraButton.clicked.connect(lambda: webbrowser.open("https://www.kaguragames.com/product-tag/patch/"))
        self.repoButton.clicked.connect(lambda: webbrowser.open("https://github.com/OscarZhang-735/Trainer-Manager"))
        self.steamButton.clicked.connect(
            lambda: webbrowser.open("https://steamcommunity.com/profiles/76561199209380880/"))

    def write_report(self):
        pass

    def donate(self):
        pass


# TODO: New feature: Game saves management and back-up
class SavingWidget(QFrame):
    class CreateNewSaveMessageBox(MessageBoxBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.titleLabel = SubtitleLabel('Create New Back-Up Configuration', self)
            self.nameLineEdit = LineEdit(self)
            self.nameLineEdit.setPlaceholderText('Name of this configuration')
            self.srcLineEdit = LineEdit(self)
            self.srcLineEdit.setPlaceholderText('Source of the game saves:')
            self.srcLineEdit.setClearButtonEnabled(True)
            self.srcButton = PushButton("Select", self)
            self.dstLineEdit = LineEdit(self)
            self.dstLineEdit.setPlaceholderText('Destination of the game saves:')
            self.dstLineEdit.setClearButtonEnabled(True)
            self.dstButton = PushButton("Select", self)

            self.srcLayout = QHBoxLayout(self)
            self.dstLayout = QHBoxLayout(self)

            self.srcLayout.addWidget(self.srcLineEdit, 4)
            self.srcLayout.addWidget(self.srcButton, 1)
            self.dstLayout.addWidget(self.dstLineEdit, 4)
            self.dstLayout.addWidget(self.dstButton, 1)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.nameLineEdit)
            self.viewLayout.addLayout(self.srcLayout)
            self.viewLayout.addLayout(self.dstLayout)

            # change the text of button
            self.yesButton.setText('Confirm')
            self.cancelButton.setText('Cancel')
            self.yesButton.setDisabled(True)

            self.widget.setMinimumWidth(350)
            self.nameLineEdit.textChanged.connect(self._verify_path)
            self.srcLineEdit.textChanged.connect(self._verify_path)
            self.dstLineEdit.textChanged.connect(self._verify_path)
            self.srcButton.clicked.connect(lambda: self._folder_selector("src"))
            self.dstButton.clicked.connect(lambda: self._folder_selector("dst"))
            # self.hideYesButton()

        def _verify_path(self):
            if self.nameLineEdit.text() != "" and self.srcLineEdit.text() != "" and self.dstLineEdit.text() != "":
                self.yesButton.setEnabled(True)
            else:
                self.yesButton.setDisabled(True)

        def _folder_selector(self, mode):
            if mode == "src":
                title = 'Select the source'
            else:
                title = 'Select the destination'
            dir_path = QFileDialog.getExistingDirectory(self, title, os.getcwd())
            if dir_path:
                if mode == "src":
                    self.srcLineEdit.setText(dir_path)
                elif mode == "dst":
                    self.dstLineEdit.setText(dir_path)

    class SaveDetailMessageBox(MessageBoxBase):
        def __init__(self, file_row, parent=None):
            super().__init__(parent)
            self.data = utils.Data.json_read("data/data.json")
            self.file_row = file_row
            self.edited = False
            self.saves = []
            self.name = self.data["files"]["save_file"][self.file_row][0]
            self.src = self.data["files"]["save_file"][self.file_row][1]
            self.dst = self.data["files"]["save_file"][self.file_row][2]
            self.titleLabel = SubtitleLabel("Manage the save", self)
            self.nameLineEdit = LineEdit(self)
            self.nameLineEdit.setText(self.name)
            self.nameLineEdit.setClearButtonEnabled(True)
            self.srcLineEdit = LineEdit(self)
            self.srcLineEdit.setText(self.src)
            self.srcLineEdit.setClearButtonEnabled(True)
            self.srcButton = PushButton("Select", self)
            self.dstLineEdit = LineEdit(self)
            self.dstLineEdit.setText(self.dst)
            self.dstLineEdit.setClearButtonEnabled(True)
            self.dstButton = PushButton("Select", self)
            self.applyButton = PrimaryPushButton("Apply", self)
            self.applyButton.setIcon(FIF.COMPLETED)
            self.deleteConfigButton = PushButton("Delete the Config", self)
            self.deleteConfigButton.setIcon(FIF.REMOVE_FROM)
            self.hTopSeparator = HorizontalSeparator(self)
            self.tableTitleLabel = BodyLabel(self)
            self.backupTable = TableWidget(self)
            self.backupTable.horizontalHeader().setVisible(False)
            self.backupTable.verticalHeader().setVisible(False)
            self.backupTable.setEditTriggers(TableWidget.NoEditTriggers)
            self.backupTable.setBorderVisible(True)
            self.newBackupButton = PrimaryPushButton("Back up", self)
            self.newBackupButton.setIcon(FIF.SAVE_COPY)
            self.recoveryButton = PushButton("Recovery", self)
            self.recoveryButton.setIcon(FIF.COPY)
            self.deleteBackupButton = PushButton("Delete", self)
            self.deleteBackupButton.setIcon(FIF.DELETE)
            self.viewFolderButton = PushButton("View folder", self)
            self.viewFolderButton.setIcon(FIF.FOLDER)

            self.srcLayout = QHBoxLayout(self)
            self.dstLayout = QHBoxLayout(self)
            self.funcLayout = QGridLayout(self)

            self.srcLayout.addWidget(self.srcLineEdit, 4)
            self.srcLayout.addWidget(self.srcButton, 1)
            self.dstLayout.addWidget(self.dstLineEdit, 4)
            self.dstLayout.addWidget(self.dstButton, 1)
            self.funcLayout.addWidget(self.newBackupButton, 1, 1)
            self.funcLayout.addWidget(self.recoveryButton, 1, 2)
            self.funcLayout.addWidget(self.deleteBackupButton, 2, 1)
            self.funcLayout.addWidget(self.viewFolderButton, 2, 2)

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.nameLineEdit)
            self.viewLayout.addLayout(self.srcLayout)
            self.viewLayout.addLayout(self.dstLayout)
            self.viewLayout.addWidget(self.applyButton)
            self.viewLayout.addWidget(self.deleteConfigButton)
            self.viewLayout.addWidget(self.hTopSeparator)
            self.viewLayout.addWidget(self.tableTitleLabel)
            self.viewLayout.addWidget(self.backupTable)
            self.viewLayout.addLayout(self.funcLayout)

            self.widget.setMinimumWidth(550)
            self.cancelButton.hide()

            self.recoveryButton.setDisabled(True)
            self.deleteBackupButton.setDisabled(True)
            self.viewFolderButton.setDisabled(True)
            self.applyButton.setDisabled(True)
            self.table_default()

            self.srcButton.clicked.connect(lambda: self._folder_selector("src"))
            self.dstButton.clicked.connect(lambda: self._folder_selector("dst"))
            self.backupTable.cellClicked.connect(lambda: self.activator_funcs(True))
            self.viewFolderButton.clicked.connect(self.view_folder)
            self.deleteBackupButton.clicked.connect(self.delete_save)
            self.newBackupButton.clicked.connect(self.new_backup)
            self.recoveryButton.clicked.connect(self.recovery_backup)
            self.nameLineEdit.textChanged.connect(self.info_change_check)
            self.srcLineEdit.textChanged.connect(self.info_change_check)
            self.dstLineEdit.textChanged.connect(self.info_change_check)
            self.applyButton.clicked.connect(self.apply_change)
            self.deleteConfigButton.clicked.connect(self.delete_config)

        def table_default(self):
            save_info = self.data["files"]["save_file"][self.file_row]
            dirs = []
            if not os.path.exists(save_info[2]):
                self.backupTable.setVisible(False)
                self.tableTitleLabel.setText("This destination folder is no longer available.")
                return False
            for file in os.scandir(save_info[2]):
                if file.is_dir():
                    dirs.append(file.name)
            count = len(dirs)
            self.saves = dirs
            if count != 0:
                self.tableTitleLabel.setText(f"There are {count} backed-up saves.")
                self.backupTable.setVisible(True)
                self.backupTable.setColumnCount(1)
                self.backupTable.setRowCount(count)
            else:
                self.backupTable.setVisible(False)
                self.tableTitleLabel.setText("There is 0 backed-up saves.")
            for dir in dirs:
                item = QTableWidgetItem()
                item.setText(dir)
                item.setFont(Font.STANDARD_FONT)
                self.backupTable.setItem(dirs.index(dir), 0, item)
            self.backupTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        def activator_funcs(self, status=True):
            if status and not self.backupTable.selectedItems():
                return False
            self.recoveryButton.setEnabled(status)
            self.deleteBackupButton.setEnabled(status)
            self.viewFolderButton.setEnabled(status)

        def view_folder(self):
            path = os.path.normpath(os.path.join(self.data["files"]["save_file"][self.file_row][2],
                                                 self.backupTable.item(self.backupTable.currentRow(), 0).text()))
            print(path)
            subprocess.run(f'explorer "{path}"')

        def _folder_selector(self, mode):
            if mode == "src":
                title = 'Select the new source'
            else:
                title = 'Select the new destination'
            dir_path = QFileDialog.getExistingDirectory(self, title, os.getcwd())
            if dir_path:
                if mode == "src":
                    self.srcLineEdit.setText(dir_path)
                elif mode == "dst":
                    self.dstLineEdit.setText(dir_path)

        def delete_save(self):
            path = os.path.normpath(os.path.join(self.dst, self.saves[self.backupTable.currentRow()]))
            w = MessageBox("Warning", f"Are you sure to remove this save:\n{path}\nThis operation is irreversible.",
                           self)
            if w.exec():
                shutil.rmtree(path)
                self.table_default()

        def delete_config(self):
            w = MessageBox("Warning", "Are you sure to remove this configuration?\nThis operation is irreversible",
                           self)
            if w.exec():
                del self.data["files"]["save_file"][self.file_row]
                utils.Data.json_write("data/data.json", self.data)
                n = MessageBox("Notification", "Would you like to clear the destination folder?", self)
                if n.exec():
                    shutil.rmtree(self.dst)
                self.close()

        def new_backup(self):
            dir_name = time.strftime("%Y-%m-%d@%H-%M-%S")
            dir_path = os.path.normpath(os.path.join(self.dst, dir_name))
            print(dir_path)
            if os.path.exists(dir_path):
                utils.Help.warning("Warning", f"Destination folder <{dir_path}> already exists.")
                return False
            if not os.path.exists(self.src):
                utils.Help.warning("Warning", f"Source folder <{self.src}> already exists.")
                return False
            shutil.copytree(self.src, dir_path)
            n = MessageBox("Notification", f"New backup created.\n<{dir_path}>", self)
            n.cancelButton.hide()
            if n.exec():
                pass
            self.table_default()

        def info_change_check(self):
            if self.nameLineEdit.text() != self.name or self.srcLineEdit.text() != self.src or self.dstLineEdit.text() != self.dst:
                self.activator_funcs(False)
                self.newBackupButton.setDisabled(True)
                self.applyButton.setEnabled(True)
                self.edited = True
            else:
                self.activator_funcs(True)
                self.newBackupButton.setEnabled(True)
                self.applyButton.setDisabled(True)
                self.edited = False

        def recovery_backup(self):
            w = MessageBox("Warning",
                           f"""
                           This operation will OVERWRITE your original save folder:
                           {self.src} .\n
                           It is strongly RECOMMENDED that you back everything up in advance.
                           This operation is IRREVERSIBLE.
                           """,
                           self)
            if w.exec():
                path = os.path.normpath(os.path.join(self.dst, self.saves[self.self.backupTable.currentRow()]))
                if not os.path.exists(path) or not os.path.exists(self.src):
                    utils.Help.warning("Warning", "Destination or Source folder doesn't exist.")
                    return False
                shutil.rmtree(self.src)
                shutil.copytree(path, self.src)
                n = MessageBox("Notification",
                               f"Recovery Successful.\n{path} -> {self.src}",
                               self)
                n.cancelButton.hide()
                if n.exec():
                    pass

        def apply_change(self):
            name = self.nameLineEdit.text()
            src = self.srcLineEdit.text()
            dst = self.dstLineEdit.text()
            name_collision = False
            dst_collision = False
            for item in self.data["files"]["save_file"]:
                if self.data["files"]["save_file"].index(item) != self.file_row:
                    if name == item[0]:
                        name_collision = True
                    if dst == item[2]:
                        dst_collision = True
                if name_collision and dst_collision:
                    break

            if name_collision or dst_collision:
                content = ""
                if name_collision:
                    content = f"The name '{name}' is already occupied by another configuration"
                    self.nameLineEdit.setText(self.name)
                elif dst_collision:
                    content = f"The destination '{dst}' is already occupied by another configuration"
                    self.dstLineEdit.setText(self.dst)
                w = MessageBox("Warning", content, self)
                w.cancelButton.hide()
                if w.exec():
                    pass
                return False
            self.data["files"]["save_file"][self.file_row][0] = name
            self.data["files"]["save_file"][self.file_row][1] = src
            self.data["files"]["save_file"][self.file_row][2] = dst
            if dst != self.dst:
                n = MessageBox("Notification", "Would you like to clear the original destination folder?", self)
                if n.exec():
                    shutil.rmtree(self.dst)
            utils.Data.json_write("data/data.json", self.data)
            self.data = utils.Data.json_read("data/data.json")
            self.name = self.data["files"]["save_file"][self.file_row][0]
            self.src = self.data["files"]["save_file"][self.file_row][1]
            self.dst = self.data["files"]["save_file"][self.file_row][2]
            self.table_default()
            self.info_change_check()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data = utils.Data.json_read("data/data.json")
        self.setObjectName("Saving")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.hBoxLayoutMiddle.setSpacing(20)

        self.titleLabel = TitleLabel("Saves", self)
        self.titleLabel.setFixedHeight(40)
        self.refreshButton = PushButton(self)
        self.refreshButton.setIcon(FIF.UPDATE)
        self.refreshButton.setText("Refresh")
        self.cloudSyncButton = PushButton(self)
        self.cloudSyncButton.setIcon(FIF.CLOUD_DOWNLOAD)
        self.cloudSyncButton.setText("Cloud Sync")
        self.cloudSyncButton.setDisabled(True)
        self.addNewButton = PrimaryPushButton(self)
        self.addNewButton.setIcon(FIF.ADD_TO)
        self.addNewButton.setText("Add new save")
        self.backupAllButton = PrimaryPushButton(self)
        self.backupAllButton.setIcon(FIF.SAVE_COPY)
        self.backupAllButton.setText("Back Up All")
        self.noSavesLabel = BodyLabel("Oops! No saves found.", self)
        self.noSavesLabel.setFont(Font.STANDARD_HUGE_FONT)
        self.noSavesLabel.setAlignment(Qt.AlignCenter)
        self.savesTable = TableWidget(self)
        self.savesTable.horizontalHeader().setVisible(False)
        self.savesTable.verticalHeader().setVisible(False)
        self.savesTable.setColumnCount(1)
        self.savesTable.setEditTriggers(TableWidget.NoEditTriggers)
        self.savesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horiz_seperator_1 = HorizontalSeparator(self)

        self.savesTable.setVisible(False)

        self.hBoxLayoutTop.addWidget(self.addNewButton, 2)
        self.hBoxLayoutTop.addWidget(self.backupAllButton, 2)
        self.hBoxLayoutTop.addWidget(self.cloudSyncButton, 1)
        self.hBoxLayoutTop.addWidget(self.refreshButton, 1)
        self.hBoxLayoutMiddle.addWidget(self.noSavesLabel)
        self.hBoxLayoutMiddle.addWidget(self.savesTable)

        self.vBoxLayoutMain.addWidget(self.titleLabel)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop)
        self.vBoxLayoutMain.addWidget(self.horiz_seperator_1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle)

        self.save_table_default()
        self.addNewButton.clicked.connect(self.create_backup)
        self.refreshButton.clicked.connect(self.refresh)
        self.savesTable.cellDoubleClicked.connect(self.save_detail)
        self.backupAllButton.clicked.connect(self.backup_all)

    def refresh(self):
        self.data = utils.Data.json_read("data/data.json")
        self.save_table_default()

    def save_table_default(self):
        save_list = self.data["files"]["save_file"]
        count = len(save_list)
        if count != 0:
            self.savesTable.setVisible(True)
            self.noSavesLabel.setVisible(False)
            self.savesTable.setRowCount(count)
            self.savesTable.clear()
        else:
            self.savesTable.setVisible(False)
            self.noSavesLabel.setVisible(True)
            self.savesTable.clear()
            return None
        for save in save_list:
            print(save)
            name = save[0]
            src_path = save[1]
            dst_path = save[2]
            item = QTableWidgetItem()
            item.setText(name)
            item.setFont(Font.STANDARD_FONT)
            self.savesTable.setItem(save_list.index(save), 0, item)

    def create_backup(self):
        w = self.CreateNewSaveMessageBox(self)
        if w.exec():
            name = w.nameLineEdit.text()
            src = w.srcLineEdit.text()
            dst = w.dstLineEdit.text()
            for item in self.data["files"]["save_file"]:
                if name == item[0] or dst == item[2]:
                    invalid = MessageBox("Warning",
                                         "Invalid name or destination, they may be occupied by other configuration",
                                         self)
                    invalid.cancelButton.hide()
                    if invalid.exec():
                        pass
                    return False
            self.data["files"]["save_file"].append([name, src, dst])
            utils.Data.json_write("data/data.json", self.data)
            self.refresh()

    def save_detail(self):
        w = self.SaveDetailMessageBox(self.savesTable.currentRow(), self)
        if w.exec() or w.close():
            self.refresh()

    # TODO: ALL-BACK-UP FEATURE INCOMPLETE
    def backup_all(self):
        save_list = self.data["files"]["save_file"]
        count = len(save_list)
        if count != 0:
            done_notice = "The following configurations have been backed-up successfully:"
            for i in range(count):
                item = save_list[i]
                name = item[0]
                src = item[1]
                dst = item[2]
                dst_name = time.strftime("%Y-%m-%d@%H-%M-%S")
                dst_path = os.path.normpath(os.path.join(dst, dst_name))
                print(f"{src} -> {dst_path}")
                if os.path.exists(dst_path):
                    utils.Help.warning("Warning", f"Destination folder <{dst_path}> already exists.")
                    return False
                if not os.path.exists(src):
                    utils.Help.warning("Warning", f"Source folder <{src}> doesn't exists.")
                    return False
                shutil.copytree(src, dst_path)
                done_notice += f"\n{name}"
            n = MessageBox("Notification", done_notice, self)
            n.cancelButton.hide()
            if n.exec():
                pass


# TODO: NEW FEATURE: Game patches download.
class PatchWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data = utils.Data.json_read("data/data.json")
        self.patches = utils.Data.json_read("data/patch.json")
        self.setObjectName("Patch")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.hBoxLayoutMiddle.setSpacing(20)

        self.titleLabel = TitleLabel("Patch", self)
        self.titleLabel.setFixedHeight(40)
        self.patchTable = TableWidget(self)
        self.patchTable.setColumnCount(2)
        self.patchTable.horizontalHeader().setVisible(False)
        self.patchTable.verticalHeader().setVisible(False)
        self.patchTable.setEditTriggers(TableWidget.NoEditTriggers)
        self.patchTable.setShowGrid(False)
        self.hSeperator_1 = HorizontalSeparator(self)

        self.hBoxLayoutMiddle.addWidget(self.patchTable)

        self.vBoxLayoutMain.addWidget(self.titleLabel)
        self.vBoxLayoutMain.addWidget(self.titleLabel)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop)
        self.vBoxLayoutMain.addWidget(self.hSeperator_1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle)

        self.list_table("nekoNyanSteam")

    def list_table(self, filter):
        patch_list = []
        if filter == "nekoNyanSteam":
            patch_list = self.patches["patches"]["neko_nyan_steam"]
        elif filter == "nekoNyanNonSteam":
            patch_list = self.patches["patches"]["neko_nyan_non_steam"]
        # print(patch_list)
        for patch in patch_list:
            item = QTableWidgetItem()
            item.setText(patch["name"])
            item.setFont(Font.STANDARD_FONT)
            self.patchTable.setItem(patch_list.index(patch), 1, item)


class AvatarWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage(USER_AVATAR).scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        if self.isPressed:
            painter.setOpacity(1)
        # draw background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont('Segoe UI')
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, USER_NAME)


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        # use dark theme mode
        setTheme(Theme.DARK)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        self.searchInterface = SearchWidget(self)
        self.libraryInterface = LibraryWidget(self)
        self.gameInterface = GameWidget(self)
        self.settingInterface = SettingWidget(self)
        # self.settingInterface = Widget("Settings", self)
        self.helpingInterface = HelpingWidget(self)
        self.savingInterface = SavingWidget(self)
        self.patchInterface = PatchWidget(self)
        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

    def initNavigation(self):
        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)
        self.addSubInterface(self.searchInterface, FIF.SEARCH, 'Search')
        self.addSubInterface(self.libraryInterface, FIF.APPLICATION, 'Trainers')
        self.addSubInterface(self.gameInterface, FIF.GAME, "Games")
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.savingInterface, FIF.FOLDER, 'Saves')
        self.navigationInterface.addSeparator()
        # self.addSubInterface(self.patchInterface, FIF.DOCUMENT, 'Patches')
        # self.navigationInterface.addSeparator()
        # self.addSubInterface(self.settingsInterface, FIF.SETTING, 'Settings')
        # add navigation items to scroll area
        self.addSubInterface(self.helpingInterface, FIF.HELP, 'Help', NavigationItemPosition.SCROLL)

        # add custom widget to bottom

        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # !IMPORTANT: don't forget to set the default route key
        qrouter.setDefaultRouteKey(self.stackWidget, self.libraryInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(1)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(ICON))
        self.setWindowTitle(TITLE)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        desktop = QApplication.desktop().availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)
        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resources/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())

    def showMessageBox(self):
        w = MessageBox("Version Info", "ver. NAN", self)
        w.yesButton.setText('Yes')
        w.cancelButton.setText('No')

        if w.exec():
            QDesktopServices.openUrl(QUrl())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


def exit_handler():
    """
    Remove image cache if there is when exiting .
    :return: None
    """
    try:
        os.remove("resources/img_cache/image.jpg")
    except FileNotFoundError:
        pass


def setup_check():
    requirements = ["./data", "./resources/game_covers", "./resources/img_cache"]
    missing = []
    for r in requirements:
        if not os.path.exists(r):
            missing.append(r)
    if len(missing) > 0:
        utils.Help.warning("Warning", f"Key files/directories are missing: {missing}.")
        exit()


if __name__ == '__main__':
    atexit.register(exit_handler)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    setup_check()
    app.exec_()
