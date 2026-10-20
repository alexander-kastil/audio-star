# Source Generated with Decompyle++
# File: LPMinibarCoverButton.pyc (Python 3.9)

'''
@Time ： 2025/9/26 10:01
@Auth ： Chris
@File ：LPMinibarCoverButton.py
@Desc:
'''
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtWidgets import QPushButton, QLabel, QStyleOptionButton, QStyle
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class LPMinibarCoverButton(QPushButton):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self._hover = False
        self.setStyleSheet('\n                    QPushButton {\n                        border: none;\n                        background: transparent;\n                    }\n                    QPushButton:hover {\n                        background-color: rgba(0, 0, 0, 100);\n                    }\n                ')

    
    def enterEvent(self, event):
        self._hover = True
        self.update()

    
    def leaveEvent(self, event):
        self._hover = False
        self.update()

    
    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        painter = QPainter(self)
        self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
        if LPGlobalUI.mainWindow.isFullScreen():
            return None
        if None._hover:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 147))
            size = 20
            rect = self.rect().adjusted((self.width() - size) // 2, (self.height() - size) // 2, -(self.width() - size) // 2, -(self.height() - size) // 2)
            if LPGlobalUI.mainWindow.isPlayViewShow:
                arrowPixmap = QPixmap(LPGlobalUI.imagePath('miniBar/cover_arrow_down.png'))
            else:
                arrowPixmap = QPixmap(LPGlobalUI.imagePath('miniBar/cover_arrow_up.png'))
            painter.drawPixmap(rect, arrowPixmap)

    __classcell__ = None

