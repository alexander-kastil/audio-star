# Source Generated with Decompyle++
# File: LPQueueListView.pyc (Python 3.9)

'''
@Time ： 2025/9/24 09:42
@Auth ： Chris
@File ：LPQueueListView.py
@Desc:
'''
import queue
import time
from threading import Thread
from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QRectF, QRect, QEvent, pyqtSignal, QPoint, QTimer, QPropertyAnimation, QPointF
from PyQt6.QtGui import QBrush, QPainterPath, QIcon, QPixmap, QFont, QFontMetrics, QPainter, QColor, QMovie, QPen, QMouseEvent, QCursor
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QToolTip, QListView, QPushButton, QAbstractItemView, QGraphicsOpacityEffect, QAbstractSlider, QMenu
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Subtitle, DEFAULT, Main_Text, Sub_Text
from LPClientFramework.LPFeature import LPFeatureCanUtils
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.listview.LPMobileListView import LPMobileListView

class LPQueueListModel(QAbstractListModel):
    
    def __init__(self = None, playList = None, parent = None):
        super().__init__(parent)
        self.playList = playList
        self._data = self.playList.list
        self.coverImageQueue = queue.Queue()
        self.fetchImageThread = None
        self.imageUpdateRunning = True
        if parent:
            parent.destroyed.connect(self.cleanup)

    
    def flags(self = None, index = None):
        flags = super().flags(index)
        return flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        playItem = None._data[row]
        if role == Qt.ItemDataRole.DisplayRole:
            imageUrl = playItem.trackImage
            if imageUrl and len(imageUrl) > 0:
                self.fetchPixmap(index, imageUrl)
            return (playItem, row == self.playList.index)
        if None == Qt.ItemDataRole.UserRole:
            return playItem
        if None == Qt.ItemDataRole.UserRole + 1:
            return self.playList.index

    
    def fetchPixmap(self, index, imageUrl, isBlurred = (False,)):
        exist = LPUtility.checkCachedPixmapWithUrl(imageUrl, 48)
        if not exist:
            self.coverImageQueue.put({
                'value': imageUrl,
                'index': index,
                'isBlurred': isBlurred })
        
        def _fetchImageMethod():
            if not self.imageUpdateRunning:
                return None
            if None.coverImageQueue.empty():
                time.sleep(0.3)
                continue
            dataDict = self.coverImageQueue.get()
            url = dataDict.get('value', None)
            indexObj = dataDict.get('index', None)
            if self.playList.header.mediaSource == 'Plex':
                respDict = LPUtility.fetchUrlQPixmap(url, True, 48)
            else:
                respDict = LPUtility.fetchUrlQPixmap(url, False, 48)
            pixmap = respDict.get('image', None)
            if pixmap:
                self.dataChanged.emit(indexObj, indexObj)
            self.coverImageQueue.task_done()
            continue

        if self.fetchImageThread is None:
            self.fetchImageThread = Thread(_fetchImageMethod, True, **('target', 'daemon'))
            self.fetchImageThread.start()

    
    def cleanup(self):
        logger.debug('cleanup ================')
        if self.fetchImageThread:
            self.imageUpdateRunning = False

    
    def addItemList(self, playList):
        start = len(self._data)
        end = start + len(playList.list) - 1
        if playList.list:
            self.beginInsertRows(QModelIndex(), start, end)
            self._data.extend(playList.list)
            self.endInsertRows()

    
    def removeRow(self, row, parent = (None,)):
        if row <= row or row < len(self._data):
            pass
        else:
            0
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._data[row]
        self.endRemoveRows()
        if row < self.playList.index:
            self.playList.index -= 1
        return True
        return False

    
    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        '''单行'''
        logger.debug('LPQueueTableModel moveRow start')
        if sourceRow == destinationChild:
            return False
        None.beginRemoveRows(QModelIndex(), sourceRow, sourceRow)
        row_data = self._data[sourceRow]
        del self._data[sourceRow]
        self.endRemoveRows()
        self.beginInsertRows(QModelIndex(), destinationChild, destinationChild)
        self._data.insert(destinationChild, row_data)
        self.endInsertRows()
        logger.debug('LPQueueTableModel moveRow end')
        return True

    __classcell__ = None


class LPQueueDelegate(QStyledItemDelegate):
    optClicked = pyqtSignal(QModelIndex, object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.listview = parent
        self.movie = QMovie(LPGlobalUI.imagePath('dark_playing.gif'))
        self.movie.frameChanged.connect(self.updateView)
        self.playingRow = -1
        self.moreMenuRow = -1
        self.listview.installEventFilter(self)

    
    def getPlayingRow(self):
        model = self.listview.model()
        if model and isinstance(model, LPQueueListModel):
            playingRow = model.playList.index
        else:
            playingRow = -1
        return playingRow

    
    def eventFilter(self, obj, event):
        '''监听队列视图显示/隐藏，按需启停播放动画。

        参数:
            obj: 事件源对象。
            event: 队列视图事件。
        返回值:
            False，不拦截事件。
        '''
        if obj is self.listview and event.type() in (QEvent.Type.Show, QEvent.Type.Hide):
            self._syncMovieState()
        return False

    
    def _syncMovieState(self):
        '''按需启停播放动画：仅在有播放行、设备播放中且视图可见时运行。

        :return: None。
        '''
        if self.getPlayingRow() >= 0 and self.listview is not None and self.listview.isVisible():
            pass
        should_run = getattr(getattr(LPGlobalUI.currentDevice, 'mediaInfo', None), 'playState', '') == 'PLAYING'
        if should_run or self.movie.state() != QMovie.MovieState.Running:
            self.movie.start()
        elif self.movie.state() != QMovie.MovieState.NotRunning:
            self.movie.stop()

    
    def sizeHint(self, option, index):
        playingHeight = 84
        normalHeight = 60
        playingRow = index.data(Qt.ItemDataRole.UserRole + 1, **('role',))
        isPlayingItem = playingRow == index.row()
        if isPlayingItem:
            return QSize(option.rect.width(), playingHeight)
        return None(option.rect.width(), normalHeight)

    
    def editorEvent(self = None, event = None, model = None, option = None, index = None):
