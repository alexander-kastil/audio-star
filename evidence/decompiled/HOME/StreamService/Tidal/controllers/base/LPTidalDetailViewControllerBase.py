# Source Generated with Decompyle++
# File: LPTidalDetailViewControllerBase.pyc (Python 3.9)

'''
TIDAL 详情页通用控制器。
'''
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QCoreApplication, QMetaObject, Qt, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import LPGlobalUI
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from HOME.StreamService.Tidal.controllers.base.LPTidalPlayController import LPTidalPlayController
from HOME.StreamService.Tidal.controllers.shell.LPTidalShellRouter import pushTidalPage, isCurrentTidalDetailPage
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalCursorBridge, applyTidalSharedQmlContext, clearTidalCursorBridge, resolveTidalQmlUrl
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest, LPTidalRequestScheduler
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from HOME.StreamService.Tidal.services.LPTidalNetworkDiagnostics import installTidalQmlNetworkDiagnostics
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPPlayList.LPTidalPlayList import LPTidalPlayList
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPPresetMenu import LPPresetMenu

class LPTidalDetailViewControllerBase(QWidget, LPTidalPlayController):
    '''TIDAL 详情页基类，统一承载 QML、调度请求和详情路由。'''
    shuffleStateChanged = pyqtSignal()
    
    def __init__(self = None, itemId = None, itemType = None, state = None, qmlPath = None, qmlFileName = None, specificContextName = None, parent = None):
        '''
        初始化详情页通用控制器。

        :param itemId: 条目 ID。
        :param itemType: 条目类型。
        :param state: 详情状态对象。
        :param qmlPath: qrc QML 路径。
        :param qmlFileName: 本地 QML 文件名。
        :param specificContextName: 注入 QML 的专用上下文名。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        if not itemId:
            pass
        self._item_id = str('').strip()
        if not itemType:
            pass
        self._item_type = str('').strip().lower()
        self._state = state
        if not qmlPath:
            pass
        self._qml_path = str('')
        if not qmlFileName:
            pass
        self._qml_file_name = str('')
        if not specificContextName:
            pass
        self._specific_context_name = str('')
        self._store = LPTidalStore.instance()
        self._provider = LPTidalDataProvider()
        self._scheduler = LPTidalRequestScheduler(self)
        self._ui_detached = False
        self._is_shuffle = self._readShufflePreference()
        self._state_active = False
        self.quickWidget = None
        self._preset_anchor = None
        self.deleteOnPrune = True
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._onDestroyed)
        self._setup_qml_page()
        self._ensure_state_active()
        self.reload()

    
    def isShuffle(self = None):
        '''
        返回当前详情页是否启用随机播放偏好。

        :return: 启用返回 True。
        '''
        return bool(self._is_shuffle)

    isShuffle = None(isShuffle)
    
    def __del__(self):
        '''
        析构时兜底失活详情状态。

        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _onDestroyed(self = None, destroyedObject = None):
        '''
        QObject 销毁回调。

        :param destroyedObject: Qt 销毁信号透传对象。
        :return: None。
        '''
        _ = destroyedObject
        self._ui_detached = True
        clearTidalCursorBridge(self)
        self.unregisterTidalDeviceInfoObserver()
        self._shutdown_scheduler()
        self._ensure_state_inactive()

    
    def viewWillAppear(self = None):
        '''
        页面显示时激活详情状态，未登录时先统一跳转登录页。

        :return: None。
        '''
        self._ui_detached = False
        if not LPTidalLoginManager.instance().ensureTidalLoggedInOrShowLogin():
            return None
        None._ensure_state_active()
        self.registerTidalDeviceInfoObserver()
        self._syncVisibleRange()

    
    def viewWillDisappear(self = None):
        '''
        页面隐藏时失活详情状态。

        :return: None。
        '''
        self._ui_detached = True
        clearTidalCursorBridge(self)
        self.unregisterTidalDeviceInfoObserver()
        cancel_owner = getattr(self._state, 'cancelImageOwner', None)
        if callable(cancel_owner):
            cancel_owner()
        self._ensure_state_inactive()
        self._shutdown_scheduler()

    
    def _syncVisibleRange(self = None):
        '''
        请求 QML 重新同步详情页可见范围。

        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is not None and root.metaObject().indexOfMethod(b'syncVisibleRange()') >= 0:
            QMetaObject.invokeMethod(root, 'syncVisibleRange', Qt.ConnectionType.QueuedConnection)

    
    def reload(self = None):
        '''
        重新加载详情数据。

        :return: None。
        '''
        if not self._item_id:
            self._state.setErrorMessage('Missing item id.')
            self._state.setLoading(False)
            return None
        None._state.setLoading(True)
        self._state.setErrorMessage('')
        request = LPTidalRequest(f'''detail::{self._item_type}::{self._item_id}''', self._request_tag(), self._fetchDetailData, self._handleDetailResult, **('key', 'tag', 'task', 'callback'))
        scheduler = self._ensure_scheduler()
        scheduler.cancelByTag(request.tag)
        scheduler.enqueue(request, 0, **('priority',))

    reload = None(reload)
    
    def onCardClicked(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        处理详情页内卡片点击。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :return: None。
        '''
        self.pushDetailPage(self, itemType, itemId)

    onCardClicked = None(onCardClicked)
    
    def updateDetailTrackVisibleRange(self = None, firstIndex = None, lastIndex = pyqtSlot(int, int)):
        '''
        更新详情页曲目列表可见范围。

        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        update_method = getattr(self._state, 'updateTrackVisibleRange', None)
        if callable(update_method):
            update_method(firstIndex, lastIndex)

    updateDetailTrackVisibleRange = None(updateDetailTrackVisibleRange)
    
    def onArtistClicked(self = None, artistId = None):
        '''
        处理卡片副标题或列表列中的艺人名称点击，跳转对应艺人详情页（push 新页面）。

        :param artistId: 艺人 ID。
        :return: None。
        '''
        if not artistId:
            pass
        normalized = str('').strip()
        if normalized:
            logger.debug('[TIDAL] artist sub-click artistId=%s', normalized)
            self.pushDetailPage(self, 'artist', normalized)

    onArtistClicked = None(onArtistClicked)
    
    def onAlbumClicked(self = None, albumId = None):
        '''
        处理卡片副标题或列表列中的专辑名称点击，跳转对应专辑详情页（push 新页面）。

        :param albumId: 专辑 ID。
        :return: None。
        '''
        if not albumId:
            pass
        normalized = str('').strip()
        if normalized:
            logger.debug('[TIDAL] album sub-click albumId=%s', normalized)
            self.pushDetailPage(self, 'album', normalized)

    onAlbumClicked = None(onAlbumClicked)
    
    def onSeeAllClicked(self = None, sectionKey = None):
        '''
        处理详情页内 See All 点击。

        :param sectionKey: 区块标识。
        :return: None。
        '''
        descriptor = self._descriptorForGenreSection(sectionKey)
        if descriptor is None:
            logger.debug('[TIDAL] detail see all unsupported section=%s itemType=%s', sectionKey, self._item_type)
            return None
        LPTidalSeeAllViewController = LPTidalSeeAllViewController
        import HOME.StreamService.Tidal.controllers.pages.LPTidalSeeAllViewController
        pushTidalPage(self, LPTidalSeeAllViewController(descriptor, self), 'tidal_see_all')

    onSeeAllClicked = None(onSeeAllClicked)
    
    def toggleFavorite(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        切换详情页条目收藏状态。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :return: None。
        '''
        desired_favorite = not self._store.favoriteState.isFavorite(itemType, itemId)
        self.setFavorite(itemType, itemId, desired_favorite)

    toggleFavorite = None(toggleFavorite)
    
    def setFavorite(self = None, itemType = None, itemId = pyqtSlot(str, str, bool), desiredFavorite = {
        'itemType': str,
        'itemId': str,
        'desiredFavorite': bool,
        'return': None }):
        '''
        设置详情页条目收藏目标状态。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :param desiredFavorite: 目标收藏状态。
        :return: None。
        '''
        account = self._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        if not user_id:
            logger.debug('[TIDAL] favorite ignored because user is not logged in')
            self._store.toastState.showToast('Please log in to manage favorites.', 'error')
            return None
        if not itemType:
            pass
        normalized_item_type = None('').strip().lower()
        if not itemId:
            pass
        normalized_item_id = str('').strip()
        if not normalized_item_id:
            return None
        LPTidalFavoriteService = LPTidalFavoriteService
        import HOME.StreamService.Tidal.services.LPTidalFavoriteService
        LPTidalFavoriteService.instance().setFavorite(normalized_item_type, normalized_item_id, bool(desiredFavorite), self._onFavoriteResult)

    setFavorite = None(setFavorite)
    
    def _showFavoriteToast(self = None, desiredFavorite = None, success = None):
        '''
        展示详情页收藏操作结果 Toast。

        :param desiredFavorite: 目标收藏状态。
        :param success: 操作是否成功。
        :return: None。
        '''
        if success:
            message = 'Added to Favorites' if desiredFavorite else 'Removed From Favorites'
            self._store.toastState.showToast(message, 'success')
            return None
        message = 'Add Failed' if None else 'Remove Failed'
        self._store.toastState.showToast(message, 'error')

    
    def _applyFavoriteStateLocally(self = None, itemType = None, itemId = None, isFavorite = {
        'itemType': str,
        'itemId': str,
        'isFavorite': bool,
        'return': None }):
