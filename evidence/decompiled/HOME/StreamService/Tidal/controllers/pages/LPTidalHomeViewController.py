# Source Generated with Decompyle++
# File: LPTidalHomeViewController.pyc (Python 3.9)

'''
TIDAL 首页控制器。
'''
from typing import Any, Dict, List, Optional, Set
import time
import json
import threading
from PyQt6.QtCore import QMetaObject, QObject, Qt, QTimer
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSlot
import LPGlobalUI
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPUtility import logger
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.controllers.base.LPTidalPlayController import LPTidalPlayController
from HOME.StreamService.Tidal.controllers.pages.LPTidalSeeAllViewController import LPTidalSeeAllViewController
from HOME.StreamService.Tidal.controllers.pages.LPTidalLoginViewController import LPTidalLoginViewController
from HOME.StreamService.Tidal.controllers.shell.LPTidalShellRouter import pushTidalPage
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.data.LPTidalHomeViewData import splitHomeSectionsForView
from HOME.StreamService.Tidal.models.LPTidalListModel import LPTidalListModel
from HOME.StreamService.Tidal.services.LPTidalCollectionSortPreference import LPTidalCollectionSortPreference
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalCursorBridge, applyTidalSharedQmlContext, clearTidalCursorBridge, resolveTidalQmlUrl
from HOME.StreamService.Tidal.services.LPTidalImageService import LPTidalImageService
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest, LPTidalRequestScheduler
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalSeeAllDescriptor, LPTidalStore
from HOME.StreamService.Tidal.services.LPTidalNetworkDiagnostics import installTidalQmlNetworkDiagnostics
from LPClientFramework.LPMSManager.Tidal.LPTidalFavoriteManager import LPTidalFavoriteManager
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPPlayList.LPTidalPlayList import tidalNormalizeQualityValue, tidalNormalizeReplayGainValue, tidalReplayGainLabel, tidalReplayGainValueForLabel, tidalReadLocalQualityValue, tidalReadLocalReplayGainValue, tidalSaveLocalQualityValue, tidalSaveLocalReplayGainValue, tidalSubscriptionSupportsMax

class LPTidalHomeViewController(QWidget, LPTidalPlayController):
    '''TIDAL 首页宿主，仅负责承载 QQuickWidget 与基础 QML 加载。'''
    COLLECTION_COVER_CALIBRATION_LIMIT = 11
    COLLECTION_COVER_CALIBRATION_TAG = 'tidal_collection_cover_calibration'
    COVER_THUMBNAIL_RETRY_DELAY_MS = 62000
    COVER_THUMBNAIL_RETRY_MAX = 3
    
    def __init__(self = None, parent = None, shellEmbedded = None):
        '''
        初始化 TIDAL 首页控制器。

        :param parent: 父级 QWidget。
        :param shellEmbedded: 是否嵌入到 TIDAL Shell 内容区。
        :return: None。
        '''
        super().__init__(parent)
        self._shell_embedded = bool(shellEmbedded)
        self._store = LPTidalStore.instance()
        self._login_manager = LPTidalLoginManager.instance(self)
        self._state = self._store.homeState
        self._provider = LPTidalDataProvider()
        self._favorite_manager = LPTidalFavoriteManager(self)
        self._scheduler = LPTidalRequestScheduler(self)
        self._ui_detached = False
        self._cover_calibration_pending_ids = set()
        self._cover_retry_attempts = { }
        self._image_service = LPTidalImageService.instance()
        self._image_service.thumbnailFailed.connect(self._on_playlist_cover_thumbnail_failed)
        self._collection_refresh_revision = 0
        self._subscription_refresh_revision = 0
        self._home_request_revision = 0
        self._page_instance_active = True
        self._state_active = False
        self._collection_state_active = False
        self._auto_play_enabled = False
        self.quickWidget = None
        self.deleteOnPrune = True
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._on_destroyed)
        self._store.accountStateChanged.connect(self._on_account_state_changed)
        self._store.collectionChange.connect(self._on_collection_change)
        self._login_manager.logoutSucceeded.connect(self._on_logout_succeeded)
        self._setup_qml_page()
        self._ensure_state_active()

    
    def __del__(self):
        '''
        析构时兜底失活首页状态。

        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _on_destroyed(self = None, destroyedObject = None):
        '''
        QObject 销毁回调，兜底失活首页状态。

        :param destroyedObject: Qt 销毁信号透传对象。
        :return: None。
        '''
        _ = destroyedObject
        self._invalidateHomeRequests()
        clearTidalCursorBridge(self)
        self.unregisterTidalDeviceInfoObserver()
        self._shutdown_scheduler()
        self._ensure_collection_state_inactive()
        self._ensure_state_inactive()
    # WARNING: Decompyle incomplete

    
    def viewWillAppear(self = None):
        '''
        页面显示时激活首页状态。

        :return: None。
        '''
        self._page_instance_active = True
        self._ui_detached = False
        self._ensure_state_active()
        if self.quickWidget is not None:
            applyTidalCursorBridge(self.quickWidget.rootContext(), self, self.quickWidget)
        self._refresh_subscription_if_logged_in()
        self.registerTidalDeviceInfoObserver()
        self._loadHomeOnEnter()
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is not None:
            if not root.property('currentTab'):
                pass
            if int(0) == 1:
                self._state.clearHomeVisibleRanges()
                self._state.cancelImageOwner()
                self._ensure_state_inactive()
                self._ensure_collection_state_active()
                self.refreshCollectionOnEnter()
            else:
                self._ensure_state_active()
                self._store.collectionState.cancelImageOwner()
                self._ensure_collection_state_inactive()
        self._syncCurrentTabVisibleRanges()

    
    def viewWillDisappear(self = None):
        '''
        页面隐藏时失活首页状态。

        :return: None。
        '''
        self._invalidateHomeRequests()
        self._ui_detached = True
        self._state.clearHomeVisibleRanges()
        self._state.cancelImageOwner()
        self._store.collectionState.cancelImageOwner()
        clearTidalCursorBridge(self)
        self.unregisterTidalDeviceInfoObserver()
        self._ensure_collection_state_inactive()
        self._ensure_state_inactive()
        self._cancel_page_requests()

    
    def _setup_qml_page(self = None):
        '''
        创建 QQuickWidget、注入最小上下文并加载首页 QML。

        :param: 无。
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
        ctx.setContextProperty('tidalHomeActions', self)
        ctx.setContextProperty('tidalHomeState', self._state)
        ctx.setContextProperty('tidalStore', self._store)
        ctx.setContextProperty('sharedStore', self._store)
        ctx.setContextProperty('tidalShowShellTopNavigation', not (self._shell_embedded))
        installTidalQmlNetworkDiagnostics(quick, 'home')
        qml_url = resolveTidalQmlUrl(LPUIPath.TidalHomeQML, 'pages/TidalHome.qml')
        logger.debug(f'''[TIDAL] loading QML source={qml_url.toString()}''')
        quick.setSource(qml_url)
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''[TIDAL] QML load failed, status={quick.status()}''')
            for err in quick.errors():
                logger.error(f'''[TIDAL] {err.toString()}''')
        else:
            logger.debug('[TIDAL] QML loaded successfully')
        self.quickWidget = quick
        root = quick.rootObject()
        if root is not None:
            set_actions = root.setProperty('homeActions', self)
            root.setProperty('tidalHomeState', self._state)
            set_shared_store = root.setProperty('sharedStore', self._store)
            root.setProperty('showShellTopNavigation', not (self._shell_embedded))
            logger.debug(f'''[TIDAL] set qml home actions result={set_actions} sharedStore={set_shared_store}''')
            self._sync_qml_home_bindings()
        self._main_layout.addWidget(quick)

    
    def _ensure_state_active(self = None):
        '''
        确保首页状态处于激活态。

        :return: None。
        '''
        if self._state_active:
            return None
        None._store.activateHomeState()
        self._state_active = True

    
    def setShellCurrentTab(self = None, tabIndex = None):
        '''
        设置 Shell 控制的 Home/My Collection tab。

        :param tabIndex: 0 表示 Home，1 表示 My Collection。
        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is None:
            return None
        if not tabIndex:
            pass
        normalized_tab = 1 if None(0) == 1 else 0
        if not root.property('currentTab'):
            pass
        current_tab = 1 if int(0) == 1 else 0
        root.setProperty('currentTab', normalized_tab)
        if current_tab == normalized_tab:
            self.onHomeTabChanged(normalized_tab)

    
    def onHomeTabChanged(self = None, tabIndex = None):
        '''
        处理 Home/My Collection tab 切换时的图片 owner 生命周期。

        :param tabIndex: 0 表示 Home，1 表示 My Collection。
        :return: None。
        '''
        if not tabIndex:
            pass
        normalized_tab = 1 if int(0) == 1 else 0
        if normalized_tab == 1:
            self._ensure_collection_state_active()
            self._state.clearHomeVisibleRanges()
            self._state.cancelImageOwner()
            self._ensure_state_inactive()
            self.refreshCollectionOnEnter()
        else:
            self._ensure_state_active()
            self._store.collectionState.cancelImageOwner()
            self._ensure_collection_state_inactive()
        self._syncCurrentTabVisibleRanges()

    onHomeTabChanged = None(onHomeTabChanged)
    
    def _syncCurrentTabVisibleRanges(self = None):
        '''
        请求 QML 重新同步当前 tab 的可见范围。

        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is not None:
            QMetaObject.invokeMethod(root, 'syncCurrentTabVisibleRanges', Qt.ConnectionType.QueuedConnection)

    
    def _ensure_collection_state_active(self = None):
        '''
        确保嵌入式收藏页状态处于激活态。

        :return: None。
        '''
        if self._collection_state_active:
            return None
        None._store.activateCollectionState()
        self._collection_state_active = True

    
    def _ensure_collection_state_inactive(self = None):
        '''
        确保嵌入式收藏页状态处于失活态。

        :return: None。
        '''
        if not self._collection_state_active:
            return None
        None._store.deactivateCollectionState()
        self._collection_state_active = False

    
    def _ensure_state_inactive(self = None):
        '''
        确保首页状态处于失活态。

        :return: None。
        '''
        if not self._state_active:
            return None
        None._store.deactivateHomeState()
        self._state_active = False

    
    def onCardClicked(self = None, sectionKey = None, itemId = pyqtSlot(str, str)):
        '''
        处理首页卡片点击。

        :param sectionKey: 区块标识。
        :param itemId: 条目 ID。
        :return: None。
        '''
        item = self._store.collectionState.findItem(sectionKey, itemId)
        is_collection_item = isinstance(item, dict)
        if not is_collection_item:
            item = self._state.findItem(sectionKey, itemId)
        item_type = ''
        if isinstance(item, dict):
            if not item.get('itemType', ''):
                pass
            item_type = str('').strip().lower()
        if not item_type:
            item_type = 'album'
        logger.debug(f'''[TIDAL] home card clicked section={sectionKey}, itemId={itemId}, itemType={item_type}''')
        if item_type == 'track':
            if not is_collection_item or self.playTidalCollectionTrack(sectionKey, itemId):
                logger.debug('[TIDAL] collection track play failed section=%s itemId=%s', sectionKey, itemId)
            elif not self.playTidalHomeTrack(sectionKey, itemId):
                logger.debug('[TIDAL] home track play failed section=%s itemId=%s', sectionKey, itemId)
            return None
        if None == 'mix' and isinstance(item, dict):
            LPTidalMixDetailViewController = LPTidalMixDetailViewController
            import HOME.StreamService.Tidal.controllers.details.LPTidalMixDetailViewController
            LPTidalStore = LPTidalStore
            import HOME.StreamService.Tidal.state.LPTidalStore
            if not item.get('title', ''):
                pass
            if not item.get('subtitle', ''):
                pass
            if not item.get('imageUrl', ''):
                pass
            pushTidalPage(self, LPTidalMixDetailViewController(itemId, str(''), str(''), str(''), self, **('itemTitle', 'itemSubtitle', 'itemImageUrl', 'parent')), 'tidal_mix_detail')
            return None
        if not None._openTidalItem(item_type, itemId, item, f'''section:{sectionKey}''', **('item', 'sourceTag')):
            logger.debug(f'''[TIDAL] onCardClicked unsupported section={sectionKey}, itemId={itemId}, itemType={item_type}''')

    onCardClicked = None(onCardClicked)
    
    def onArtistClicked(self = None, artistId = None):
        '''
        处理首页曲目副标题艺人点击。

        :param artistId: 艺人 ID。
        :return: None。
        '''
        if not artistId:
            pass
        normalized_id = str('').strip()
        if not normalized_id:
            return None
        None.debug('[TIDAL] home artist clicked artistId=%s', normalized_id)
        self._openTidalItem('artist', normalized_id, 'home-track-artist', **('sourceTag',))

    onArtistClicked = None(onArtistClicked)
    
    def onAlbumClicked(self = None, albumId = None):
        '''
        首页卡片副标题或列表列专辑点击（新增），push 专辑详情新页。

        :param albumId: 专辑 ID。
        :return: None。
        '''
        if not albumId:
            pass
        normalized = str('').strip()
        if normalized:
            logger.debug('[TIDAL] home album sub-click albumId=%s', normalized)
            self._openTidalItem('album', normalized, 'home-album-sub', **('sourceTag',))

    onAlbumClicked = None(onAlbumClicked)
    
    def onPlayTrackClicked(self = None, trackId = None):
        '''
        处理首页曲目播放按钮点击。

        :param trackId: 曲目 ID。
        :return: None。
        '''
        if not trackId:
            pass
        normalized_id = str('').strip()
        if not normalized_id:
            return None
        if not None.playTidalHomeTrack('', normalized_id):
            logger.debug('[TIDAL] home play track failed trackId=%s', normalized_id)

    onPlayTrackClicked = None(onPlayTrackClicked)
    
    def onCollectionPlayTrackClicked(self = None, sectionKey = None, trackId = pyqtSlot(str, str)):
        '''
        处理嵌入式收藏页曲目播放按钮点击。

        :param sectionKey: 收藏区块标识。
        :param trackId: 曲目 ID。
        :return: None。
        '''
        if not trackId:
            pass
        normalized_id = str('').strip()
        if not sectionKey:
            pass
        if not str('').strip():
            pass
        normalized_section = 'favoriteTracks'
        if not normalized_id:
            return None
        if not None.playTidalCollectionTrack(normalized_section, normalized_id):
            logger.debug('[TIDAL] collection play track failed section=%s trackId=%s', normalized_section, normalized_id)

    onCollectionPlayTrackClicked = None(onCollectionPlayTrackClicked)
    
    def onPlayClicked(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        '''
        处理首页媒体卡片封面播放按钮点击。

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
            if not self.playTidalHomeTrack('', normalized_id):
                logger.debug('[TIDAL] home card play track failed itemId=%s', normalized_id)
            return None
        if None in frozenset({'album', 'mix', 'playlist'}):
            if not self.playTidalMediaQueue(normalized_type, normalized_id):
                logger.debug('[TIDAL] home card media queue play failed type=%s itemId=%s', normalized_type, normalized_id)
            return None
        if not None._openTidalItem(normalized_type, normalized_id, 'home-card-play-fallback', **('sourceTag',)):
            logger.debug('[TIDAL] home card play fallback unsupported type=%s itemId=%s', normalized_type, normalized_id)

    onPlayClicked = None(onPlayClicked)
    
    def onSupportingItemClicked(self = None, itemType = None, itemId = pyqtSlot(str, str)):
        if not itemType:
            pass
        if not str('').strip().lower():
            pass
        normalized_type = 'album'
        if not itemId:
            pass
        normalized_id = str('').strip()
        if not normalized_id:
            return None
        if None == 'track':
            self.playTidalHomeTrack('', normalized_id)
        else:
            self._openTidalItem(normalized_type, normalized_id)

    onSupportingItemClicked = None(onSupportingItemClicked)
    
    def _openTidalItem(self = None, itemType = None, itemId = None, item = (None, 'home'), sourceTag = {
        'itemType': str,
        'itemId': str,
        'item': Optional[Dict[(str, Any)]],
        'sourceTag': str,
        'return': bool }):
        '''
        按条目类型打开对应的 TIDAL 页面。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :param item: 可选条目字典，用于读取展示标题。
        :param sourceTag: 调试来源标记。
        :return: 成功触发跳转返回 True。
        '''
        if not itemType:
            pass
        normalized_type = str('').strip().lower()
        if not itemId:
            pass
        normalized_item_id = str('').strip()
        if not normalized_type or normalized_item_id:
            return False
        if None == 'mood':
            mood_title = str(normalized_item_id).strip() if isinstance(item, dict) else normalized_item_id
            descriptor = LPTidalSeeAllViewController.descriptorForMoodSection(normalized_item_id, mood_title, 'mood-playlists')
            if descriptor is not None:
                pushTidalPage(self, LPTidalSeeAllViewController(descriptor, self), 'tidal_see_all')
            return True
        if None == 'genre':
            LPTidalGenreDetailViewController = LPTidalGenreDetailViewController
            import HOME.StreamService.Tidal.controllers.details.LPTidalGenreDetailViewController
            category_title = str(normalized_item_id).strip() if isinstance(item, dict) else normalized_item_id
            pushTidalPage(self, LPTidalGenreDetailViewController(normalized_item_id, category_title, self, 'genre', **('categoryType',)), 'tidal_genre_detail')
            return True
        return None(LPTidalDetailViewControllerBase.pushDetailPage(self, normalized_type, normalized_item_id))

    
    def onHeroPrimaryClicked(self = None, categoryId = None, itemType = pyqtSlot(str, str, str), itemId = {
        'categoryId': str,
        'itemType': str,
        'itemId': str,
        'return': None }):
        '''
        处理 Hero 主按钮点击，打开当前分类主条目详情。

        :param categoryId: 当前 Featured 分类 path。
        :param itemType: 主条目类型。
        :param itemId: 主条目 ID。
        :return: None。
        '''
        if not categoryId:
            pass
        if not itemType:
            pass
        if not itemId:
            pass
        logger.debug('[TIDAL] hero primary clicked category=%s itemType=%s itemId=%s', str(''), str(''), str(''))
        if not itemType:
            pass
        normalized_item_type = str('').strip().lower()
        if normalized_item_type == 'video':
            if not categoryId:
                pass
            if not itemId:
                pass
            logger.debug('[TIDAL] hero primary click skipped video category=%s itemId=%s', str(''), str(''))
            return None
        if not categoryId:
            pass
        if not None._openTidalItem(itemType, itemId, f'''hero:{str('')}''', **('sourceTag',)):
            if not categoryId:
                pass
            if not itemType:
                pass
            if not itemId:
                pass
            logger.debug('[TIDAL] hero primary click unsupported category=%s itemType=%s itemId=%s', str(''), str(''), str(''))

    onHeroPrimaryClicked = None(onHeroPrimaryClicked)
    
    def onHeroResourceClicked(self = None, categoryId = None, categoryTitle = pyqtSlot(str, str, str), resourceType = {
        'categoryId': str,
        'categoryTitle': str,
        'resourceType': str,
        'return': None }):
        '''
        处理 Hero 资源按钮点击，打开当前分类资源的 See All 页面。

        :param categoryId: 当前 Featured 分类 path。
        :param categoryTitle: 当前分类标题。
        :param resourceType: 资源类型，例如 `albums`。
        :return: None。
        '''
        if not categoryId:
            pass
        normalized_category_id = str('').strip().lower()
        if not categoryTitle:
            pass
        normalized_category_title = str(normalized_category_id).strip()
        if not resourceType:
            pass
        normalized_resource_type = str('').strip().lower()
        if not normalized_category_id or normalized_resource_type:
            logger.debug('[TIDAL] hero resource click skipped category=%s resource=%s', normalized_category_id, normalized_resource_type)
            return None
        if None == 'videos':
            logger.debug('[TIDAL] hero resource click skipped video category=%s resource=%s', normalized_category_id, normalized_resource_type)
            return None
        item_type_mapping = {
            'albums': None,
            'tracks': 'track',
            'playlists': 'playlist' }
        descriptor = LPTidalSeeAllDescriptor(f'''featured-{normalized_category_id}-{normalized_resource_type}''', f'''{normalized_category_title} {normalized_resource_type.title()}''', item_type_mapping.get(normalized_resource_type, 'album'), f'''/v1/featured/{normalized_category_id}/{normalized_resource_type}''', 'token', False, 'home', **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'sourceKind'))
        logger.debug('[TIDAL] hero resource clicked category=%s title=%s resource=%s endpoint=%s', normalized_category_id, normalized_category_title, normalized_resource_type, descriptor.endpointPath)
        pushTidalPage(self, LPTidalSeeAllViewController(descriptor, self), 'tidal_see_all')

    onHeroResourceClicked = None(onHeroResourceClicked)
    
    def refreshCollectionOnEnter(self = None):
        '''
        My Collection 每次进入时触发整页后台刷新。

        :return: None。
        '''
        logger.debug('[TIDAL] collection page entered, refreshing collection data')
        self._refresh_collection_if_logged_in(True, **('skipCache',))

    refreshCollectionOnEnter = None(refreshCollectionOnEnter)
    
    def _on_collection_change(self = None, scope = None):
        '''
        Collection 数据变化时在 My Collection 页签可见时后台静默刷新。

        :param scope: Collection 变更范围。
        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is None:
            return None
        if not root.property('currentTab'):
            pass
        if None(0) != 1:
            return None
        account = None._store.accountState
        if not bool(account.get('isLoggedIn', False)):
            return None
        if not scope:
            pass
        normalized_scope = None('all').strip()
        if normalized_scope == 'userPlaylists':
            self._refresh_collection_playlists_if_logged_in(True, **('skipCache',))
            return None
        None._refresh_collection_if_logged_in(True, **('skipCache',))

    _on_collection_change = None(_on_collection_change)
    
    def onCollectionTabSelected(self = None):
        '''
        处理 My Collection 页签选中事件，触发收藏数据刷新。

        :return: None。
        '''
        self.refreshCollectionOnEnter()

    onCollectionTabSelected = None(onCollectionTabSelected)
    
    def updateHomeSectionVisibleRange(self = None, sectionKey = None, firstIndex = pyqtSlot(str, int, int), lastIndex = {
        'sectionKey': str,
        'firstIndex': int,
        'lastIndex': int,
        'return': None }):
        '''
        接收 QML 首页区块可见范围，触发缩略图预取；
        用户自建歌单分区同时按可见区补发详情封面校准请求。

        :param sectionKey: 区块标识。
        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        collection_state = self._store.collectionState
        if collection_state.collectionModelForSection(sectionKey) is not None:
            collection_state.updateCollectionSectionVisibleRange(sectionKey, firstIndex, lastIndex)
            if not sectionKey:
                pass
            if str('').strip() == 'userPlaylists':
                self._calibrate_visible_playlist_covers(firstIndex, lastIndex)
            return None
        None._state.updateHomeSectionVisibleRange(sectionKey, firstIndex, lastIndex)

    updateHomeSectionVisibleRange = None(updateHomeSectionVisibleRange)
    
    def clearHomeSectionVisibleRange(self = None, sectionKey = None):
        '''
        清空 QML 首页区块可见范围。

        :param sectionKey: 区块标识。
        :return: None。
        '''
        self._state.clearHomeSectionVisibleRange(sectionKey)

    clearHomeSectionVisibleRange = None(clearHomeSectionVisibleRange)
    
    def debugLog(self = None, message = None):
        '''
        输出 QML 调试日志。

        :param message: 调试信息。
        :return: None。
        '''
        logger.debug(f'''[TIDAL][QML] {message}''')

    debugLog = None(debugLog)
    
    def _mergeSectionImagePaths(self = None, oldModel = None, newItems = None):
