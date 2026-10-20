# Source Generated with Decompyle++
# File: LPTidalAddToPlaylistDialogHost.pyc (Python 3.9)

'''
TIDAL Add-to-playlist 全局 QML 对话框宿主。
'''
from typing import Optional
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QDialog, QVBoxLayout
import LPGlobalUI
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalSharedQmlContext, resolveTidalQmlPath
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPUtility import logger

class LPTidalAddToPlaylistDialogHost(QDialog):
    '''承载全局 Add-to-playlist QML 对话框，供 Queue TrackMore 等入口复用。'''
    _instance: Optional['LPTidalAddToPlaylistDialogHost'] = None
    
    def __init__(self = None, parent = None):
        '''
        初始化对话框宿主。

        :param parent: 父级窗口。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPTidalStore.instance()
        self.setModal(True)
        self.setWindowTitle('Add to playlist')
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(600, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._quick_widget = QQuickWidget(self)
        self._quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self._quick_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._quick_widget.setClearColor(Qt.GlobalColor.transparent)
        ctx = self._quick_widget.rootContext()
        applyTidalSharedQmlContext(ctx)
        ctx.setContextProperty('tidalStore', self._store)
        ctx.setContextProperty('sharedStore', self._store)
        ctx.setContextProperty('playlistManager', self._store.playlistManager)
        local_qml = resolveTidalQmlPath('dialogs/TidalAddToPlaylistDialog.qml')
        if local_qml.exists():
            self._quick_widget.setSource(QUrl.fromLocalFile(str(local_qml)))
        else:
            self._quick_widget.setSource(QUrl('qrc:/qml/Tidal/dialogs/TidalAddToPlaylistDialog.qml'))
        root_object = self._quick_widget.rootObject()
        if root_object is not None:
            root_object.setProperty('playlistManager', self._store.playlistManager)
        if self._quick_widget.status() != QQuickWidget.Status.Ready:
            for err in self._quick_widget.errors():
                logger.error('[TIDAL] AddToPlaylist dialog load failed: %s', err.toString())
        layout.addWidget(self._quick_widget)
        self._store.playlistManager.addToPlaylistState.visibleChanged.connect(self._syncVisibility)

    
    def instance(cls = None):
        '''
        返回全局对话框宿主单例。

        :return: 对话框宿主实例。
        '''
        if cls._instance is None:
            parent = getattr(LPGlobalUI, 'mainWindow', None)
            cls._instance = cls(parent)
        return cls._instance

    instance = None(instance)
    
    def _syncVisibility(self = None):
        '''
        根据状态对象同步对话框显示。

        :return: None。
        '''
        state = self._store.playlistManager.addToPlaylistState
        if bool(state.visible):
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            self.hide()

    
    def showForTrack(self = None, trackId = None, trackTitle = None):
        '''
        为指定曲目打开对话框。

        :param trackId: 曲目 ID。
        :param trackTitle: 曲目标题。
        :return: None。
        '''
        self._store.playlistManager.openAddToPlaylist(trackId, trackTitle)
        self._syncVisibility()

    __classcell__ = None

