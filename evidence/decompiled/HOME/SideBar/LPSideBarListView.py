# Source Generated with Decompyle++
# File: LPSideBarListView.pyc (Python 3.9)

'''
@Time ： 2025/12/29 13:26
@Auth ： Chris
@File ：LPSideBarListView.py
@Desc:
'''
from PyQt6.QtCore import Qt, QAbstractListModel, QSize, QRectF, QRect, QEvent
from PyQt6.QtGui import QPainter, QBrush, QColor, QPainterPath, QIcon, QPixmap, QFont, QLinearGradient
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import Sub_Text

def paintSideBarSelectedBackground(painter, cellRect):
    '''
    绘制侧边栏条目的选中高亮背景。

    参数:
        painter: 当前条目绘制使用的 QPainter。
        cellRect: 当前条目的绘制区域。
    返回值:
        None。
    '''
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    highlightPath = QPainterPath()
    highlightPath.addRoundedRect(QRectF(cellRect), 8, 8)
    highlightStartColor = QColor(LPGlobalUI.THEME_ACCENT_COLOR)
    highlightStartColor.setAlpha(51)
    highlightEndColor = QColor(LPGlobalUI.THEME_ACCENT_COLOR)
    highlightEndColor.setAlpha(15)
    gradient = QLinearGradient(cellRect.left(), cellRect.top(), cellRect.right(), cellRect.top())
    gradient.setColorAt(0, highlightStartColor)
    gradient.setColorAt(1, highlightEndColor)
    painter.fillPath(highlightPath, QBrush(gradient))
    painter.save()
    painter.setClipPath(highlightPath)
    painter.fillRect(QRect(cellRect.x(), cellRect.y(), 3, cellRect.height()), LPGlobalUI.THEME_ACCENT_COLOR)
    painter.restore()


class LPSideBarListModel(QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        '''
        初始化普通侧边栏列表模型。

        参数:
            data: 侧边栏条目数据列表。
            parent: Qt 父对象。
        返回值:
            None。
        '''
        super().__init__(parent)
        self._data = data

    
    def rowCount(self, parent = (None,)):
        '''
        获取侧边栏条目数量。

        参数:
            parent: Qt 模型父索引。
        返回值:
            int: 当前数据条目数量。
        '''
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        '''
        获取指定索引和角色的数据。

        参数:
            index: Qt 模型索引。
            role: Qt 数据角色。
        返回值:
            object: 当前条目数据；无效时返回 None。
        '''
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        item = None._data[row]
        if role == Qt.ItemDataRole.DisplayRole:
            return item

    __classcell__ = None


class LPSideBarListDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None):
        '''
        初始化普通侧边栏列表条目绘制代理。

        参数:
            parent: 代理绑定的列表视图。
        返回值:
            None。
        '''
        super().__init__(parent)
        self.listview = parent
        self.listview.setMouseTracking(True)
        self.listview.viewport().installEventFilter(self)

    
    def eventFilter(self = None, watched = None, event = None):
