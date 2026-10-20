# Source Generated with Decompyle++
# File: LPSuperTableView.pyc (Python 3.9)

import queue
from distutils.version import LooseVersion
from PyQt6.QtCore import Qt, QModelIndex, QMimeData, QPoint, QRect, pyqtSignal, QPropertyAnimation, QTimer, QEasingCurve, pyqtProperty, QEvent, QPointF
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QFontMetrics, QIcon, QColor, QPen, QCursor, QFont, QBrush, QMouseEvent
from PyQt6.QtWidgets import *
import LPGlobalUI
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPMediaInfo import LPLoopMode

class LPSuperTableDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.can_animate = False
        self.parent = parent

    
    def paint(self = None, painter = None, option = None, index = None):
        option.state &= ~(QStyle.StateFlag.State_HasFocus)
        superTableView = option.styleObject
        behavior = superTableView.selectionBehavior()
        hoverIndex = superTableView.hoverIndex()
        if option.state & QStyle.StateFlag.State_Selected and behavior != QAbstractItemView.SelectionBehavior.SelectItems:
            if behavior == QAbstractItemView.SelectionBehavior.SelectRows and hoverIndex.row() == index.row():
                option.state |= QStyle.StateFlag.State_MouseOver
            if behavior == QAbstractItemView.SelectionBehavior.SelectColumns and hoverIndex.column() == index.column():
                option.state |= QStyle.StateFlag.State_MouseOver
        if option.state & QStyle.StateFlag.State_Selected:
            option.state &= ~(QStyle.StateFlag.State_MouseOver)
        rect = option.rect
        if self.can_animate and self.parent is not None and index.row() in self.parent.animations:
            y_pos = self.parent.animations[index.row()].currentValue()
            rect.moveTop(y_pos)
        super().paint(painter, option, index)

    __classcell__ = None


class LPSuperTableView(QTableView):
    move_delete_lock_signal = pyqtSignal()
    visibleRowsChanged = pyqtSignal(int, int)
    
    def __init__(self = None, parent = None):
        '''
        初始化增强表格视图，并绑定滚动/拖拽相关状态。

        参数:
            parent (QWidget): 父级控件。
        返回:
            无
        '''
        super(LPSuperTableView, self).__init__(parent)
        self.mHoverRow = -1
        self.mHoverColumn = -1
        self._lastVisibleRows = (-2, -2)
        self.setMouseTracking(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalScrollBar().valueChanged.connect(self.sliderValueChanged)
        self.verticalScrollBar().rangeChanged.connect(self._scrollRangeChanged)
        self.lastCursorPos = None
        self.lastCursorActionIndex = None
        self.source_row = -1
        self.drop_row = -1
        self.drop_position = None
        self.init_scroll()
        self.animations = { }

    
    def setupUI(self):
        '''
        初始化表格默认样式。

        参数:
            无
        返回:
            无
        '''
        self.setStyleSheet('\n            QTableView::item {color: rgb(108,108,108)}\n            QTableView::item:selected{\n            selection-color: white;\n            background-color: rgb(72, 72, 72);\n            }\n            QTableView{selection-background-color: rgb(72, 72, 72); border: none;}\n            QTableView::item:hover{background: rgb(31,31,31); color: white}\n\n            QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle:vertical {\n                    background: rgb(82,82,82);\n                    min-height: 30px;\n                    border-radius: 5px;\n                }\n                QScrollBar::handle:horizontal {\n                    background: rgb(82,82,82);\n                    min-width: 30px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                    QScrollBar::add-page, QScrollBar::sub-page {\n            height: 0px;\n                    width: 0px;\n                    border: 0px;\n            }\n            QHeaderView::section {\n            background-color: transparent;\n            color: white;\n            min-height: 50px;\n            }\n            QHeaderView::down-arrow {\n            subcontrol-position: center right;\n            image: url("%s");\n            padding-right: 8px;\n            }\n            QHeaderView::up-arrow {\n            subcontrol-position: center right;\n            image: url("%s");\n            padding-right: 8px;\n            }\n            ' % (LPGlobalUI.imagePath('arrow_down.png'), LPGlobalUI.imagePath('arrow_up.png')))

    
    def sliderValueChanged(self, value):
        '''
        处理滚动条位置变化，并同步悬浮行与可见区状态。

        参数:
            value (int): 当前滚动条值。
        返回:
            无
        '''
        self.updateRowHover()
        self.emitVisibleRowsChanged()

    
    def _scrollRangeChanged(self, minimum, maximum):
        '''
        处理滚动范围变化，并延迟刷新当前可见行范围。

        参数:
            minimum (int): 滚动条最小值。
            maximum (int): 滚动条最大值。
        返回:
            无
        '''
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def hoverIndex(self):
        '''
        返回当前悬浮所在的模型索引。

        参数:
            无
        返回:
            QModelIndex: 当前悬浮索引。
        '''
        return self.model().index(self.mHoverRow, self.mHoverColumn)

    
    def setModel(self = None, model = None):
        '''
        设置表格模型，并在模型切换后刷新当前可见行范围。

        参数:
            model (QAbstractItemModel | None): 新模型对象。
        返回:
            无
        '''
        super().setModel(model)
        self._lastVisibleRows = (-2, -2)
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def showEvent(self = None, event = None):
        '''
        处理控件显示事件，并刷新当前可见行范围。

        参数:
            event (QShowEvent): Qt 显示事件对象。
        返回:
            无
        '''
        super().showEvent(event)
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def resizeEvent(self = None, event = None):
        '''
        处理控件尺寸变化事件，并刷新当前可见行范围。

        参数:
            event (QResizeEvent): Qt 尺寸变化事件对象。
        返回:
            无
        '''
        super().resizeEvent(event)
        None(None, (lambda : self.emitVisibleRowsChanged(True)))

    
    def emitVisibleRowsChanged(self, force = (False,)):
        '''
        计算并广播当前视口可见的首尾行。

        参数:
            force (bool): 是否忽略重复范围强制发送信号。
        返回:
            无
        '''
        model = self.model()
        if model is None or model.rowCount() == 0:
            visibleRows = (-1, -1)
        elif self.isVisible() or self.viewport().height() <= 0:
            visibleRows = (-1, -1)
        else:
            firstRow = self.rowAt(0)
            lastRow = self.rowAt(max(0, self.viewport().height() - 1))
            if firstRow < 0 and lastRow < 0:
                visibleRows = (-1, -1)
            elif firstRow < 0:
                firstRow = lastRow
            if lastRow < 0:
                lastRow = firstRow
            visibleRows = (firstRow, lastRow)
        if force and visibleRows == self._lastVisibleRows:
            return None
        self._lastVisibleRows = None
        self.visibleRowsChanged.emit(visibleRows[0], visibleRows[1])

    
    def mouseMoveEvent(self = None, event = None):
        super().mouseMoveEvent(event)
        self.lastCursorPos = event.pos()
        self.updateRowHover()
        event.accept()

    
    def updateRowHover(self):
        if not self.lastCursorPos:
            return None
        if not None.model():
            return None
        index = None.indexAt(self.lastCursorPos)
        oldHoverRow = self.mHoverRow
        oldHoverColumn = self.mHoverColumn
        self.mHoverRow = index.row()
        self.mHoverColumn = index.column()
        if self.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectRows:
            for i in range(self.model().columnCount()):
                self.update(self.model().index(self.mHoverRow, i))
        if self.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectColumns:
            for i in range(self.model().rowCount()):
                self.update(self.model().index(i, self.mHoverColumn))
                self.update(self.model().index(i, oldHoverColumn))

    
    def set_allow_drag(self):
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)

    
    def startDrag(self, supportedActions):
        indexes = self.selectedIndexes()
        if not indexes:
            return None
        mime_data = None()
        selected_text = (lambda .0 = None: [ self.model().data(index, Qt.ItemDataRole.DisplayRole) for index in .0 ])(indexes)
        track_name = selected_text[1].get('trackName', '')
        mime_data.setText(track_name)
        source_index = indexes[0]
        self.source_row = source_index.row()
        mime_data.setData('application/x-pyqt-table-row', str(source_index.row()).encode())
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        pixmap = self.create_drag_pixmap(track_name)
        drag.setHotSpot(pixmap.rect().topLeft() + QPoint(-15, -10))
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)

    
    def dropEvent(self, event):
        if not event.mimeData().hasText():
            event.ignore()
            self.reset_drop_state()
            return None
        None.reset_scroll_state()
        mime_data = event.mimeData()
        source_row = int(mime_data.data('application/x-pyqt-table-row'))
        target = self.indexAt(event.position().toPoint())
        target_row = target.row()
        if target_row == -1:
            target_row = self.model().rowCount() - 1
            self.drop_row = target_row
            self.drop_position = 'below'
        if not target_row == self.model().playList.index or self.drop_position == 'below':
            if (target_row == self.model().playList.index + 1 or self.drop_position == 'above' or target_row == 0) and self.model().playList.index + 1 == self.model().rowCount() and self.drop_position == 'above' and self.is_preloading():
                track_name = self.get_preloading_track_name(target_row)
                text = f'''The next track,{track_name},is preloading and cannot be modified or deleted'''
                LPGlobalUI.toast.showToast(text, self)
                self.reset_drop_state()
                return None
            target_index = None + 1
            source_index = source_row + 1
            if self.drop_position == 'above':
                if source_row < target_row:
                    target_index = target_index - 2
                    target_row = target_row - 1
                else:
                    target_index = target_index - 1
                    target_row = target_row
        if self.drop_position == 'below':
            if source_row < target_row:
                target_index = target_index - 1
                target_row = target_row
            else:
                target_index = target_index
                target_row = target_row + 1
        logger.debug('chris source index == ' + str(source_index))
        logger.debug('chris target  index == ' + str(target_index))
        self.start_animation(source_row, target_row, source_index, target_index)
        self.reset_drop_state()
        event.accept()
        logger.debug('dropEvent == end')

    
    def get_preloading_track_name(self, target_row):
        '''获取preloading歌曲的名字'''
        track_name = self.model().playList.list[0].trackName
        if target_row != self.model().rowCount() - 1:
            if target_row == self.model().playList.index + 1 or target_row == 0:
                track_name = self.model().playList.list[target_row].trackName
            else:
                track_name = self.model().playList.list[target_row + 1].trackName
        return track_name

    
    def get_preloading_row(self):
        '''获取preloading的行号'''
        if self.is_preloading():
            if self.model().playList.index != self.model().rowCount() - 1:
                return self.model().playList.index + 1
            return None

    
    def is_preloading(self):
        ''' 获取是否preloading状态'''
        result_queue = queue.Queue()
        LPGlobalUI.currentDevice.queueManager.get_queue_index(result_queue)
        result = result_queue.get()
        preload_index = result.get('PreloadingIndex', None)
        current_index = result.get('CurrentIndex', None)
        return int(preload_index) != int(current_index)

    
    def reset_drop_state(self):
        self.drop_row = -1
        self.source_row = -1
        self.drop_position = None
        self.selectionModel().clearSelection()

    
    def dragEnterEvent(self, event):
        '''拖动进入事件'''
        logger.debug('dragEnterEvent triggered!')
        if self.source_row == self.model().playList.index or self.source_row == self.get_preloading_row():
            logger.debug('dragEnterEvent ignore!')
            event.ignore()
        else:
            logger.debug('dragEnterEvent accept!')
            event.accept()

    
    def dragMoveEvent(self, event):
        logger.debug('dragMoveEvent triggered!')
        self.start_scroll(event)
        pos = event.position().toPoint()
        index = self.indexAt(pos)
        if index.isValid():
            rect = self.visualRect(index)
            self.drop_row = index.row()
            self.drop_position = 'above' if pos.y() < rect.center().y() else 'below'
        else:
            self.drop_row = -1
            self.drop_position = None
        self.update()
        event.accept()

    
    def dragLeaveEvent(self = None, event = None):
        logger.debug('dragLeaveEvent triggered!')
        self.reset_drag_leave_state()
        self.reset_scroll_state()
        super().dragLeaveEvent(event)

    
    def reset_drag_leave_state(self):
        self.drop_row = -1
        self.drop_position = None
        self.selectionModel().clearSelection()

    
    def create_drag_pixmap(self, track_name):
        font = QFont()
        font.setPointSize(13)
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.horizontalAdvance(track_name)
        text_height = font_metrics.height()
        padding = 10
        corner_radius = 5
        pixmap_width = text_width + 2 * padding
        pixmap_height = text_height + 2 * padding
        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(25, 25, 25, 150))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, pixmap_width, pixmap_height, corner_radius, corner_radius)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, track_name)
        painter.end()
        return pixmap

    
    def need_scroll(self):
        '''根据数量判断是否需要滚动 这里设置为超过8行需要滚动'''
        model = self.model()
        row_count = model.rowCount()
        if row_count <= 8:
            self.setAutoScroll(False)
            return False
        None.setAutoScroll(True)
        return True

    
    def setAutoScroll(self = None, enabled = None):
        '''控制垂直滚动条的滚动是否启用'''
        if enabled:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    
    def start_auto_scroll(self, direction):
        '''开始自动滚动'''
        logger.debug('start_auto_scroll self.is_scrolling --> ' + str(self.is_scrolling))
        if not self.is_scrolling:
            self.is_scrolling = True
            logger.debug('start_auto_scroll self.is_scrolling --> ' + str(self.is_scrolling))
            self.scroll_direction = direction
            logger.debug('start_auto_scroll self.scroll_direction --> ' + direction)
            self.scroll_timer.start()

    
    def stop_auto_scroll(self):
        '''停止自动滚动'''
        if self.is_scrolling:
            self.is_scrolling = False
            self.scroll_timer.stop()

    
    def smooth_scroll(self):
        '''平滑滚动的实现'''
        logger.debug('smooth_scroll !!!!')
        if self.scroll_direction == 'up':
            logger.debug('smooth_scroll up')
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)
        elif self.scroll_direction == 'down':
            logger.debug('smooth_scroll down')
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)

    
    def start_scroll(self, event):
        if not self.need_scroll():
            return None
        None.debug('start_scroll !!!!')
        rect = self.viewport().rect()
        scroll_threshold = 40
        if int(event.position().y()) < scroll_threshold:
            self.start_auto_scroll('up')
            logger.debug('start_scroll up !!!')
        elif int(event.position().y()) > rect.height() - scroll_threshold:
            self.start_auto_scroll('down')
            logger.debug('start_scroll down !!!')
        else:
            self.stop_auto_scroll()
        if self.lastCursorPos is not None:
            delta_y = event.position().y() - self.lastCursorPos.y()
            if delta_y > 0:
                self.is_scrolling_down = True
                self.is_scrolling_up = False
            elif delta_y < 0:
                self.is_scrolling_up = True
                self.is_scrolling_down = False
            if self.is_scrolling_up and self.is_scrolling_down:
                logger.debug('reverse direction --> start stop_auto_scroll')
                self.stop_auto_scroll()
        self.lastCursorPos = event.position().toPoint()

    
    def init_scroll(self):
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(100)
        self.scroll_timer.timeout.connect(self.smooth_scroll)
        self.is_scrolling = False
        self.scroll_direction = None
        self.is_scrolling_up = False
        self.is_scrolling_down = False

    
    def reset_scroll_state(self):
        self.scroll_timer.stop()
        self.scroll_direction = None
        self.is_scrolling = None
        self.is_scrolling_up = False
        self.is_scrolling_down = False

    
    def reset_cursor(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)

    
    def row_y_position(self, row):
        return row * self.rowHeight(0)

    
    def start_animation(self, source_row, target_row, source_index, target_index):
        start_y = self.row_y_position(source_row)
        end_y = self.row_y_position(target_row)
        animation = QPropertyAnimation(self, b'row_position')
        animation.setStartValue(start_y)
        animation.setEndValue(end_y)
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        None((lambda : self.animation_finished(source_row, target_row, source_index, target_index)))
        self.animations[source_row] = animation
        animation.start()

    
    def row_position(self):
        return 0

    
    def set_row_position(self, value):
        self.update()

    row_position = pyqtProperty(int, row_position, set_row_position, **('fget', 'fset'))
    
    def animation_finished(self, source_row, target_row, source_index, target_index):
        if source_row in self.animations:
            del self.animations[source_row]
        self.real_move(source_row, target_row, source_index, target_index)
        self.clear_state_after_animation()

    
    def clear_state_after_animation(self):
        self.selectionModel().clearSelection()
        pos = QCursor.pos()
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(pos), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        self.mouseMoveEvent(event)

    
    def real_move(self, source_row, target_row, source_index, target_index):
        
        def finished_method(result = None):
            if result:
                logger.debug('upnp drag_drop_rows success')
            else:
                logger.debug('upnp drag_drop_rows failed')
            self.reset_drop_state()

        music_array = self.model().playList.list[source_row:source_row + 1]
        self.model().moveRow(QModelIndex, source_row, QModelIndex, target_row)
        if source_row < self.model().playList.index and target_row >= self.model().playList.index:
            self.model().playList.index -= 1
        if source_row > self.model().playList.index and target_row <= self.model().playList.index:
            self.model().playList.index += 1
        self.move_delete_lock_signal.emit()
        LPGlobalUI.currentDevice.drag_drop_rows(source_index, target_index, self.model().playList, music_array, finished_method)

    __classcell__ = None

