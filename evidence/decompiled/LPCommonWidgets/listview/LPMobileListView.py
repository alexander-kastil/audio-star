# Source Generated with Decompyle++
# File: LPMobileListView.pyc (Python 3.9)

'''
@Time ： 2025/9/26 17:19
@Auth ： Chris
@File ：LPMobileListView.py
@Desc:
'''
from PyQt6.QtCore import QMimeData, Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QEvent, QPointF, QModelIndex
from PyQt6.QtGui import QDrag, QFont, QFontMetrics, QPixmap, QPainter, QColor, QCursor, QMouseEvent
from PyQt6.QtWidgets import QListView, QAbstractItemView
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class LPMobileListView(QListView):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.allowDrag = False
        self.lastCursorPos = None
        self.sourceRow = -1
        self.dropRow = -1
        self.dropPosition = None
        self.initScroll()
        self.animations = { }
        self.scrollBarTimer = QTimer(self)
        self.scrollBarTimer.setSingleShot(True)
        self.scrollBarTimer.timeout.connect(self.hideScrollBar)
        self._suppressAutoShow = False
        self.verticalScrollBar().hide()
        self.verticalScrollBar().setStyleSheet('\n            QScrollBar {\n                border: 0px;\n                background: transparent;\n                width:10px;\n                height:10px;\n                margin: 0px 0px 0px 0px;\n            }\n            QScrollBar:vertical {\n                background: transparent;\n                width: 8px\n            }\n            QScrollBar::handle:vertical {\n                background: rgba(255,255,255,166);\n                min-height: 30px;\n                border-radius: 4px;\n            }\n            QScrollBar::add-line {\n                border: 0px;\n                background: none;\n                height: 0px;\n                width: 0px;\n            }\n            QScrollBar::sub-line {\n                border: 0px;\n                background: none;\n                height: 0px;\n                width: 0px;\n            }\n            QScrollBar::add-page, QScrollBar::sub-page {\n                height: 0px;\n                width: 0px;\n                border: 0px;\n            }\n        ')
        self.verticalScrollBar().valueChanged.connect(self.showScrollBar)

    
    def resizeEvent(self = None, event = None):
        '''尺寸变化期间抑制滚动条自动显示，避免沉浸切换等布局重排导致滚动条闪烁。'''
        self._suppressAutoShow = True
        super().resizeEvent(event)
        QTimer.singleShot(0, self._clearSuppressAutoShow)

    
    def _clearSuppressAutoShow(self):
        '''清除尺寸变化抑制标志。'''
        self._suppressAutoShow = False

    
    def showScrollBar(self):
        if self._suppressAutoShow:
            return None
        None.verticalScrollBar().show()
        self.scrollBarTimer.start(2000)

    
    def hideScrollBar(self):
        self.verticalScrollBar().hide()

    
    def setAllowDrag(self, allow = (True,)):
        self.allowDrag = allow

    
    def mouseMoveEvent(self = None, event = None):
        super().mouseMoveEvent(event)
        self.lastCursorPos = event.pos()
        event.accept()

    
    def resetDropState(self):
        self.dropRow = -1
        self.sourceRow = -1
        self.dropPosition = None
        self.selectionModel().clearSelection()

    
    def startDrag(self, supportedActions):
        logger.debug('[LPMobileListView] startDrag')
        if not self.allowDrag:
            return None
        indexes = None.selectedIndexes()
        if not indexes:
            return None
        mimeData = None()
        sourceIndex = indexes[0]
        self.sourceRow = sourceIndex.row()
        mimeData.setData('application/x-pyqt-table-row', str(sourceIndex.row()).encode())
        showText = self.getShowText(indexes)
        if showText:
            mimeData.setText(showText)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        if showText:
            pixmap = self.createDragPixmap(showText)
            if pixmap:
                drag.setHotSpot(pixmap.rect().topLeft() + QPoint(-15, -10))
                drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)

    
    def dropEvent(self, event):
        if not event.mimeData().hasText():
            event.ignore()
            self.resetDropState()
            return None
        None.resetScrollState()
        mimeData = event.mimeData()
        sourceRow = int(mimeData.data('application/x-pyqt-table-row'))
        target = self.indexAt(event.position().toPoint())
        targetRow = target.row()
        if targetRow == -1:
            targetRow = self.model().rowCount() - 1
            self.dropRow = targetRow
            self.dropPosition = 'below'
        if not self.canRowDrop(targetRow):
            self.onRowNotAllowDrop(targetRow)
            self.resetDropState()
            return None
        targetIndex = None + 1
        sourceIndex = sourceRow + 1
        print('hahahhaahahahahh------------', self.dropPosition)
        if self.dropPosition == 'above':
            if sourceRow < targetRow:
                targetIndex = targetIndex - 2
                targetRow = targetRow - 1
            else:
                targetIndex = targetIndex - 1
                targetRow = targetRow
        if self.dropPosition == 'below':
            if sourceRow < targetRow:
                targetIndex = targetIndex - 1
                targetRow = targetRow
            else:
                targetIndex = targetIndex
                targetRow = targetRow + 1
        logger.debug('chris source index == ' + str(sourceIndex))
        logger.debug('chris target  index == ' + str(targetIndex))
        self.startAnimation(sourceRow, targetRow, sourceIndex, targetIndex)
        self.resetDropState()
        event.accept()
        logger.debug('dropEvent == end')

    
    def dragEnterEvent(self, event):
        '''拖动进入事件'''
        logger.debug('dragEnterEvent triggered!')
        if self.canRowDrag(self.sourceRow):
            logger.debug('dragEnterEvent accept!')
            event.accept()
        else:
            logger.debug('dragEnterEvent ignore!')
            event.ignore()

    
    def dragMoveEvent(self, event):
        logger.debug('dragMoveEvent triggered!')
        self.startScroll(event)
        pos = event.position().toPoint()
        index = self.indexAt(pos)
        if index.isValid():
            rect = self.visualRect(index)
            self.dropRow = index.row()
            self.dropPosition = 'above' if pos.y() < rect.center().y() else 'below'
        else:
            self.dropRow = -1
            self.dropPosition = None
        self.update()
        event.accept()

    
    def dragLeaveEvent(self = None, event = None):
        logger.debug('dragLeaveEvent triggered!')
        self.resetDragLeaveState()
        self.resetScrollState()
        super().dragLeaveEvent(event)

    
    def resetDragLeaveState(self):
        self.dropRow = -1
        self.dropPosition = None
        self.selectionModel().clearSelection()

    
    def createDragPixmap(self, showText):
        pass

    
    def initScroll(self):
        self.scrollTimer = QTimer(self)
        self.scrollTimer.setInterval(100)
        self.scrollTimer.timeout.connect(self.smoothScroll)
        self.isScrolling = False
        self.scrollDirection = None
        self.isScrollingUp = False
        self.isScrollingDown = False

    
    def needScroll(self):
        return self.verticalScrollBar().maximum() > 0

    
    def startAutoScroll(self, direction):
        '''开始自动滚动'''
        logger.debug('[startAutoScroll] self.isScrolling --> ' + str(self.isScrolling))
        if not self.isScrolling:
            self.isScrolling = True
            logger.debug('start_auto_scroll self.is_scrolling --> ' + str(self.isScrolling))
            self.scrollDirection = direction
            logger.debug('start_auto_scroll self.scroll_direction --> ' + direction)
            self.scrollTimer.start()

    
    def stopAutoScroll(self):
        '''停止自动滚动'''
        if self.isScrolling:
            self.isScrolling = False
            self.scrollTimer.stop()

    
    def startScroll(self, event):
        if not self.needScroll():
            return None
        None.debug('start_scroll !!!!')
        rect = self.viewport().rect()
        scroll_threshold = 40
        if int(event.position().y()) < scroll_threshold:
            self.startAutoScroll('up')
            logger.debug('start_scroll up !!!')
        elif int(event.position().y()) > rect.height() - scroll_threshold:
            self.startAutoScroll('down')
            logger.debug('start_scroll down !!!')
        else:
            self.stopAutoScroll()
        if self.lastCursorPos is not None:
            delta_y = event.position().y() - self.lastCursorPos.y()
            if delta_y > 0:
                self.isScrollingDown = True
                self.isScrollingUp = False
            elif delta_y < 0:
                self.isScrollingUp = True
                self.isScrollingDown = False
            if self.isScrollingUp and self.isScrollingDown:
                logger.debug('reverse direction --> start stop_auto_scroll')
                self.stopAutoScroll()
        self.lastCursorPos = event.position().toPoint()

    
    def smoothScroll(self):
        '''平滑滚动的实现'''
        logger.debug('smooth_scroll !!!!')
        if self.scrollDirection == 'up':
            logger.debug('smooth_scroll up')
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)
        elif self.scrollDirection == 'down':
            logger.debug('smooth_scroll down')
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)

    
    def resetScrollState(self):
        self.scrollTimer.stop()
        self.scrollDirection = None
        self.isScrolling = False
        self.isScrollingUp = False
        self.isScrollingDown = False

    
    def row_y_position(self, row):
        index = self.model().index(row, 0)
        rect = self.visualRect(index)
        return rect.top()

    
    def startAnimation(self, sourceRow, targetRow, sourceIndex, targetIndex):
        start_y = self.row_y_position(sourceRow)
        end_y = self.row_y_position(targetRow)
        animation = QPropertyAnimation(self, b'row_position')
        animation.setStartValue(start_y)
        animation.setEndValue(end_y)
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        None((lambda : self.onAnimationFinished(sourceRow, targetRow, sourceIndex, targetIndex)))
        self.animations[sourceRow] = animation
        animation.start()

    
    def row_position(self):
        return 0

    
    def set_row_position(self, value):
        self.update()

    row_position = pyqtProperty(int, row_position, set_row_position, **('fget', 'fset'))
    
    def onAnimationFinished(self, sourceRow, targetRow, sourceIndex, targetIndex):
        if sourceRow in self.animations:
            del self.animations[sourceRow]
        self.realMove(sourceRow, targetRow, sourceIndex, targetIndex)
        self.clear_state_after_animation()

    
    def clear_state_after_animation(self):
        self.selectionModel().clearSelection()
        pos = QCursor.pos()
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(pos), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        self.mouseMoveEvent(event)

    
    def realMove(self, source_row, target_row, source_index, target_index):
        pass

    
    def canRowDrag(self, sourceRow):
        return True

    
    def canRowDrop(self, targetRow):
        return True

    
    def onRowNotAllowDrop(self, targetRow):
        text = f'''The row {targetRow} cannot be modified or deleted'''
        LPGlobalUI.toast.showToast(text, self)

    
    def getShowText(self, indexes):
        pass

    __classcell__ = None

