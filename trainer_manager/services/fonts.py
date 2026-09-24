"""Font helpers, extracted without changing behavior."""

from PyQt5.QtGui import QFont


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
