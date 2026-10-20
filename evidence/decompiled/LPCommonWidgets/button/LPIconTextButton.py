# Source Generated with Decompyle++
# File: LPIconTextButton.pyc (Python 3.9)

'''
@Time ： 2025/9/30 14:29
@Auth ： Chris
@File ：LPIconTextButton.py
@Desc:
'''
from PyQt6.QtCore import QRect, Qt, QSize
from PyQt6.QtGui import QPainter, QPalette, QColor, QFontMetrics, QPixmap, QFont
from PyQt6.QtWidgets import QPushButton, QStyleOptionButton, QStyle
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import Main_Text

class LPIconTextButton(QPushButton):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.defaultPixmap = None
        self.checkedPixmap = None
        self.spacing = 5
        self.text = ''
        self.hovered = False
        self.setCheckable(True)

    
    def setSpacing(self, spacing):
        self.spacing = spacing

    
    def setText(self, text):
        self.text = text
        self.update()

    
    def setImage(self, defaultPixmap, checkedPixmap):
        self.defaultPixmap = defaultPixmap
        self.checkedPixmap = checkedPixmap
        self.update()

    
    def enterEvent(self, event):
        self.hovered = True
        self.update()

    
    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        if self.isChecked():
            bg_color = QColor(255, 255, 255)
            pixmap = self.checkedPixmap
        else:
            bg_color = QColor(0, 0, 0, 0)
            pixmap = self.defaultPixmap
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        if self.isChecked():
            text_color = QColor(0, 0, 0)
        else:
            text_color = QColor(255, 255, 255, 166)
        content_width = 0
        iconSize = self.iconSize()
        if not pixmap:
            return None
        scaledPixmap = None.scaled(iconSize.width(), iconSize.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        font = QFont()
        font.setPointSizeF(Main_Text)
        painter.setFont(font)
        fm = QFontMetrics(font)
        textWidth = fm.horizontalAdvance(self.text) if self.text else 0
        if self.defaultPixmap and self.text:
            content_width = iconSize.width() + self.spacing + textWidth
        else:
            content_width = iconSize.width() + textWidth
        x = (self.width() - content_width) // 2
        y = (self.height() - fm.height()) // 2
        if self.defaultPixmap:
            icon_y = (self.height() - iconSize.height()) // 2
            painter.drawPixmap(x, icon_y, scaledPixmap)
            x += iconSize.width() + self.spacing
        if self.text:
            text_rect = QRect(x, y, textWidth, fm.height())
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self.text)

    __classcell__ = None

