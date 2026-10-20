# Source Generated with Decompyle++
# File: LPSuperTableWidget.pyc (Python 3.9)

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, QEvent
import LPGlobalUI

class LPSuperTableWidgetDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.hovered_row = -1

    
    def onHoverIndexChanged(self, item):
        self.hovered_row = item.row()

    
    def onLeaveTableEvent(self):
        self.hovered_row = -1

    
    def paint(self = None, painter = None, option = None, index = None):
        opt = option
        if index.row() == self.hovered_row:
            painter.fillRect(option.rect, LPGlobalUI.THEME_DISABLE_COLOR)
        super().paint(painter, opt, index)

    __classcell__ = None


class LPSuperTableWidget(QTableWidget):
    hoverIndexChanged = pyqtSignal(object)
    leaveTableEvent = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.setMouseTracking(True)

    
    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos())
        self.hoverIndexChanged.emit(index)

    
    def leaveEvent(self, event):
        self.leaveTableEvent.emit()
        self.viewport().update()

    
    def eventFilter(self = None, source = None, event = None):
        if event.type() == QEvent.Type.Enter:
            index = self.indexAt(source.pos())
            self.hoverIndexChanged.emit(index)
            return True
        if None.type() == QEvent.Type.Leave:
            self.leaveTableEvent.emit()
            self.viewport().update()
            return True
        return None().eventFilter(source, event)

    __classcell__ = None

