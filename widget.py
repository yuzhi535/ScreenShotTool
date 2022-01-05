# This Python file uses the following encoding: utf-8
import sys
from typing_extensions import ParamSpec
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtGui import QRgba64, QScreen, QGuiApplication, QPainter, QPixmap
from PySide6 import QtCore

grey_color = "#bdc3c7"
white_color = QRgba64.fromRgba64(0, 250, 0, 1.0)


class ScreenShotWidget(QWidget):
    def __init__(self, app: QApplication, width: int, height: int):
        super().__init__()
        self.label = QLabel(parent=self)
        self.canvas = QPixmap(width, height)
        self.canvas.fill(white_color)
        print(self.canvas.hasAlpha())
        self.label.setPixmap(self.canvas)

    @QtCore.Slot()
    def shot(self, x: int, y: int, width: int, height: int):
        screen = QGuiApplication.primaryScreen()
        self.pixmap = screen.grabWindow(0)


if __name__ == "__main__":
    app = QApplication([])
    curr_size = QGuiApplication.primaryScreen().size()
    window = ScreenShotWidget(app, curr_size.width(), curr_size.height())
    # window.showFullScreen()
    window.resize(curr_size.width(), curr_size.height())
    window.show()
    sys.exit(app.exec())
