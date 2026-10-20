# Source Generated with Decompyle++
# File: LPTableViewSkeleton.pyc (Python 3.9)

'''
@Time ： 2025/6/12 13:49
@Auth ： Chris
@File ：LPTableViewSkeleton.py
@Desc:
'''
from PyQt6.QtCore import Qt, QRect, QAbstractTableModel, pyqtProperty, QPropertyAnimation
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
import LPGlobalUI

class LPTableViewSkeletonTableModel(QAbstractTableModel):
    
    def __init__(self = None, rowCount = None, columnCount = None, parent = None):
        super().__init__(parent)
        self.colCount = columnCount
        self._data = [
            'simulate'] * rowCount

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def columnCount(self, parent = (None,)):
        return self.colCount

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            return self._data

    __classcell__ = None


class LPTableViewSkeletonDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None, hasImage = None):
        super().__init__(parent)
        self.hasImage = hasImage
        self._offset = 0
        self.animation = QPropertyAnimation(self, b'offset')
        self.animation.setStartValue(0)
        self.animation.setEndValue(300)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)

    
    def startAnimation(self):
        self.animation.start()

    
    def stopAnimation(self):
        if self.animation:
            self.animation.stop()

    
    def get_offset(self):
        return self._offset

    
    def set_offset(self, value):
        self._offset = value
        if self.parent():
            self.parent().viewport().update()

    offset = pyqtProperty(int, get_offset, set_offset, **('fget', 'fset'))
    
    def paint(self, painter, option, index):
        option.state &= ~(QStyle.StateFlag.State_MouseOver)
        option.state &= ~(QStyle.StateFlag.State_Selected)
        cellRect = option.rect
        painter.setBrush(QBrush(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if index.column() == 0:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        elif index.column() == 1:
            leftX = 57
            rect = QRect(cellRect.x() + leftX, cellRect.y() + 12, cellRect.width() - leftX, cellRect.height() - 24)
            radius = 10
        elif index.column() == 2:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        elif index.column() == 3:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        elif index.column() == 4:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        elif index.column() == 5:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        elif index.column() == 6:
            radius = 10
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
        gradient = QLinearGradient(rect.x() + self._offset - 150, rect.y(), rect.x() + self._offset + 150, rect.y())
        gradient.setColorAt(0, QColor(72, 72, 72))
        gradient.setColorAt(0.25, QColor(90, 90, 90))
        gradient.setColorAt(0.5, QColor(110, 110, 110))
        gradient.setColorAt(0.75, QColor(90, 90, 90))
        gradient.setColorAt(1, QColor(72, 72, 72))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)

    __classcell__ = None

