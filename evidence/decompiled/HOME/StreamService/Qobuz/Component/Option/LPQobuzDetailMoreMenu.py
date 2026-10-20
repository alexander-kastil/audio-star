# Source Generated with Decompyle++
# File: LPQobuzDetailMoreMenu.pyc (Python 3.9)

'''
@Time ： 2025/7/25 13:51
@Auth ： Chris
@File ：LPQobuzDetailMoreMenu.py
@Desc:
'''
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication, pyqtSlot, QPoint
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMenu
import LPGlobalUI
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPPublicDefine import LPMSCommonOption
from LPClientFramework.LPUtility import logger
QobuzSupportedCommonOption = [
    LPMSCommonOption.Option_Add_To_Playlist,
    LPMSCommonOption.Option_View_Artist,
    LPMSCommonOption.Option_View_Album]

class LPQobuzDetailMoreMenu(QMenu):
    noOptionSignal = pyqtSignal()
    
    def __init__(self = None, playItem = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.source = LPPlayListSource.Qobuz.value
        self.playItem = playItem

    
    def setupUI(self):
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.noOptionSignal.connect(self._onNoOption)
        self.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                font: 14px;\n                min-width: 150px;               \n            }\n            QMenu::item{\n                border-radius: 3px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                min-width: 130px;\n                margin-left: 8px;\n                margin-right: 8px;\n                margin-top: 5px;\n                margin-bottom: 5px;\n                padding-left: 10px;\n                padding-right: 10px;\n\n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n\n            QMenu::item:hover {\n                background-color: %s;\n            }\n\n            QMenu::item:disabled{\n                color: %s;\n            }\n            QMenu::right-arrow {\n                width: 8px;\n                height: 8px;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))

    
    def buildActions(self, device):
        self.streamService = device.deviceStreamServiceManager.streamServiceForSource(self.source)
        if self.streamService.LPTrackMoreViewControllerCanViewArtist(self.playItem, self.playItem, False, self._canArtistCallback):
            viewArtistActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_View_Artist.value)
            icon = QIcon(LPGlobalUI.imagePath('lib/mymusic_artist.png'))
            self.viewArtistAction = self.addAction(icon, viewArtistActionText)
            self.viewArtistAction.triggered.connect(self.viewArtist)
        if self.streamService.LPTrackMoreViewControllerCanViewAlbum(self.playItem, self.playItem, None, False, self._albumCallback):
            viewAlbumActionText = QCoreApplication.translate('TrackMore', LPMSCommonOption.Option_View_Album.value)
            icon = QIcon(LPGlobalUI.imagePath('lib/mymusic_album.png'))
            self.viewAlbumAction = self.addAction(icon, viewAlbumActionText)
            self.viewAlbumAction.triggered.connect(self.viewAlbum)

    
    def _onNoOption(self):
        logger.debug('_onNoOption')
        noOptionActionText = QCoreApplication.translate('TrackMore', 'No More Options')
        self.addAction(noOptionActionText)

    
    def showMenu(self, pos):
        self.buildActions(LPGlobalUI.currentDevice)
        if not self.actions():
            self.noOptionSignal.emit()
        button_top_right = self.parent.mapToGlobal(self.parent.rect().topRight())
        menu_size = self.sizeHint()
        menu_x = button_top_right.x()
        menu_y = button_top_right.y() - menu_size.height()
        self.exec(QPoint(menu_x, menu_y))

    
    def addToPlaylist(self):
        pass

    addToPlaylist = pyqtSlot()(addToPlaylist)
    
    def viewArtist(self):
        
        def _viewCallback(viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            LPGlobalUI.navigationManager.push(viewController, self.streamService.detailNavigationItemId('artist'))

        self.streamService.LPTrackMoreViewControllerViewArtist(self.playItem, self.playItem, None, _viewCallback)

    viewArtist = pyqtSlot()(viewArtist)
    
    def viewAlbum(self):
        
        def _viewCallback(viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            LPGlobalUI.navigationManager.push(viewController, self.streamService.detailNavigationItemId('album'))

        self.streamService.LPTrackMoreViewControllerViewAlbum(self.playItem, self.playItem, None, _viewCallback)

    viewAlbum = pyqtSlot()(viewAlbum)
    
    def _canArtistCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz detail track --> {self.playItem.trackId} can not view artist''')

    
    def _addPlaylistCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz detail track --> {self.playItem.trackId} can not add to playlist''')

    
    def _albumCallback(self, canView, item):
        if not canView:
            logger.debug(f'''qobuz detail track --> {self.playItem.trackId} can not view album''')

    __classcell__ = None

