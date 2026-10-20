# Source Generated with Decompyle++
# File: LPQobuzDetailBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/1 16:49
@Auth ： Chris
@File ：LPQobuzDetailBaseViewController.py
@Desc:
'''
import enum
import json
import random
import threading
from functools import partial
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtWidgets import QHeaderView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzAlbumTrackTableView import LPQobuzAlbumTracksTableModel, LPQobuzAlbumTrackTableDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzDetailMoreMenu import LPQobuzDetailMoreMenu
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPClientFramework.LPShuffleManager import LPShuffleManager
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPPresetMenu import LPPresetMenu
from LPCommonWidgets.skeleton.LPTableViewSkeleton import LPTableViewSkeletonTableModel, LPTableViewSkeletonDelegate

class ShuffleCacheType(enum.Enum):
    ALBUM_SHUFFLE = 'albumShuffle'
    PLAYLIST_SHUFFLE = 'playlistShuffle'
    ARTIST_SHUFFLE = 'artistShuffle'
    WEEKLYQ_SHUFFLE = 'weeklyQShuffle'


class LPQobuzDetailBaseViewController(LPQobuzBaseViewController):
    loadDataSignal = pyqtSignal(object, object)
    updateShuffleButtonSignal = pyqtSignal(object)
    updateShuffleCacheSignal = pyqtSignal()
    updateFavBtnSignal = pyqtSignal(object)
    initTableViewSignal = pyqtSignal(object)
    updateTableviewSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.total = self.defaultTotal
        self.limit = self.defaultLimit
        self.itemId = None
        self.itemType = None
        self.firstShow = True
        self.isShuffle = False
        self.playItem = None
        self.playList = None
        self.shuffleCacheType = None
        self.defaultShufflePixmap = LPUtility.tintImage(LPGlobalUI.imagePath('minibar/shuffle.png'), LPGlobalUI.THEME_DEFAULT_COLOR)
        self.shufflePixmap = LPUtility.tintImage(LPGlobalUI.imagePath('minibar/shuffle.png'), LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        self.unFavoritePixmap = LPUtility.tintImage(LPGlobalUI.imagePath('unfavorite.png'), LPGlobalUI.THEME_DEFAULT_COLOR)
        self.presetPixmap = LPUtility.tintImage(LPGlobalUI.imagePath('track_more_preset.png'), LPGlobalUI.THEME_DEFAULT_COLOR)
        self.loadDataSignal.connect(self._loadData)
        self.updateShuffleButtonSignal.connect(self.updateShuffleButtonUI)
        self.updateShuffleCacheSignal.connect(self.updateShuffleCache)
        self.updateFavBtnSignal.connect(self._onFavBtnChanged)
        self.initTableViewSignal.connect(self._initTableview)
        self.updateTableviewSignal.connect(self._updateTableview)
        self.onOptClickedMethod = None
        self.skeletonDelegate = None

    
    def initFavoriteButtonStatus(self):
        '''按本地收藏缓存同步详情页头部收藏按钮状态，缓存未就绪时保持原样。'''
        ids = self.qobuz.favMgr.getFavIds(self.itemType)
        if ids is None:
            return None
        isFavorite = None(self.itemId) in ids
        if self.playItem is not None:
            self.playItem.isFavorite = isFavorite
        self.updateFavBtnSignal.emit(self.favoriteButton)

    
    def refreshFavoriteStatus(self):
        '''按最新收藏缓存刷新详情页头部收藏按钮与曲目行的收藏状态。'''
        playList = getattr(self, 'playList', None)
        if playList is not None:
            self.checkPlayListFavorite(playList)
        if hasattr(self, 'favoriteButton'):
            self.initFavoriteButtonStatus()
        table_view = getattr(self, 'tableView', None)
        if table_view is not None:
            table_view.update()

    
    def _updateTableview(self):
        self.tableView.update()

    _updateTableview = pyqtSlot()(_updateTableview)
    
    def checkMore(self):
        if self.offset >= self.total or self.total == self.defaultTotal:
            return False

    
    def _loadData(self, genres, binding):
        pass

    _loadData = pyqtSlot(object, object)(_loadData)
    
    def favoriteButtonPressed(self):
        logger.debug('[Qobuz Detail] favoriteButtonPressed')
        self.playItem.isFavorite = not (self.playItem.isFavorite)
        self.updateFavBtnSignal.emit(self.sender())
        changeType = 'add' if self.playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, self.itemType, self.itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, self.itemType, self.itemId, changeType)

    
    def _onFavBtnChanged(self, favButton):
        logger.debug(f'''[_onFavoriteButtonChanged] Favorite={self.playItem.isFavorite}''')
        if self.playItem.isFavorite:
            pixmap = LPUtility.tintImage(LPGlobalUI.imagePath('favorite.png'), LPGlobalUI.THEME_HIGH_HIGH_COLOR)
            favButton.setIcon(QIcon(pixmap))
        else:
            favButton.setIcon(QIcon(LPGlobalUI.imagePath('unfavorite.png')))

    
    def _initTableview(self, tableView):
        '''
        playlist 和 weekly 用， album要单独处理多cd
        '''
        self._endSkeleton()
        model = LPQobuzTracksTableWithCoverModel(self.playList, tableView)
        delegate = LPQobuzTrackTableWithCoverDelegate(tableView)
        tableView.setModel(model)
        tableView.horizontalHeader().setVisible(True)
        tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        delegate.favClicked.connect(self.onFavClicked)
        delegate.optClicked.connect(self.onOptClicked)
        tableView.setItemDelegate(delegate)
        tableView.setColumnWidth(0, 50)
        tableView.setColumnWidth(2, 200)
        tableView.setColumnWidth(3, 150)
        tableView.setColumnWidth(4, 50)
        tableView.setColumnWidth(5, 50)
        tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    _initTableview = pyqtSlot(object)(_initTableview)
    
    def onFavClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'add' if playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, LPHeaderType.LP_HEADER_TYPE_SONG, itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    
    def onOptClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        trackMoreMenu = LPQobuzTrackMoreMenu(playItem, self.playItem, self.tableView)
        trackMoreMenu.setupUI()
        trackMoreMenu.showMenu(QCursor.pos())
        if self.itemType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            trackMoreMenu.removeFromPlaylistSignal.connect(self.removeTrack)

    
    def removeTrack(self, playItem):
        pass

    removeTrack = pyqtSlot(object)(removeTrack)
    
    def _loadSkeleton(self, isFixHeight = (False,)):
        rowCount = 10
        if not self.playList:
            self.tableView.horizontalHeader().setVisible(False)
            self.tableView.setModel(LPTableViewSkeletonTableModel(rowCount, 6, self.tableView))
            if not self.skeletonDelegate:
                self.skeletonDelegate = LPTableViewSkeletonDelegate(self.tableView)
            self.skeletonDelegate.startAnimation()
            self.tableView.setItemDelegate(self.skeletonDelegate)
            self.tableView.setColumnWidth(0, 20)
            if isFixHeight:
                tableHeight = rowCount * 60 + 60
                self.tableView.setFixedHeight(tableHeight)

    
    def _endSkeleton(self):
        if self.skeletonDelegate:
            self.skeletonDelegate.stopAnimation()

    
    def playNowButtonPressed(self, tableView):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        if not None.playList:
            logger.warning('error, self.playList not ready')
            return None
        if None.isShuffle:
            row = random.randint(1, len(self.playList.list))
            LPShuffleManager.setShuffle()
        else:
            LPShuffleManager.setNoShuffle()
            row = 1
        playList = tableView.model().playList
        playItem = playList.list[row - 1]
        startIndex = playItem.startIndex
        playList.header.searchUrl = playItem.searchUrl
        xml = playList.generateXML(str(startIndex))
        self.playQobuzPlayList(playList, playItem, xml, row - 1, 'qobuz album', **('playIndex', 'logPrefix'))

    
    def presetButtonPressed(self):
        if self.playList:
            presetMenu = LPPresetMenu(self.sender(), self.playList)
            presetMenu.showMenu()

    
    def shuffleButtonPressed(self):
        self.isShuffle = not (self.isShuffle)
        self.updateShuffleButtonSignal.emit(self.sender())
        self.updateShuffleCacheSignal.emit()

    
    def updateShuffleButtonUI(self, shuffleButton):
        if self.isShuffle:
            pixmap = self.shufflePixmap
        else:
            pixmap = self.defaultShufflePixmap
        shuffleButton.setIcon(QIcon(pixmap))

    
    def updateShuffleCache(self):
        
        def target(isShuffle = None):
            if self.shuffleCacheType == ShuffleCacheType.WEEKLYQ_SHUFFLE:
                LPQobuzUtil.cacheWeeklyShuffle(self.qobuz.fileCache, self.shuffleCacheType, isShuffle)
            elif isShuffle:
                logger.debug(f''' updateShuffleCache add id={self.itemId}  type={self.shuffleCacheType.value}''')
                LPQobuzUtil.cacheShuffleId(self.qobuz.fileCache, self.shuffleCacheType, self.itemId, 'add')
            else:
                logger.debug(f'''updateShuffleCache remove id={self.itemId} type={self.shuffleCacheType.value}''')
                LPQobuzUtil.cacheShuffleId(self.qobuz.fileCache, self.shuffleCacheType, self.itemId, 'remove')

        t = threading.Thread(target, (self.isShuffle,), **('target', 'args'))
        t.start()

    
    def moreButtonPressed(self):
        detailMoreMenu = LPQobuzDetailMoreMenu(self.playItem, self.sender())
        detailMoreMenu.setupUI()
        detailMoreMenu.showMenu(QCursor.pos())

    
    def itemDoubleClick(self, index):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        playList = None.tableView.model().playList
        playItem = playList.list[index.row()]
        streamable = playItem.streamable
        if not streamable:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz playlist detail', 'This track is not available'), LPGlobalUI.mainWindow)
            logger.debug('qobuz track %s not streamable' % playItem.trackName)
            return None
        startIndex = None(playItem.startIndex)
        playList.header.searchUrl = playItem.searchUrl
        xml = playList.generateXML(startIndex)
        self.playQobuzPlayList(playList, playItem, xml, index.row(), 'qobuz album', **('playIndex', 'logPrefix'))

    
    def onTableViewItemClick(self, index):
        if self.tableView.lastCursorActionIndex:
            data = index.data()
            if data is None:
                return None
            itemType = None[2]
            if itemType == 'artist':
                LPQobuzArtistDetailViewController = LPQobuzArtistDetailViewController
                import HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController
                Ui_qobuzArtistDetailViewWidget = Ui_qobuzArtistDetailViewWidget
                import HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui
                artistPlayItem = LPQobuzPlayItem()
                artistPlayItem.trackId = data[3]
                artistPlayItem.trackName = data[0]
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistPlayItem), 'qobuzdetail')

    __classcell__ = None

