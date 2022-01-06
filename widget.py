# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import *
from PySide6.QtGui import QColor, QGuiApplication, QPixmap, QAction, QIcon, QMouseEvent, QPaintEvent, QPainter, QPen, \
    QCursor, QScreen, QShortcut, QKeySequence
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QFileDialog, QPushButton

grey_color = QColor(0, 0, 0, 255)
white_color = QColor(60, 60, 60, 20)
brush_color = QColor(128, 128, 255, 100)


class ScreenShotWidget(QWidget):
    def __init__(self, app: QApplication, width: float, height: float):
        self.deviceWidth = width
        self.deviceHeight = height
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
        self.moveX = self.moveY = .0
        self.isPopup = False
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

        self.exitShortCut = QShortcut(QKeySequence("Escape"), self)
        self.exitShortCut.activated.connect(self.escEvent)
        self.isMove = False

    @Slot()
    def escEvent(self):
        self.beginX = self.beginY = self.endX = self.endY = .0
        self.update()
        self.hide()

    def paintEvent(self, e: QPaintEvent) -> None:
        self.setWindowOpacity(.3)
        qp = QPainter(self)
        qp.setPen(QPen(QColor(255, 0, 0, 0), 3))
        qp.setBrush(brush_color)
        rect = QRectF(self.beginX, self.beginY, self.endX - self.beginX, self.endY - self.beginY)
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

    @Slot()
    def saveToFile(self):
        self.setWindowOpacity(0)
        screen = QGuiApplication.primaryScreen()
        re = self.computeRect()
        x = re[0]
        y = re[1]
        xDis = re[2]
        yDis = re[3]
        pix = screen.grabWindow(0, x, y, xDis, yDis)
        self.hide()
        # set default filename
        filename = QDateTime.currentDateTime().toString("yyyy-MM-dd-HH-mm-ss")

        pix.save(filename + ".png", "png")
        self.isPopup = False
        self.beginY = self.beginX = self.endY = self.endX = 0
        self.update()
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.hide()

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
            self.isMove = False
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

    def swap(self):
        if self.endX < self.beginX:
            t = self.endX
            self.endX = self.beginX
            self.beginX = t
        if self.endY < self.beginY:
            t = self.endY
            self.endY = self.beginY
            self.beginY = t

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if self.isMove:
            x = e.position().x()
            y = e.position().y()
            xDis = x - self.moveX
            yDis = y - self.moveY
            if self.beginX + xDis >= 0 and self.beginY + yDis >= 0 \
                    and self.endX + xDis <= self.deviceWidth and \
                    self.endY + yDis <= self.deviceHeight:
                self.beginX += xDis
                self.beginY += yDis
                self.endX += xDis
                self.endY += yDis
            elif self.beginX + xDis < 0:
                self.beginX = 0
            elif self.endX + xDis > self.deviceWidth:
                self.endX = self.deviceWidth
            elif self.beginY + yDis < 0:
                self.beginY = 0
            elif self.endY + yDis > self.deviceHeight:
                self.endY = self.deviceHeight
            self.moveX = x
            self.moveY = y
            self.update()

        elif not self.isReleased:
            self.endX = e.position().x()
            self.endY = e.position().y()
            self.update()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and not self.isPopup:
            self.isReleased = False
            self.swap()
            if self.beginX <= e.position().x() <= self.endX and self.beginY <= e.position().y() <= self.endY:
                if not self.isMove:
                    self.isMove = True
                    self.moveX = e.position().x()
                    self.moveY = e.position().y()
                    # print(self.moveX, self.moveY)

            else:
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


@Slot()
def showScreenShotWindow():
    window.show(), QApplication.setOverrideCursor(Qt.CrossCursor)


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

    curr_size = QApplication.primaryScreen().size()
    window = ScreenShotWidget(app, curr_size.width(), curr_size.height())
    showWindow.triggered.connect(showScreenShotWindow)

    # showWindow.setShortcut(QKeySequence("Ctrl+Shift+A"))

    window.resize(curr_size.width(), curr_size.height())
    mainWindow = MainWindow(window)
    window.hide()
    mainWindow.show()
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    sys.exit(app.exec())
