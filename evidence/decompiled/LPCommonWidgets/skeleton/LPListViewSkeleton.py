# Source Generated with Decompyle++
# File: LPListViewSkeleton.pyc (Python 3.9)

'''
@Time ： 2025/1/16 17:20
@Auth ： Chris
@File ：LPListViewSkeleton.py
@Desc:
'''
from PyQt6.QtCore import QAbstractListModel, Qt, QSize, QRectF, QTimer, QRect
from PyQt6.QtGui import QBrush, QPainterPath, QColor, QLinearGradient
from PyQt6.QtWidgets import QStyledItemDelegate
import LPGlobalUI

class LPListViewSkeletonListModel(QAbstractListModel):
    
    def __init__(self = None, num = None, parent = None):
        super().__init__(parent)
        self._data = [
            'simulate'] * num

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            return self._data

    __classcell__ = None


class LPListViewSkeletonDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None, config = None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.list_view = parent.listView
        self.gradient_pos = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(30)

    
    def update_animation(self):
        self.gradient_pos += 0.05
        if self.gradient_pos > 1:
            self.gradient_pos = 0
        if self.list_view:
            self.list_view.viewport().update()

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QSize(self.config.width, self.config.height)
        return result

    
    def paint(self, painter, option, index):
        data = index.data()
        if data is None:
            return None
        cellRect = None.rect
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QPainterPath()
        path.addRoundedRect(QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        gradient = QLinearGradient(cellRect.left(), cellRect.top(), cellRect.right(), cellRect.top())
        gradient.setColorAt(max(0, self.gradient_pos - 0.5), QColor(30, 30, 30))
        gradient.setColorAt(max(0, self.gradient_pos - 0.2), QColor(33, 33, 33))
        gradient.setColorAt(min(1, self.gradient_pos), QColor(36, 36, 36))
        gradient.setColorAt(min(1, self.gradient_pos + 0.5), QColor(40, 40, 40))
        painter.fillRect(cellRect, gradient)
        painter.restore()

    __classcell__ = None


class LPListViewSkeletonDelegateWithSize(QStyledItemDelegate):
    
    def __init__(self = None, listView = None, width = None, height = None):
        super().__init__(listView)
        self.list_view = listView
        self.width = width
        self.height = height
        self.gradient_pos = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)

    
    def update_animation(self):
        self.gradient_pos += 0.05
        if self.gradient_pos > 1:
            self.gradient_pos = 0
        if self.list_view:
            self.list_view.viewport().update()

    
    def startAnimation(self):
        if self.animation_timer:
            self.animation_timer.start(30)

    
    def stopAnimation(self):
        if self.animation_timer:
            self.animation_timer.stop()

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QSize(self.width, self.height)
        return result

    
    def paint(self, painter, option, index):
        data = index.data()
        if data is None:
            return None
        cellRect = None.rect
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QPainterPath()
        path.addRoundedRect(QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        gradient = QLinearGradient(cellRect.left(), cellRect.top(), cellRect.right(), cellRect.top())
        gradient.setColorAt(max(0, self.gradient_pos - 0.5), QColor(30, 30, 30))
        gradient.setColorAt(max(0, self.gradient_pos - 0.2), QColor(33, 33, 33))
        gradient.setColorAt(min(1, self.gradient_pos), QColor(36, 36, 36))
        gradient.setColorAt(min(1, self.gradient_pos + 0.5), QColor(40, 40, 40))
        painter.fillRect(cellRect, gradient)

    __classcell__ = None

