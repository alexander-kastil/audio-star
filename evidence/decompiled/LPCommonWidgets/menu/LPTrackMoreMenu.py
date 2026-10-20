# Source Generated with Decompyle++
# File: LPTrackMoreMenu.pyc (Python 3.9)

'''
@Time ： 2025/3/31 18:32
@Auth ： Chris
@File ：LPTrackMoreMenu.py
@Desc:
'''
from functools import partial
from PyQt6.QtCore import QCoreApplication, QPoint, pyqtSignal, pyqtSlot, Qt, QSize
from PyQt6.QtGui import QAction, QFontMetrics
from PyQt6.QtWidgets import QMenu
import LPGlobalUI
from LPClientFramework import LPStreamServiceManager
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPPresetMenu import LPPresetMenu

class LPTrackMoreMenu(QMenu):
    '''minibar 当前播放更多菜单。'''
    noOptionSignal = pyqtSignal()
    closePlayViewSignal = pyqtSignal()
    
    def __init__(self = None, source = None, parent = None):
        '''初始化当前播放更多菜单。

        :param source: 当前播放音源。
        :param parent: 菜单宿主控件。
        :returns: None。
        '''
        super().__init__(parent)
        self.parent = parent
        self.source = source
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.noOptionSignal.connect(self._onNoOption)
        self.closePlayViewSignal.connect(self._closePlayView)
        self.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                font-family: "%s";\n                font-size: 14px;\n                min-width: 150px;               \n            }\n            QMenu::item{\n                border-radius: 3px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                min-width: 130px;\n                margin-left: 5px;\n                margin-right: 5px;\n                padding-left: 5px;\n                padding-right: 5px;\n\n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n\n            QMenu::item:hover {\n                background-color: %s;\n            }\n\n            QMenu::item:disabled{\n                color: %s;\n            }\n            QMenu::right-arrow {\n                width: 8px;\n                height: 8px;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), getFontFamily(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
        device = LPGlobalUI.currentDevice
        if not device:
            return None
        if None.source == 'PC_RemoteLocal':
            self.streamService = LPStreamServiceManager.streamServiceForSource(self.source)
        else:
            self.streamService = device.deviceStreamServiceManager.streamServiceForSource(self.source)
        if not self.streamService:
            return None
        self.currentPlayItem = None.streamService.currentPlayItem(LPGlobalUI.currentDevice)
        self.currentPlayHeader = self.streamService.currentPlayHeader(LPGlobalUI.currentDevice)
        if self.streamService.LPTrackMoreViewControllerCanViewArtist(self.currentPlayHeader, self.currentPlayItem, False, self._artistCallback):
            viewArtistActionText = QCoreApplication.translate('TrackMore', 'View Artist')
            self.viewArtistAction = self.addAction(viewArtistActionText)
            self.viewArtistAction.triggered.connect(self.viewArtist)
        if self.streamService.LPTrackMoreViewControllerCanViewAlbum(self.currentPlayHeader, self.currentPlayItem, self.artistItem, False, None):
            viewAlbumActionText = QCoreApplication.translate('TrackMore', 'View Album')
            self.viewAlbumAction = self.addAction(viewAlbumActionText)
            self.viewAlbumAction.triggered.connect(self.viewAlbum)
        if self.streamService.LPTrackMoreCanPreset(device):
            presetMenu = LPPresetMenu(self, getattr(device.mediaInfo, 'playSection', None), **('playSection',))
            presetTitle = QCoreApplication.translate('TrackMore', 'Preset')
            presetMenu.setTitle(presetTitle)
            self.addMenu(presetMenu)

    
    def _onNoOption(self):
        logger.debug('_onNoOption')
        noOptionActionText = QCoreApplication.translate('TrackMore', 'No More Options')
        self.addAction(noOptionActionText)

    
    def showMenu(self):
        button_top_right = self.parent.mapToGlobal(self.parent.rect().topRight())
        menu_size = self.sizeHint()
        menu_x = button_top_right.x()
        menu_y = button_top_right.y() - menu_size.height()
        if not self.actions():
            self.noOptionSignal.emit()
        self.exec(QPoint(menu_x, menu_y))

    
    def set_elided_action_text(self, action, max_width):
        '''超出部分设置省略号'''
        font = action.font()
        font_metrics = QFontMetrics(font)
        elided_text = font_metrics.elidedText(action.text(), Qt.TextElideMode.ElideRight, max_width)
        action.setText(elided_text)

    
    def viewArtist(self):
        
        def _viewCallback(parent = None, viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            itemId = self.streamService.detailNavigationItemId('artist')
            LPGlobalUI.navigationManager.push(viewController, itemId)
            if LPGlobalUI.mainWindow.playViewController.isAncestorOf(parent):
                self.closePlayViewSignal.emit()

        callback = partial(_viewCallback, self.parent)
        self.streamService.LPTrackMoreViewControllerViewArtist(self.currentPlayHeader, self.currentPlayItem, None, callback)

    viewArtist = pyqtSlot()(viewArtist)
    
    def viewAlbum(self):
        
        def _viewCallback(parent = None, viewController = None):
            if type(LPGlobalUI.getTopWidget()) == type(viewController):
                LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
            itemId = self.streamService.detailNavigationItemId('album')
            LPGlobalUI.navigationManager.push(viewController, itemId)
            if LPGlobalUI.mainWindow.playViewController.isAncestorOf(parent):
                self.closePlayViewSignal.emit()

        callback = partial(_viewCallback, self.parent)
        self.streamService.LPTrackMoreViewControllerViewAlbum(self.currentPlayHeader, self.currentPlayItem, None, callback)

    viewAlbum = pyqtSlot()(viewAlbum)
    
    def _artistCallback(self, canView, artistItem):
        self.canViewAritst = canView
        self.artistItem = artistItem

    
    def _closePlayView(self):
        LPGlobalUI.mainWindow.playViewCloseMethod(True, **('ignoreFullScreen',))

    __classcell__ = None

