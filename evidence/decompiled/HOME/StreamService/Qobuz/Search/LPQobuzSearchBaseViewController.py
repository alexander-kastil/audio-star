# Source Generated with Decompyle++
# File: LPQobuzSearchBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/8/5 18:52
@Auth ： Chris
@File ：LPQobuzSearchBaseViewController.py
@Desc:
'''
import copy
from functools import partial
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCursor
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController, LPQobuzPlayMode
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPClientFramework.LPUtility import logger

class LPQobuzSearchBaseViewController(LPQobuzBaseViewController):
    
    def __init__(self = None):
        super().__init__()

    
    def onFavClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'add' if playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    
    def favoriteCallback(self, changeType, itemId, result):
        status = result.data
        if status == 'success':
            self.qobuz.favMgr.changeFav(changeType, LPHeaderType.LP_HEADER_TYPE_SONG, itemId)
            if changeType == 'add':
                LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Added to Favorites'), LPGlobalUI.mainWindow)
            else:
                LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Removed From Favorites'), LPGlobalUI.mainWindow)
        elif changeType == 'add':
            LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Add Failed'), LPGlobalUI.mainWindow)
        else:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Remove Failed'), LPGlobalUI.mainWindow)

    
    def onOptClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        trackMoreMenu = LPQobuzTrackMoreMenu(playItem, None, self.tableView)
        trackMoreMenu.setupUI()
        trackMoreMenu.showMenu(QCursor.pos())

    
    def onTableViewItemDoubleClick(self, index):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        playList = None.deepcopy(self.tableView.model().playList)
        playItem = playList.list[index.row()]
        playList.list = [
            playItem]
        playList.header.playOrigin = 'search_track'
        xml = playList.generateTrackPlayXML(playList.list, '1')
        self.playQobuzPlayList(playList, playItem, xml, 0, LPQobuzPlayMode.SingleTrack, 'qobuz all content table', playList.header, **('playIndex', 'playMode', 'logPrefix', 'header'))

    
    def onTableViewItemClick(self, index):
        if self.tableView.lastCursorActionIndex:
            data = index.data()
            if data is None:
                return None
            itemType = None[2]
            if itemType == 'artist':
                artistPlayItem = LPQobuzPlayItem()
                artistPlayItem.trackId = data[3]
                artistPlayItem.trackName = data[0]
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistPlayItem), 'qobuzdetail')

    
    def loadData(self):
        self.showLoadingOverlaySignal.emit()

    
    def onDataLoadCallback(self):
        self.hideLoadingOverlaySignal.emit()

    __classcell__ = None

