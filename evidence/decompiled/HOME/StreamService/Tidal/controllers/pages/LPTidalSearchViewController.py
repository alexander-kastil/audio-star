# Source Generated with Decompyle++
# File: LPTidalSearchViewController.pyc (Python 3.9)

'''
TIDAL 搜索页控制器。
'''
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QMetaObject, Qt, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import LPGlobalUI
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.controllers.pages.LPTidalLoginViewController import LPTidalLoginViewController
from HOME.StreamService.Tidal.controllers.base.LPTidalPlayController import LPTidalPlayController
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalCursorBridge, applyTidalSharedQmlContext, clearTidalCursorBridge, resolveTidalQmlUrl
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest, LPTidalRequestScheduler
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from HOME.StreamService.Tidal.services.LPTidalNetworkDiagnostics import installTidalQmlNetworkDiagnostics
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPMSManager.Tidal.LPTidalFavoriteManager import LPTidalFavoriteManager
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPUtility import logger

class LPTidalSearchViewController(QWidget, LPTidalPlayController):
    '''TIDAL 搜索页宿主，负责搜索动作、结果分发和 QML 加载。'''
    SEARCH_TYPE_BY_FILTER = {
        'artists': 'ARTISTS',
        'albums': 'ALBUMS',
        'tracks': 'TRACKS',
        'playlists': 'PLAYLISTS' }
    
    def __init__(self = None, parent = None, shellEmbedded = None):
        '''
        初始化搜索页控制器。

        :param parent: 父级 QWidget。
        :param shellEmbedded: 是否嵌入到 TIDAL Shell 内容区。
        :return: None。
        '''
        super().__init__(parent)
        self._shell_embedded = bool(shellEmbedded)
        self._store = LPTidalStore.instance()
        self._state = self._store.searchState
        self._provider = LPTidalDataProvider()
        self._favorite_manager = LPTidalFavoriteManager(self)
        self._scheduler = LPTidalRequestScheduler(self)
        self._ui_detached = False
        self._state_active = False
        self._search_revision = 0
        self.quickWidget = None
        self.deleteOnPrune = True
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._onDestroyed)
        self._setup_qml_page()
        self._ensure_state_active()

    
    def __del__(self):
        '''
        析构时兜底失活搜索状态。

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
        页面显示时激活搜索状态，未登录时先统一跳转登录页。

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
        页面隐藏时失活搜索状态。

        :return: None。
        '''
        self._ui_detached = True
        clearTidalCursorBridge(self)
        self.unregisterTidalDeviceInfoObserver()
        self._state.cancelImageOwner()
        self._ensure_state_inactive()
        self._shutdown_scheduler()

    
    def _syncVisibleRange(self = None):
        '''
        请求 QML 重新同步搜索结果可见范围。

        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is not None:
            QMetaObject.invokeMethod(root, 'syncVisibleRange', Qt.ConnectionType.QueuedConnection)

    
    def onLoginClicked(self = None):
        '''
        打开 TIDAL 登录页。

        :return: None。
        '''
        LPGlobalUI.navigationManager.push(LPTidalLoginViewController(self), 'tidal_login')

    onLoginClicked = None(onLoginClicked)
    
    def setSearchText(self = None, text = None):
        '''
        更新搜索文本。

        :param text: 搜索文本。
        :return: None。
        '''
        self._state.setSearchText(text)

    setSearchText = None(setSearchText)
    
    def triggerSearch(self = None):
        '''
        使用 `/v1/search/top-hits/` 执行搜索并拆分分类结果。

        :return: None。
        '''
        if not self._state.searchText:
            pass
        query = str('').strip()
        logger.info('[TIDAL] trigger search query=%s', query)
        if not query:
            self._search_revision += 1
            self._state.setErrorMessage('')
            self._state.setLoading(False)
            self._state.clearResults()
            return None
        None._search_revision += 1
        revision = self._search_revision
        self._state.setLoading(True)
        self._state.setErrorMessage('')
        request = None(None, None, None, (lambda result = None, searchRevision = None: self._handleSearchResult(searchRevision, result)), **('key', 'tag', 'task', 'callback'))
        scheduler = self._ensure_scheduler()
        scheduler.cancelByTag('tidal_search')
        scheduler.enqueue(request, 0, **('priority',))

    triggerSearch = None(triggerSearch)
    
    def onSearchFilterChanged(self = None, filterKey = None):
        '''
        切换 Top、Artists、Albums、Tracks、Playlists 结果视图。

        :param filterKey: 筛选项标识。
        :return: None。
        '''
        self._state.setSearchFilter(filterKey)

    onSearchFilterChanged = None(onSearchFilterChanged)
    
    def onCardClicked(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        处理搜索结果点击。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :return: None。
        '''
        if not itemType:
            pass
        if str('').strip().lower() == 'track':
            if not self.playTidalSearchTrack(itemId):
                logger.debug(f'''[TIDAL] search track play failed itemId={itemId}''')
            return None
        if not None.pushDetailPage(self, itemType, itemId):
            logger.debug(f'''[TIDAL] search item clicked type={itemType}, itemId={itemId}''')

    onCardClicked = None(onCardClicked)
    
    def onPlayClicked(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        处理搜索结果媒体卡片封面播放按钮点击。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :return: None。
        '''
        if not itemType:
            pass
        normalized_type = str('').strip().lower()
        if not itemId:
            pass
        normalized_id = str('').strip()
        if not normalized_id:
            return None
        if None.toggleCurrentPlaybackForItem(normalized_type, normalized_id):
            return None
        if None == 'track':
            if not self.playTidalSearchTrack(normalized_id):
                logger.debug('[TIDAL] search card play track failed itemId=%s', normalized_id)
            return None
        if None in frozenset({'album', 'mix', 'playlist'}):
            if not self.playTidalMediaQueue(normalized_type, normalized_id):
                logger.debug('[TIDAL] search card media queue play failed type=%s itemId=%s', normalized_type, normalized_id)
            return None
        None.onCardClicked(normalized_type, normalized_id)

    onPlayClicked = None(onPlayClicked)
    
    def toggleFavorite(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        切换搜索卡片收藏状态。

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
        设置搜索卡片收藏目标状态。

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
    
    def onArtistClicked(self = None, artistId = None):
        '''
        搜索结果表格/卡片副标题艺人点击，push 艺人详情新页。

        :param artistId: 艺人 ID。
        :return: None。
        '''
        if not artistId:
            pass
        normalized = str('').strip()
        if normalized:
            logger.debug('[TIDAL] search artist sub-click %s', normalized)
            LPTidalDetailViewControllerBase.pushDetailPage(self, 'artist', normalized)

    onArtistClicked = None(onArtistClicked)
    
    def onAlbumClicked(self = None, albumId = None):
        '''
        搜索结果表格/卡片副标题专辑点击，push 专辑详情新页。

        :param albumId: 专辑 ID。
        :return: None。
        '''
        if not albumId:
            pass
        normalized = str('').strip()
        if normalized:
            logger.debug('[TIDAL] search album sub-click %s', normalized)
            LPTidalDetailViewControllerBase.pushDetailPage(self, 'album', normalized)

    onAlbumClicked = None(onAlbumClicked)
    
    def updateSearchVisibleRange(self = None, resultKey = None, firstIndex = pyqtSlot(str, int, int), lastIndex = {
        'resultKey': str,
        'firstIndex': int,
        'lastIndex': int,
        'return': None }):
        '''
        接收 QML 搜索结果可见范围，并触发缩略图预取。

        :param resultKey: 搜索结果类型。
        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        self._state.updateSearchVisibleRange(resultKey, firstIndex, lastIndex)

    updateSearchVisibleRange = None(updateSearchVisibleRange)
    
    def loadMoreSearchResults(self = None, resultKey = None):
        '''
        加载指定搜索分类的下一页结果。

        :param resultKey: 搜索分类标识。
        :return: None。
        '''
        if not self._state.searchText:
            pass
        query = str('').strip()
        if not resultKey:
            pass
        normalized_key = str('').strip().lower()
        search_type = self.SEARCH_TYPE_BY_FILTER.get(normalized_key, '')
        if not query or search_type:
            return None
        if not None._state.isLoadingMoreForResult(normalized_key) or self._state.hasMoreForResult(normalized_key):
            return None
        offset = None._state.offsetForResult(normalized_key)
        limit = self._state.limitForResult(normalized_key)
        revision = self._search_revision
        self._state.setSearchResultLoadingMore(normalized_key, True)
        request = None(None, None, None, (lambda result = None, searchRevision = None, key = None: self._handleSearchMoreResult(searchRevision, key, result)), **('key', 'tag', 'task', 'callback'))
        self._ensure_scheduler().enqueue(request, 5, **('priority',))

    loadMoreSearchResults = None(loadMoreSearchResults)
    
    def debugLog(self = None, message = None):
        '''
        输出搜索页 QML 调试日志。

        :param message: 调试信息。
        :return: None。
        '''
        logger.debug(f'''[TIDAL][QML] {message}''')

    debugLog = None(debugLog)
    
    def _showFavoriteToast(self = None, desiredFavorite = None, success = None):
        '''
        展示搜索收藏操作结果 Toast。

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

    
    def _updateSearchItemFavorite(self = None, itemType = None, itemId = None, isFavorite = {
        'itemType': str,
        'itemId': str,
        'isFavorite': bool,
        'return': None }):
        '''
        更新所有搜索结果模型中指定条目的 isFavorite 状态。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :param isFavorite: 新的收藏状态。
        :return: None。
        '''
        models = self._state._trackedImageModels()
        for model in models:
            model.updateItem(itemId, {
                'isFavorite': isFavorite })

    
    def _onFavoriteResult(self = None, result = None):
        '''
        处理常驻收藏服务的结果回调，只负责页面内展示与搜索结果模型刷新。

        :param result: 收藏服务结果字典。
        :return: None。
        '''
        if not isinstance(result, dict):
            return None
        if not result.get('error', ''):
            pass
        if None('') == 'not_logged_in':
            return None
        success = None(result.get('success'))
        desired_favorite = bool(result.get('desiredFavorite', False))
        was_favorite = bool(result.get('wasFavorite', False))
        if not result.get('itemType', ''):
            pass
        item_type = str('')
        if not result.get('itemId', ''):
            pass
        item_id = str('')
        if self._ui_detached:
            toastFavoriteResult = toastFavoriteResult
            import HOME.StreamService.Tidal.services.LPTidalFavoriteService
            toastFavoriteResult(result)
            return None
        None._updateSearchItemFavorite(item_type, item_id, desired_favorite if success else was_favorite)
        self._showFavoriteToast(desired_favorite, success)

    
    def _handleSearchResult(self = None, revision = None, result = None):
        '''
        处理搜索回包。

        :param revision: 搜索修订号。
        :param result: 请求结果。
        :return: None。
        '''
        if revision != self._search_revision:
            logger.debug(f'''[TIDAL] ignore stale search result revision={revision}''')
            return None
        None._state.setLoading(False)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._state.setErrorMessage('Search failed. Please try again.')
            return None
        normalized = None._provider.normalizeSearchResults(result.get('data'))
        self._state.setResults(normalized)

    
    def _handleSearchMoreResult(self = None, revision = None, resultKey = None, result = {
        'revision': int,
        'resultKey': str,
        'result': Any,
        'return': None }):
        '''
        处理搜索分类分页回包。

        :param revision: 搜索修订号。
        :param resultKey: 搜索分类标识。
        :param result: 请求结果。
        :return: None。
        '''
        if revision != self._search_revision:
            logger.debug(f'''[TIDAL] ignore stale search more result revision={revision}''')
            return None
        None._state.setSearchResultLoadingMore(resultKey, False)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._state.setErrorMessage('Search failed. Please try again.')
            return None
        normalized = None._provider.normalizeSearchResults(result.get('data'))
        if not resultKey:
            pass
        section = normalized.get(str('').strip().lower(), { })
        self._state.appendResults(resultKey, section)

    
    def _setup_qml_page(self = None):
        '''
        创建 QQuickWidget 并加载搜索 QML。

        :return: None。
        '''
        if self.quickWidget is not None:
            return None
        quick = None(self)
        quick.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        quick.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        quick.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        quick.setMouseTracking(True)
        quick.setClearColor(LPGlobalUI.THEME_BACKGROUND_COLOR_UI)
        quick.setStyleSheet(f'''background-color: {LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name()};''')
        ctx = quick.rootContext()
        applyTidalSharedQmlContext(ctx)
        applyTidalCursorBridge(ctx, self, quick)
        ctx.setContextProperty('tidalSearchStateBridge', self._state)
        ctx.setContextProperty('tidalSearchState', self._state)
        ctx.setContextProperty('tidalSearchActionsBridge', self)
        ctx.setContextProperty('tidalSearchActions', self)
        ctx.setContextProperty('tidalStore', self._store)
        ctx.setContextProperty('tidalShowShellTopNavigation', not (self._shell_embedded))
        installTidalQmlNetworkDiagnostics(quick, 'search')
        quick.setSource(resolveTidalQmlUrl(LPUIPath.TidalSearchQML, 'pages/TidalSearch.qml'))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''[TIDAL] Search QML load failed, status={quick.status()}''')
            for err in quick.errors():
                logger.error(f'''[TIDAL] {err.toString()}''')
        root = quick.rootObject()
        if root is not None:
            root.setProperty('tidalSearchState', self._state)
            root.setProperty('tidalSearchActions', self)
            root.setProperty('sharedStore', self._store)
            root.setProperty('showShellTopNavigation', not (self._shell_embedded))
        self._main_layout.addWidget(quick)
        self.quickWidget = quick

    
    def _ensure_state_active(self = None):
        '''
        确保搜索状态处于激活态。

        :return: None。
        '''
        if self._state_active:
            return None
        None._store.activateSearchState()
        self._state_active = True

    
    def _ensure_state_inactive(self = None):
        '''
        确保搜索状态处于失活态。

        :return: None。
        '''
        if not self._state_active:
            return None
        None._store.deactivateSearchState()
        self._state_active = False

    
    def _ensure_scheduler(self = None):
        '''
        确保搜索请求调度器可用。

        :return: 请求调度器。
        '''
        if self._scheduler is None or self._scheduler.isShutdown:
            self._scheduler = LPTidalRequestScheduler(self)
        return self._scheduler

    
    def _shutdown_scheduler(self = None):
        '''
        停止搜索请求调度器并丢弃未完成回调。

        :return: None。
        '''
        scheduler = self._scheduler
        if scheduler is None:
            return None
        self._scheduler = None
    # WARNING: Decompyle incomplete

    __classcell__ = None

