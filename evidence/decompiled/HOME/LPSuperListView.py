# Source Generated with Decompyle++
# File: LPSuperListView.pyc (Python 3.9)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QTimer
import math

class LPSuperListView(QListView):
    resizeSignal = pyqtSignal()
    visibleRowsChanged = pyqtSignal(int, int)
    
    def __init__(self = None, parent = None):
        '''
        初始化增强列表视图，并绑定滚动与可见区监听状态。

        参数:
            parent (QWidget): 父级控件。
        返回:
            无
        '''
        super(LPSuperListView, self).__init__(parent)
        self.setMouseTracking(True)
        self.lastCursorPos = None
        self.lastCursorActionIndex = None
        self.showAllItems = False
        self.maxContentHeight = 0
        self._lastVisibleRows = (-2, -2)
        self.verticalScrollBar().valueChanged.connect(self._scrollValueChanged)
        self.verticalScrollBar().rangeChanged.connect(self._scrollRangeChanged)

    
    def setupUI(self):
        '''
        初始化列表默认样式。

        参数:
            无
        返回:
            无
        '''
        self.setStyleSheet('QListView{border:none;}\nQListView::item {color: rgb(108,108,108)}\nQScrollBar {\n        border: 0px;\n        background: transparent;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle:vertical {\n        background: rgb(82,82,82);\n        min-height: 30px;\n\tborder-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        border: 0px;\n}\nQHeaderView::section {\nbackground-color: transparent;\ncolor: white;\n}\n')

    
    def mouseMoveEvent(self = None, event = None):
        '''
        处理鼠标移动事件，并刷新当前悬停索引。

        参数:
            event (QMouseEvent): Qt 鼠标事件对象。
        返回:
            无
        '''
        super().mouseMoveEvent(event)
        self.lastCursorPos = event.pos()
        index = self.indexAt(self.lastCursorPos)
        self.update(index)

    
    def setModel(self = None, model = None):
        '''
        设置列表模型，并在模型切换后刷新内容高度与可见区。

        参数:
            model (QAbstractItemModel | None): 新模型对象。
        返回:
            无
        '''
        super().setModel(model)
        self._lastVisibleRows = (-2, -2)
        self.updateContentHeight()
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def showEvent(self = None, event = None):
        '''
        处理控件显示事件，并刷新当前可见区。

        参数:
            event (QShowEvent): Qt 显示事件对象。
        返回:
            无
        '''
        super().showEvent(event)
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def resizeEvent(self = None, event = None):
        '''
        处理尺寸变化事件，并同步内容高度与可见区。

        参数:
            event (QResizeEvent): Qt 尺寸变化事件对象。
        返回:
            无
        '''
        super(LPSuperListView, self).resizeEvent(event)
        self.updateContentHeight()
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def _scrollValueChanged(self, value):
        '''
        处理滚动条值变化，并广播新的可见区。

        参数:
            value (int): 当前滚动条位置。
        返回:
            无
        '''
        self.emitVisibleRowsChanged()

    
    def _scrollRangeChanged(self, minimum, maximum):
        '''
        处理滚动范围变化，并延迟刷新可见区。

        参数:
            minimum (int): 滚动条最小值。
            maximum (int): 滚动条最大值。
        返回:
            无
        '''
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def updateContentHeight(self):
        '''
        根据当前网格参数更新内容高度。

        参数:
            无
        返回:
            无
        '''
        if not self.model():
            self.maxContentHeight = 0
            return None
        itemCount = None.model().rowCount()
        gridWidth = max(1, self.gridSize().width())
        itemCountInRow = max(1, math.floor(self.width() / gridWidth))
        rowCount = math.ceil(itemCount / itemCountInRow)
        self.maxContentHeight = rowCount * (self.gridSize().height() + 30)
        if self.showAllItems:
            self.setMinimumHeight(self.maxContentHeight)
        self.resizeSignal.emit()

    
    def emitVisibleRowsChanged(self, force = (False,)):
        '''
        计算并广播当前视口可见的首尾索引范围。

        参数:
            force (bool): 是否忽略重复范围并强制发送信号。
        返回:
            无
        '''
        model = self.model()
        if model is None or model.rowCount() == 0:
            visibleRows = (-1, -1)
        elif self.isVisible() or self.viewport().height() <= 0:
            visibleRows = (-1, -1)
        else:
            visibleRows = self._calculateVisibleRows(model.rowCount())
        if force and visibleRows == self._lastVisibleRows:
            return None
        self._lastVisibleRows = None
        self.visibleRowsChanged.emit(visibleRows[0], visibleRows[1])

    
    def _calculateVisibleRows(self, totalRows):
        '''
        基于网格布局和滚动位置估算当前视口可见索引范围。

        参数:
            totalRows (int): 当前模型总行数。
        返回:
            tuple[int, int]: 可见首尾索引；无可见项时返回 `(-1, -1)`。
        '''
        if totalRows <= 0:
            return (-1, -1)
        gridWidth = None(1, self.gridSize().width())
        gridHeight = max(1, self.gridSize().height())
        viewportWidth = max(1, self.viewport().width())
        itemCountInRow = max(1, math.floor(viewportWidth / gridWidth))
        scrollValue = max(0, self.verticalScrollBar().value())
        firstVisualRow = scrollValue // gridHeight
        lastVisualRow = (scrollValue + max(0, self.viewport().height() - 1)) // gridHeight
        firstRow = min(totalRows - 1, firstVisualRow * itemCountInRow)
        lastRow = min(totalRows - 1, (lastVisualRow + 1) * itemCountInRow - 1)
        return (firstRow, max(firstRow, lastRow))

    __classcell__ = None

