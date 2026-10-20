# Source Generated with Decompyle++
# File: LPQobuzTrackMoreMenu.pyc (Python 3.9)

'''
@Time ： 2025/7/24 18:21
@Auth ： Chris
@File ：LPQobuzTrackMoreMenu.py
@Desc:
'''
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMenu, QDialog
import LPGlobalUI
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPPublicDefine import LPMSCommonOption
from LPClientFramework.LPUtility import logger
QobuzSupportedCommonOption = [
    LPMSCommonOption.Option_Add_To_Playlist,
    LPMSCommonOption.Option_View_Artist,
    LPMSCommonOption.Option_View_Album]

class LPQobuzTrackMoreMenu(QMenu):
    noOptionSignal = pyqtSignal()
    removeFromPlaylistSignal = pyqtSignal(object)
    
    def __init__(self = None, playItem = None, parentPlayItem = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.source = LPPlayListSource.Qobuz.value
        self.playItem = playItem
        self.header = parentPlayItem
        self.qobuz = LPQobuzManager.instance()

    
    def setupUI(self):
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.noOptionSignal.connect(self._onNoOption)
        self.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                font: 14px;\n                min-width: 150px;               \n            }\n            QMenu::item{\n                border-radius: 3px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                min-width: 130px;\n                margin-left: 8px;\n                margin-right: 8px;\n                margin-top: 5px;\n                margin-bottom: 5px;\n                padding-left: 10px;\n                padding-right: 10px;\n\n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n\n            QMenu::item:hover {\n                background-color: %s;\n            }\n\n            QMenu::item:disabled{\n                color: %s;\n            }\n            QMenu::right-arrow {\n                width: 8px;\n                height: 8px;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))

    
    def buildActions(self, device):
        self.streamService = device.deviceStreamServiceManager.streamServiceForSource(self.source)
        if self.streamService.LPTrackMoreViewControllerCanViewArtist(self.header, self.playItem, False, self._canArtistCallback):
            viewArtistActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_View_Artist.value)
            icon = QIcon(LPGlobalUI.imagePath('lib/mymusic_artist.png'))
            self.viewArtistAction = self.addAction(icon, viewArtistActionText)
            self.viewArtistAction.triggered.connect(self.viewArtist)
        if self.streamService.LPTrackMoreViewControllerCanViewAlbum(self.header, self.playItem, None, False, self._albumCallback):
            viewAlbumActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_View_Album.value)
            icon = QIcon(LPGlobalUI.imagePath('lib/mymusic_album.png'))
            self.viewAlbumAction = self.addAction(icon, viewAlbumActionText)
            self.viewAlbumAction.triggered.connect(self.viewAlbum)
        if self.streamService.LPTrackMoreViewControllerCanAddToPlaylist(self.header, self.playItem, None, False, self._albumCallback):
            addToPlaylistActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_Add_To_Playlist.value)
            icon = QIcon(LPGlobalUI.imagePath('icon_playlist.png'))
            self.addToPlaylistAction = self.addAction(icon, addToPlaylistActionText)
            self.addToPlaylistAction.triggered.connect(self.addToPlaylist)
        if self.streamService.LPTrackMoreViewControllerCanRemoveFromPlaylist(self.header, self.playItem, self.qobuz.loginMgr.account, False, self._albumCallback):
            removeFromPlaylistActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_Remove_From_Playlist.value)
            icon = QIcon(LPGlobalUI.imagePath('icon_remove.png'))
            self.removeFromPlaylistAction = self.addAction(icon, removeFromPlaylistActionText)
            self.removeFromPlaylistAction.triggered.connect(self.removeFromPlaylist)

    
    def _onNoOption(self):
        logger.debug('_onNoOption')
        noOptionActionText = QCoreApplication.translate('TrackMore', 'No More Options')
        self.addAction(noOptionActionText)

    
    def showMenu(self, pos):
        self.buildActions(LPGlobalUI.currentDevice)
        if not self.actions():
            self.noOptionSignal.emit()
        self.popup(pos)

    
    def addToPlaylist(self):
        
        def _viewCallback(viewController):
            if isinstance(viewController, QDialog):
                viewController.exec()

        self.streamService.LPTrackMoreViewControllerAddToPlaylist(self.header, self.playItem, None, _viewCallback)

    addToPlaylist = pyqtSlot()(addToPlaylist)
    
    def removeFromPlaylist(self):
        
        def _viewCallback(viewController = None):
            self.removeFromPlaylistSignal.emit(self.playItem)

        self.streamService.LPTrackMoreViewControllerRemoveFromPlaylist(self.header, self.playItem, self.parent, _viewCallback)

    removeFromPlaylist = pyqtSlot()(removeFromPlaylist)
    
    def viewArtist(self):
        
        def _viewCallback(viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            LPGlobalUI.navigationManager.push(viewController, self.streamService.detailNavigationItemId('artist'))

        self.streamService.LPTrackMoreViewControllerViewArtist(self.header, self.playItem, None, _viewCallback)

    viewArtist = pyqtSlot()(viewArtist)
    
    def viewAlbum(self):
        
        def _viewCallback(viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            LPGlobalUI.navigationManager.push(viewController, self.streamService.detailNavigationItemId('album'))

        self.streamService.LPTrackMoreViewControllerViewAlbum(self.header, self.playItem, None, _viewCallback)

    viewAlbum = pyqtSlot()(viewAlbum)
    
    def _canArtistCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz track --> {self.playItem.trackId} can not view artist''')

    
    def _addPlaylistCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz track --> {self.playItem.trackId} can not add to playlist''')

    
    def _albumCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz track --> {self.playItem.trackId} can not view album''')

    __classcell__ = None

