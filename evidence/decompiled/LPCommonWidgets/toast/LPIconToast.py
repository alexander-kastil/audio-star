# Source Generated with Decompyle++
# File: LPIconToast.pyc (Python 3.9)

'''
@Time ： 2025/5/12 10:00
@Auth ： Chris
@File ：LPIconToast.py
@Desc:
'''
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget
import LPGlobalUI

class IconToast(QWidget):
    
    def __init__(self = None, iconPath = None, titleText = None, tipText = None, parent = None, timeout = None):
        super().__init__(parent)
        self.iconPath = iconPath
        self.titleText = titleText
        self.tipText = tipText
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        self.timeout = timeout * 1000

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet('\n                QFrame#mainFrame{\n                    border: 1px solid #FF878A;\n                    border-radius: 12px;\n                    background-color: #FFE4E5;\n                }\n                QFrame {\n                    border: none;\n                    background-color: transparent;\n                }\n                QLabel#titleLabel {\n                    color: rgba(0,0,0,191);\n                    background-color: transparent;\n                }\n                QLabel#tipLabel {\n                    color: rgba(0,0,0,166);\n                    background-color: transparent;\n                }\n                QPushButton#closeButton {\n                    background-color: transparent;\n                }\n                }\n                ')
        self.closeButton.hide()
        self.titleLabel.setText(self.titleText)
        self.tipLabel.setText(self.tipText)
        scaled = QPixmap(self.iconPath).scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.imageLabel.setPixmap(scaled)

    
    def showToast(self):
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + 70
            self.move(QPoint(x, y))
        self.timer.start(self.timeout)
        self.raise_()
        self.show()

    __classcell__ = None

