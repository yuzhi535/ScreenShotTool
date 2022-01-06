# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import *
from PySide6.QtGui import QColor, QGuiApplication, QPixmap, QAction, QIcon, QMouseEvent, QPaintEvent, QPainter, QPen, \
    QCursor, QScreen, QShortcut, QKeySequence
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QFileDialog, QPushButton

grey_color = QColor(0, 0, 0, 200)
white_color = QColor(160, 160, 160, 200)
brush_color = QColor(128, 128, 255, 100)


class ScreenShotWidget(QWidget):
    def __init__(self, app: QApplication, width: int, height: int):
        super(ScreenShotWidget, self).__init__()
        self.setGeometry(0, 0, width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.label = QLabel(parent=self)
        self.canvas = QPixmap(width, height)
        self.canvas.fill(white_color)
        self.label.setPixmap(self.canvas)
        self.isReleased = True
        self.beginX = .0
        self.beginY = .0
        self.endX = .0
        self.endY = .0
        self.isPopup = False
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

    def paintEvent(self, e: QPaintEvent) -> None:
        self.setWindowOpacity(.3)
        qp = QPainter(self)
        qp.setPen(QPen(QColor('green'), 3))
        qp.setBrush(brush_color)
        rect = QRectF(self.beginX, self.beginY, self.endX -
                      self.beginX, self.endY - self.beginY)
        qp.drawRect(rect)
        qp.fillRect(rect, grey_color)

    def computeRect(self):
        x = min(self.beginX, self.endX)
        y = min(self.beginY, self.endY)
        xDis = abs(self.endX - self.beginX)
        yDis = abs(self.endY - self.beginY)
        return x, y, xDis, yDis

    @Slot()
    def shot(self):
        self.isPopup = False
        self.setWindowOpacity(0)
        screen = QApplication.primaryScreen()
        re = self.computeRect()
        x = re[0]
        y = re[1]
        xDis = re[2]
        yDis = re[3]
        pix = screen.grabWindow(0, x, y, xDis, yDis)
        QApplication.clipboard().setPixmap(pix)

        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.isPopup = False
        self.beginY = self.beginX = self.endY = self.endX = 0
        self.update()
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.hide()

    @Slot()
    def exit(self):
        self.isPopup = False
        self.beginY = self.beginX = self.endY = self.endX = 0
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.hide()

    def mouseMoveEvent(self, e: QMouseEvent):
        if not self.isReleased:
            self.endX = e.position().x()
            self.endY = e.position().y()
            self.update()

    @Slot()
    def saveToFile(self):
        self.setWindowOpacity(0)
        screen = QApplication.primaryScreen()
        re = self.computeRect()
        x = re[0]
        y = re[1]
        xDis = re[2]
        yDis = re[3]
        pix = screen.grabWindow(0, x, y, xDis, yDis)
        self.hide()
        # set default filename
        filename, _ = QFileDialog.getSaveFileName(self, caption="choose location and file name",
                                                  dir=QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"),
                                                  filter="PNG(*.png);; JPEG(*.jpg)")

        if filename[-3:] == "png":
            pix.save(filename, "png")
        elif filename[-3:] == "jpg":
            pix.save(filename, "jpg")
        self.beginY = self.beginX = self.endY = self.endX = 0
        self.update()
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.isPopup = False

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
            popup_menu = QMenu(self)
            saveClip = QAction("save to clipboard", self)
            saveFile = QAction("save", self)
            exit = QAction("exit", self)
            saveClip.triggered.connect(self.shot)
            exit.triggered.connect(self.exit)
            saveFile.triggered.connect(self.saveToFile)
            popup_menu.addAction(saveClip)
            popup_menu.addAction(saveFile)
            popup_menu.addAction(exit)
            popup_menu.popup(QCursor.pos())
            self.isPopup = True
        else:
            self.isReleased = True
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and not self.isPopup:
            self.isReleased = False
            self.endX = self.beginX = e.position().x()
            self.endY = self.beginY = e.position().y()
            self.update()
        self.isPopup = False


class MainWindow(QWidget):
    def __init__(self, window):
        super(MainWindow, self).__init__()
        self.rectBtn = QPushButton("rect shot", self)
        self.rectBtn.show()
        self.screenWindow = window
        self.rectBtn.clicked.connect(self.showWindow)

    @Slot()
    def showWindow(self):
        self.screenWindow.show()
        self.window().hide()
        QApplication.setOverrideCursor(Qt.CrossCursor)


if __name__ == "__main__":
    app = QApplication([])
    icon = QIcon("./assets/img/icon.png")
    tray = QSystemTrayIcon(icon, app)
    tray.setVisible(True)

    menu = QMenu()
    showWindow = QAction("show the window")
    exitApp = QAction("Exit")
    menu.addAction(showWindow)
    menu.addAction(exitApp)

    exitApp.triggered.connect(lambda: QApplication.exit(0))

    tray.setContextMenu(menu)
    tray.show()

    curr_size = QGuiApplication.primaryScreen().size()
    window = ScreenShotWidget(app, curr_size.width(), curr_size.height())
    showWindow.triggered.connect(
        lambda: (window.show(), QApplication.setOverrideCursor(Qt.CrossCursor)))

    showWindow.setShortcut(QKeySequence("Ctrl+Shift+A"))

    window.resize(curr_size.width(), curr_size.height())
    mainWindow = MainWindow(window)
    window.hide()
    mainWindow.show()
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    sys.exit(app.exec())
