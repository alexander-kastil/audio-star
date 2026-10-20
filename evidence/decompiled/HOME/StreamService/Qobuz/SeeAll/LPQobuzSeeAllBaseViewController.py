# Source Generated with Decompyle++
# File: LPQobuzSeeAllBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/8 14:36
@Auth ： Chris
@File ：LPQobuzDetailBaseViewController.py
@Desc:
'''
from LPClientFramework.LPUtility import logger
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QModelIndex, QCoreApplication
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistListModel, LPQobuzPlaylistDelegate

class LPQobuzSeeAllBaseViewController(LPQobuzBaseViewController):
    loadDataSignal = pyqtSignal(object, object)
    initListViewSignal = pyqtSignal(object, object)
    listViewAddDataSignal = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.offset = 0
        self.total = self.defaultTotal
        self.limit = self.defaultLimit
        self.itemId = None
        self.playItem = None
        self.playList = None
        self.loadDataSignal.connect(self._loadData)
        self.genreSnapshot = ''
        self.initListViewSignal.connect(self._initListView)
        self.listViewAddDataSignal.connect(self._addData)

    
    def _initListView(self, headType, playList):
        self.playList = playList
        if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            model = LPQobuzListModel(self.playList, self.listView)
            delegate = LPQobuzAlbumDelegate(self.listView)
        elif headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            model = LPQobuzPlaylistListModel(self.playList, self.listView)
            delegate = LPQobuzPlaylistDelegate(self.listView)
        self.listView.setModel(model)
        self.listView.setItemDelegate(delegate)

    
    def _addData(self, playList):
        model = self.listView.model()
        if model:
            model.addItemList(playList)

    
    def needRefresh(self):
        if self.playList and self.genreSnapshot == self.disGenreManager.getSelectedGenreStr():
            return False

    
    def checkMore(self):
        if self.offset >= self.total:
            return False

    
    def _loadData(self, genres, binding):
        pass

    _loadData = pyqtSlot(object, object)(_loadData)
    
    def onListViewItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        if None.isAlbum:
            streamable = playItem.streamable
            if not streamable:
                LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz fav album see all', 'This album is not available'), LPGlobalUI.mainWindow)
                logger.debug('qobuz album %s not streamable' % playItem.trackName)
                return None
            LPQobuzAlbumDetailViewController = LPQobuzAlbumDetailViewController
            import HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController
            Ui_qobuzAlbumDetailViewWidget = Ui_qobuzAlbumDetailViewWidget
            import HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, playItem), 'qobuzdetail')
        elif playItem.isPlaylist:
            LPQobuzPlaylistDetailViewController = LPQobuzPlaylistDetailViewController
            import HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController
            Ui_qobuzPlaylistDetailViewWidget = Ui_qobuzPlaylistDetailViewWidget
            import HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistDetailViewControllerUI, Ui_qobuzPlaylistDetailViewWidget, LPQobuzPlaylistDetailViewController, playItem), 'qobuzdetail')
        elif playItem.isArtist:
            LPQobuzArtistDetailViewController = LPQobuzArtistDetailViewController
            import HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController
            Ui_qobuzArtistDetailViewWidget = Ui_qobuzArtistDetailViewWidget
            import HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, playItem), 'qobuzdetail')

    __classcell__ = None

