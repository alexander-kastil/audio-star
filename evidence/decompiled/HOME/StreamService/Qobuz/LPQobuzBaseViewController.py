# Source Generated with Decompyle++
# File: LPQobuzBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/30 16:10
@Auth ： Chris
@File ：LPQobuzBaseViewController.py
@Desc:
'''
import enum
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QCoreApplication
from PyQt6.QtWidgets import QWidget, QListView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenreManager import LPQobuzGenreManager
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import UIText
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPMusicLibrary.LPRecentlyManager import LPRecentlyManager
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPNetworkClient.LPRequestCounter import LPRequestCounter
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzAccount, LPQobuzPlayHeader, LPQobuzPlayItem, LPQobuzPlayList, RECENTLY_FAVORITE_TRACKS_ID, RECENTLY_PURCHASED_TRACKS_ID
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.page.LPLoadingOverlay import LPLoadingOverlay
from LPCommonWidgets.page.LPMSNoNetworkPage import LPMSNoNetworkPage
from LPCommonWidgets.page.LPMS4xxErrorPage import LPMS4xxErrorPage
from LPCommonWidgets.page.UI.LPLoadingOverlay_ui import Ui_loadingOverlay
from LPCommonWidgets.page.UI.LPMS4xxErrorPage_ui import Ui_MS4xxErrorWidget
from LPCommonWidgets.page.UI.LPMSNoNetworkPage_ui import Ui_MSNoNetworkWidget

class LPQobuzPlayMode(enum.Enum):
    Normal = 0
    SingleTrack = 1


class PlaylistIDCacheType(enum.Enum):
    PLAYLIST_ID = 'playlistID'


class LPQobuzBaseViewController(QWidget):
    updatePlaylistIdCacheSignal = pyqtSignal()
    updatePlaylistIdCompleteSignal = pyqtSignal()
    upnpModel = LPUpnpAsyncDataModel()
    disGenreManager = LPQobuzGenreManager()
    libGenreManager = LPQobuzGenreManager()
    showLoadingOverlaySignal = pyqtSignal()
    hideLoadingOverlaySignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        self.source = LPPlayListSource.Qobuz.value
        self.qobuz = LPQobuzManager.instance()
        self.seeAllText = QCoreApplication.translate('qobuz browse', UIText.See_All.value)
        self.offset = 0
        self.defaultTotal = 16777215
        self.defaultLimit = 50
        self.maxLimit = 500
        self.listViewDefaultSpacing = 5
        self.listViewDefaultFlow = QListView.Flow.LeftToRight
        self.playlistIds = []
        self.updatePlaylistIdOffset = 0
        self.updatePlaylistIdLimit = 500
        self.updatePlaylistIdTotal = 0
        self.updatePlaylistIdCacheSignal.connect(self.updatePlaylistIdCache)
        self.updatePlaylistIdCompleteSignal.connect(self.updatePlaylistIdComplete)
        self.qobuz.favMgr.favLoadSignal.connect(self._onQobuzFavoriteCacheChanged)
        self.qobuz.requestMgr.http4xxErrorSignal.connect(self.on4xxError)
        self.requestCount = -1
        self.requestCounter = LPRequestCounter(self)
        self.requestCounter.pageErrorSignal.connect(self.onPageError)
        self.loadingOverlay = LPGlobalUI.loadUI(LPUIPath.LPLoadingOverlayUI, Ui_loadingOverlay, LPLoadingOverlay, self)
        self.showLoadingOverlaySignal.connect(self.showLoadingOverlay)
        self.hideLoadingOverlaySignal.connect(self.hideLoadingOverlay)

    
    def showLoadingOverlay(self):
        self.loadingOverlay.showOverlay()

    
    def hideLoadingOverlay(self):
        self.loadingOverlay.hideOverlay()

    
    def onPageError(self):
        logger.debug('[qobuz] page time out ')
        noNetworkPage = LPGlobalUI.loadUI(LPUIPath.MSNoNetworkPageUI, Ui_MSNoNetworkWidget, LPMSNoNetworkPage, self.source)
        LPGlobalUI.navigationManager.push(noNetworkPage, 'qobuz no network')

    
    def listViewWheelEvent(self, event):
        event.ignore()

    
    def favoriteCallback(self, changeType, itemType, itemId, result):
        pass
    # WARNING: Decompyle incomplete

    
    def favFavoriteCallback(self, itemId, result):
        status = result.data
        changeType = 'delete'
        itemType = LPHeaderType.LP_HEADER_TYPE_SONG
        if status == 'success':
            self.qobuz.favMgr.changeFav(changeType, itemType, itemId)
            LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Removed From Favorites'), LPGlobalUI.mainWindow)

    
    def checkPlayListFavorite(self, playList):
        '''按本地收藏缓存同步列表中的曲目收藏状态，不依赖投影是否已初始化。'''
        if not playList or playList.list:
            return None
        favoriteTrackIdList = None.qobuz.favMgr.getFavIds(LPHeaderType.LP_HEADER_TYPE_SONG)
        if favoriteTrackIdList is None:
            return None
        for playItem in None.list:
            playItem.isFavorite = str(playItem.trackId) in favoriteTrackIdList

    
    def checkPlayListAllFavorite(self, playList):
        if playList.list:
            for playItem in playList.list:
                playItem.isFavorite = True

    
    def _onQobuzFavoriteCacheChanged(self):
        '''收藏缓存变化后刷新当前页面的收藏显示。'''
        self.refreshFavoriteStatus()

    
    def refreshFavoriteStatus(self):
        '''按最新收藏缓存刷新当前页面曲目行的收藏显示；子类可按页面结构覆写。'''
        playList = getattr(self, 'playList', None)
        if playList is not None:
            self.checkPlayListFavorite(playList)
        table_view = getattr(self, 'tableView', None)
        if table_view is not None:
            table_view.update()

    
    def updatePlaylistIdCache(self):
        
        def callback(playList = None):
            self.updatePlaylistIdTotal = playList.header.total
            if not playList.list:
                return None
            playlistIds = (lambda 