# coding:utf-8
import subprocess
import sys
import os
import time
import atexit

from PyQt5.QtCore import Qt, QRect, QUrl
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices, QStandardItemModel, QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QVBoxLayout, QHeaderView, \
    QTableWidgetItem, QSizePolicy

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, qrouter, ImageLabel, BodyLabel, PushButton,
                            TableWidget, LineEdit, PrimaryPushButton, HorizontalSeparator, VerticalSeparator)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar
import crawler
import utils
import webbrowser
import keyboard

STANDARD_FONT = QFont()
STANDARD_FONT.setFamily("Segoe UI")
STANDARD_FONT.setPointSize(10)
STANDARD_HUGE_FONT = QFont()
STANDARD_HUGE_FONT.setFamily("Segoe UI")
STANDARD_HUGE_FONT.setPointSize(18)


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
        self.config = utils.Data.json_read("data\\data.json")["config"]
        self.data = utils.Data.json_read("./data/data.json")
        self.setObjectName("Search")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMiddle = QVBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.vBoxLayoutMiddle.setSpacing(10)

        self.searchLine = LineEdit(self)
        self.searchLine.setAlignment(Qt.AlignCenter)
        self.searchLine.setFixedWidth(300)
        self.searchButton = PrimaryPushButton(self)
        self.searchButton.setIcon(FIF.SEARCH)
        self.searchButton.setText("Search")

        self.clearButton = PushButton(self)
        self.clearButton.setIcon(FIF.CLOSE)
        self.clearButton.setText("Clear")

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
        self.waitingWidget.setText("Input a keyword to search")
        self.waitingWidget.setFont(STANDARD_HUGE_FONT)
        self.waitingWidget.setAlignment(Qt.AlignCenter)
        self.noResultWidget = BodyLabel(self)
        self.noResultWidget.setText("Oops! No results found.")
        self.noResultWidget.setFont(STANDARD_HUGE_FONT)
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

        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop, 1)
        self.vBoxLayoutMain.addWidget(self.separator_horiz_top)
        self.vBoxLayoutMain.addWidget(self.waitingWidget, 1)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle, 1)

        self.resultTable.setVisible(False)
        self.noResultWidget.setVisible(False)

        keyboard.add_hotkey("enter", self.search)
        self.query_result = None
        self.detail_result = None
        self.searchButton.clicked.connect(self.search)
        self.clearButton.clicked.connect(self.clear)
        self.resultTable.cellClicked.connect(self.show_detail)
        self.downloadButton.clicked.connect(self.download_file)
        self.visitPageButton.clicked.connect(self.open_link)

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
            filename = self.config["runtime"]["detail_img"]
            utils.Download.download_file(self.query_result[row][2], filename)
            pic.load(filename)
        else:
            self.detail_result = [name, self.query_result[row][1], "No Info",
                                  "No Info\n**This is an archived Trainer**", "Before 2019-05"]
            pic.load(self.config["runtime"]["blank_img"])
            self.visitPageButton.setDisabled(True)
        content = f"Name: {name}\nLatest File: {self.detail_result[0]}\nSize: {self.detail_result[2]}\nDate: {self.detail_result[4]}\nDownloads: {self.detail_result[3]}"
        self.detailLabel.setText(content)
        self.detailLabel.setFont(STANDARD_FONT)
        self.detailImage.setImage(pic)
        self.detailImage.setFixedSize(250, 250)
        self.check_download(name)
        self.resultTable.resizeColumnsToContents()

    def download_file(self):
        print("Downloading", self.detail_result[1])
        if ".rar" in self.detail_result[1]:
            file_name = self.config["download"]["path"] + self.detail_result[0] + ".rar"
        else:
            file_name = self.config["download"]["path"] + self.detail_result[0] + ".zip"
        print(file_name)
        utils.Download.download_file(self.detail_result[1], file_name)
        print("Download Completed.")
        if self.config["download"]["extract"]:
            flag = utils.Download.extract_file(file_name)
            if flag == -1:
                print("WinRAR is probably not installed or added to PATH, cannot proceed extraction.")
            else:
                print("Extraction Completed.")
                os.remove(file_name)
        self.verify_download()

    def search(self):
        if self.searchLine.text() == "":
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
            item.setFont(STANDARD_FONT)
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

    def verify_download(self):
        data = self.data
        name = self.detail_result[0]
        print("VRF: NAME:", name)
        for original_file in os.listdir(self.config["download"]["path"]):
            name = name.replace(".", "").replace("-FLiNG", "").replace(" ", "")
            file = original_file.replace(" ", "").replace(".", "")
            if name in file:
                self.downloadButton.setIcon(FIF.COMPLETED)
                self.downloadButton.setText("Downloaded")
                self.downloadButton.setDisabled(True)
                if self.config["cache"]["detail_image"]:
                    pic_name = "./img_cache/" + utils.File.string_valid(
                        self.resultTable.item(self.row, 0).text()) + "-image.jpg"
                    if self.query_result[self.row][-1] == "COMMON":
                        register = [self.resultTable.item(self.row, 0).text(),
                                    data["config"]["download"]["path"] + original_file,
                                    time.strftime('%Y-%m-%d', time.localtime()), pic_name, "COMMON",
                                    self.query_result[self.row][1],
                                    "VERIFIED"]
                    else:
                        register = [self.resultTable.item(self.row, 0).text(),
                                    data["config"]["download"]["path"] + original_file,
                                    time.strftime('%Y-%m-%d', time.localtime()), pic_name, "ARCHIVED", "NONE",
                                    "VERIFIED"]
                    try:
                        os.rename("./img_cache/image.jpg", pic_name)
                    except FileExistsError:
                        pass
                    data["files"]["downloaded"].append(register)
                    print("Registered:", register)
                    utils.Data.json_write("./data/data.json", data)
                return None
        self.downloadButton.setIcon(FIF.DOWNLOAD)
        self.downloadButton.setText("Download")
        self.downloadButton.setDisabled(False)

    def check_download(self, name):
        for downloaded in self.data["files"]["downloaded"]:
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
        self.data = utils.Data.json_read("data\\data.json")
        self.setObjectName("Library")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.vBoxLayoutMiddle = QVBoxLayout(self)
        self.hBoxLayoutMiddle = QHBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.vBoxLayoutMiddle.setSpacing(10)

        self.searchLine = LineEdit(self)
        self.searchLine.setAlignment(Qt.AlignCenter)
        self.searchLine.setFixedWidth(300)
        self.searchButton = PrimaryPushButton(self)
        self.searchButton.setIcon(FIF.SEARCH)
        self.searchButton.setText("Search")

        self.clearButton = PushButton(self)
        self.clearButton.setIcon(FIF.UPDATE)
        self.clearButton.setText("Refresh")

        self.resultLabel = BodyLabel(self)
        self.resultLabel.setText("")

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
        self.waitingWidget.setFont(STANDARD_HUGE_FONT)
        self.waitingWidget.setAlignment(Qt.AlignCenter)
        self.noResultWidget = BodyLabel(self)
        self.noResultWidget.setText("Oops! No results found.")
        self.noResultWidget.setFont(STANDARD_HUGE_FONT)
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

        self.hBoxLayoutTop.addWidget(self.searchLine, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.searchButton, 1, Qt.AlignLeft)
        self.hBoxLayoutTop.addWidget(self.resultLabel, 1, Qt.AlignLeft)
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

        self.vBoxLayoutMain.addLayout(self.hBoxLayoutTop, 1)
        self.vBoxLayoutMain.addWidget(self.separator_horiz_top)
        self.vBoxLayoutMain.addWidget(self.waitingWidget, 1)
        self.vBoxLayoutMain.addWidget(self.noResultWidget, 1)
        self.vBoxLayoutMain.addLayout(self.hBoxLayoutMiddle, 1)

        self.resultTable.cellClicked.connect(self.show_detail)
        self.resultTable.cellDoubleClicked.connect(self.run_trainer)
        self.clearButton.clicked.connect(self.table_default)
        self.runButton.clicked.connect(self.run_trainer)
        self.deleteButton.clicked.connect(self.remove_file)
        self.visitPageButton.clicked.connect(self.open_link)
        # self.resultTable.setVisible(False)
        self.table_default()
        self.noResultWidget.setVisible(False)

    def run_trainer(self):
        subprocess.run(self.current_exe, check=False, shell=True, close_fds=True, creationflags=0x00000008)

    def open_link(self):
        link = self.data["files"]["downloaded"][self.row][4]
        if link != "NONE":
            webbrowser.open(link)

    def remove_file(self):
        mbox = MessageBox("Warning", "Are you sure you want to delete this file? This operation is irreversible.", self)
        mbox.yesButton.setText('Confirm')
        mbox.cancelButton.setText('Cancel')
        if mbox.exec():
            os.remove(self.current_exe)
            os.remove(self.file_name_list[self.row][3])
            del self.file_name_list[self.row]
            self.data["files"]["downloaded"] = self.file_name_list
            utils.Data.json_write("./data/data.json", self.data)
            self.table_default()

    def table_default(self):
        self.data = utils.Data.json_read("data\\data.json")
        self.separator_vertical_middle.setVisible(False)
        self.detailImage.setVisible(False)
        self.detailLabel.setVisible(False)
        self.runButton.setVisible(False)
        self.visitPageButton.setVisible(False)
        self.deleteButton.setVisible(False)
        self.updateButton.setVisible(False)
        self.resultTable.setVisible(True)
        file_name_list = self.data["files"]["downloaded"]
        self.file_name_list = file_name_list
        if self.data["config"]["library"]["filter"] == "VERIFIED_ONLY":
            if len(file_name_list) <= 0:
                self.resultTable.setVisible(False)
                self.waitingWidget.setVisible(True)
                self.waitingWidget.setText("No downloaded trainers found.")
                return None
        else:
            for temp_file in os.listdir(self.data["config"]["download"]["path"]):
                if temp_file not in file_name_list:
                    file_name_list.append([temp_file, "UNKNOWN", "UNKNOWN", "UNVERIFIED"])
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
        if self.file_name_list[row][-1] == "VERIFIED":
            pic_file = self.file_name_list[row][3]
            pic.load(pic_file)
            content = f"Name: {self.file_name_list[row][0]}\nDownload Time: {self.file_name_list[row][2]}"
        else:
            content = f"File: {self.file_name_list[row][0]}\n**[WARNING]This file hasn't been verified.**"
            pic.load(self.data["config"]["runtime"]["blank_img"])
            self.visitPageButton.setDisabled(True)
            self.updateButton.setDisabled(True)
        if self.file_name_list[row][-3] != "COMMON":
            self.visitPageButton.setDisabled(True)
            self.updateButton.setDisabled(True)
            content += "\n**This is an archived Trainer**"
        self.detailLabel.setText(content)
        self.detailLabel.setFont(STANDARD_FONT)
        self.detailImage.setImage(pic)
        self.detailImage.setFixedSize(250, 250)
        self.current_exe = self.file_name_list[row][1]
        self.resultTable.resizeColumnsToContents()

    def search(self):
        pass

    def fill_table(self, table):
        count = len(table)
        self.waitingWidget.setVisible(False)
        self.resultTable.setRowCount(count)
        self.resultTable.clear()
        if count == 0:
            self.noResultWidget.setVisible(True)
            return None
        for row in range(count):
            item = QTableWidgetItem()
            item.setText(table[row][0])
            item.setFont(STANDARD_FONT)
            if table[row][-1] == "UNVERIFIED":
                item.setForeground(QBrush(Qt.gray))
            self.resultTable.setItem(row, 0, item)
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class SettingWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.resize(400, 400)
        self.config = utils.Data.json_read("data\\data.json")["config"]
        # self.data = utils.Data.json_read("./data/data.json")
        self.setObjectName("Setting")
        self.vBoxLayoutMain = QVBoxLayout(self)
        self.hBoxLayoutTop = QHBoxLayout(self)
        self.vBoxLayoutMain.setContentsMargins(30, 60, 30, 50)
        self.vBoxLayoutMain.setSpacing(30)
        self.hBoxLayoutTop.setSpacing(20)
        self.title_label = QLabel("Settings", self)
        self.title_label.setFont(STANDARD_HUGE_FONT)
        self.horiz_seperator_1 = HorizontalSeparator(self)
        self.vBoxLayoutMain.addWidget(self.title_label)
        self.vBoxLayoutMain.addWidget(self.horiz_seperator_1)


class HelpingWidget(QFrame):
    pass


class AvatarWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage('resource/iconC.png').scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

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
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, 'Dev')


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
        self.settingInterface = SettingWidget(self)
        self.helpingInterface = Widget('Help Interface', self)
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
        self.addSubInterface(self.libraryInterface, FIF.APPLICATION, 'My Trainers')
        self.navigationInterface.addSeparator()
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
        self.setWindowIcon(QIcon('resource/iconC.png'))
        self.setWindowTitle('Trainer Manager')
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
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())

    def showMessageBox(self):
        w = MessageBox("Version Info", "ver 0.0.2 Alpha", self)
        w.yesButton.setText('Yes')
        w.cancelButton.setText('No')

        if w.exec():
            QDesktopServices.openUrl(QUrl())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


def exit_handler():
    try:
        os.remove("./img_cache/image.jpg")
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    atexit.register(exit_handler)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
