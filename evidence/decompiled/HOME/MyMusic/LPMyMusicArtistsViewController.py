# Source Generated with Decompyle++
# File: LPMyMusicArtistsViewController.pyc (Python 3.9)

from string import Template
import hashlib
import queue
import threading
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QAction
import LPGlobalUI
from HOME import LPMyMusicViewController
from HOME.LPMyMusicViewController_ui import Ui_mymusicViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController import LPMyMusicArtistDetailViewController
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from HOME.MyMusic.LPTrackImageLoadHelper import LPTrackImageLoadHelper
from LPClientFramework import LPUtility, LPBeetsWrapper
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle, StackWidget_Title
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
ARTIST_CARD_COVER_SIZE = 155
ARTIST_CARD_PREFETCH_ROWS = 4

class LPMyMusicArtistsListModel(QtCore.QAbstractListModel):
    artistInfoResolvedSignal = QtCore.pyqtSignal(int, int, object, object, object)
    
    def __init__(self = None, data = None, parent = None):
        '''
        初始化艺人卡片模型，并建立可见区驱动的头像解析与下载协调器。

        参数:
            data (list[dict]): 艺人数据数组。
            parent (QObject | None): Qt 父对象。
        返回:
            无
        '''
        super(LPMyMusicArtistsListModel, self).__init__(parent)
        self._data = data
        self._view = None
        self._generation = 0
        self._isShutdown = False
        self._pendingArtistInfoRows = set()
        self._lock = threading.RLock()
        self.trackImageLoadHelper = LPTrackImageLoadHelper(self._imageUrlForRow, self.rowCount, LPUtility, ARTIST_CARD_COVER_SIZE, ARTIST_CARD_PREFETCH_ROWS, self, **('cacheSize', 'prefetchRows', 'parent'))
        self.trackImageLoadHelper.rowImageReadySignal.connect(self._handleRowImageReady)
        self.artistInfoResolvedSignal.connect(self._handleArtistInfoResolved, QtCore.Qt.ConnectionType.QueuedConnection)
        self._artistInfoQueue = queue.Queue()
        self._artistInfoThread = threading.Thread(self._artistInfoWorkerLoop, 'LPMyMusicArtistsInfoLoader', True, **('target', 'name', 'daemon'))
        self._artistInfoThread.start()

    
    def rowCount(self, parent = (None,)):
        '''
        返回当前模型中的艺人数。

        参数:
            parent (QModelIndex | None): Qt 父索引。
        返回:
            int: 当前模型行数。
        '''
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        '''
        返回指定索引的展示数据，不再在这里触发后台副作用。

        参数:
            index (QModelIndex): 目标索引。
            role (Qt.ItemDataRole): 请求的数据角色。
        返回:
            object | None: 展示角色返回艺人字典，其余情况返回 None。
        '''
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            return self._data[row]

    
    def attachView(self, view):
        '''
        绑定列表视图，并开始按可见区调度头像解析与下载。

        参数:
            view (QListView | None): 需要绑定的列表视图。
        返回:
            无
        '''
        if self._view is view:
            self.refreshVisibleRows()
            return None
        if None._view is not None:
            self._disconnectViewSignals(self._view)
        self._view = view
        self.trackImageLoadHelper.attachView(view)
        if self._view is None:
            return None
        None._view.visibleRowsChanged.connect(self._onVisibleRowsChanged)
        self._view.destroyed.connect(self.shutdown)
        self.refreshVisibleRows()

    
    def refreshVisibleRows(self):
