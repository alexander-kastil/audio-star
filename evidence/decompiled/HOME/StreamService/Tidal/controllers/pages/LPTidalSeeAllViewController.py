# Source Generated with Decompyle++
# File: LPTidalSeeAllViewController.pyc (Python 3.9)

'''
TIDAL See All 查看全部页控制器。
'''
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QMetaObject, Qt, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import LPGlobalUI
from LPClientFramework.LPMSManager.Tidal.LPTidalFavoriteManager import LPTidalFavoriteManager
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPPlayList.LPTidalPlayList import TIDAL_FAVORITE_TRACKS_ID, TIDAL_FAVORITE_TRACKS_SECTION_KEY
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.controllers.base.LPTidalPlayController import LPTidalPlayController
from HOME.StreamService.Tidal.controllers.shell.LPTidalShellRouter import pushTidalPage
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.services.LPTidalCollectionSortPreference import LPTidalCollectionSortPreference
from HOME.StreamService.Tidal.services.LPTidalSeeAllViewPreference import LPTidalSeeAllViewPreference
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalCursorBridge, applyTidalSharedQmlContext, clearTidalCursorBridge, resolveTidalQmlUrl
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest, LPTidalRequestScheduler
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalSeeAllDescriptor, LPTidalStore
from HOME.StreamService.Tidal.services.LPTidalNetworkDiagnostics import installTidalQmlNetworkDiagnostics
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPUtility import logger

class LPTidalSeeAllViewController(QWidget, LPTidalPlayController):
    '''TIDAL See All 页面，负责分页加载、过滤状态、视图切换和详情路由。'''
    PAGE_LIMIT = 50
    HOME_DESCRIPTORS: Dict[(str, Dict[(str, Any)])] = {
        'featured-new-albums': {
            'title': 'New Albums',
            'itemType': 'album',
            'endpointPath': '/v1/featured/new/albums' },
        'featured-new-tracks': {
            'title': 'New Tracks',
            'itemType': 'track',
            'endpointPath': '/v1/featured/new/tracks' },
        'featured-new-playlists': {
            'title': 'New Playlists',
            'itemType': 'playlist',
            'endpointPath': '/v1/featured/new/playlists' },
        'rising-new-tracks': {
            'title': 'Rising Tracks',
            'itemType': 'track',
            'endpointPath': '/v1/rising/new/tracks' },
        'rising-new-albums': {
            'title': 'Rising Albums',
            'itemType': 'album',
            'endpointPath': '/v1/rising/new/albums' },
        'hi-res-albums': {
            'title': 'Hi-Res Albums',
            'itemType': 'album',
            'endpointPath': '/v1/master/recommended/albums' },
        'custom-mixes': {
            'title': 'Custom Mixes',
            'itemType': 'playlist',
            'endpointPath': '/v1/pages/my_collection_my_mixes',
            'sourceKind': 'page_module' } }
    COLLECTION_DESCRIPTORS: Dict[(str, Dict[(str, Any)])] = {
        'userPlaylists': {
            'title': 'Playlists',
            'itemType': 'playlist',
            'endpointPath': '/v1/users/{userId}/playlistsAndFavoritePlaylists' },
        'favoriteArtists': {
            'title': 'Favorite Artists',
            'itemType': 'artist',
            'endpointPath': '/v1/users/{userId}/favorites/artists' },
        'favoriteAlbums': {
            'title': 'Favorite Albums',
            'itemType': 'album',
            'endpointPath': '/v1/users/{userId}/favorites/albums' },
        'favoriteTracks': {
            'title': 'Favorite Tracks',
            'itemType': 'track',
            'endpointPath': '/v1/users/{userId}/favorites/tracks' },
        'favoriteVideos': {
            'title': 'Favorite Videos',
            'itemType': 'video',
            'endpointPath': '/v1/users/{userId}/favorites/videos' } }
    
    def __init__(self = None, descriptor = None, parent = None):
        '''
        初始化 See All 页面。

        :param descriptor: See All 数据源描述。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._descriptor = descriptor
        self._store = LPTidalStore.instance()
        self._state = self._store.acquireSeeAllState(descriptor)
        self._provider = LPTidalDataProvider()
        self._scheduler = LPTidalRequestScheduler(self)
        self._state_active = False
        self.quickWidget = None
        self.deleteOnPrune = True
        self._favorite_manager = LPTidalFavoriteManager(self)
        self._ui_detached = False
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._onDestroyed)
        logger.debug('[TIDAL] init see all section=%s title=%s itemType=%s endpoint=%s', descriptor.sectionKey, descriptor.title, descriptor.itemType, descriptor.endpointPath)
        self._restoreViewModePreference()
        self._setup_qml_page()
        self._ensure_state_active()
        self.reload()

    
    def __del__(self):
        '''
        析构时兜底失活状态并停止调度器。

        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def descriptorForHomeSection(cls = None, sectionKey = None):
        '''
        根据首页 section 创建 See All 描述。

        :param sectionKey: 首页区块标识。
        :return: 描述对象或 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        spec = cls.HOME_DESCRIPTORS.get(section_key)
        if spec and section_key.startswith('featured-'):
            return cls._descriptorForFeaturedHomeSection(section_key)
        if not None:
            return None
        return None(section_key, str(spec.get('title', section_key)), str(spec.get('itemType', '')), str(spec.get('endpointPath', '')), 'token', False, str(spec.get('sourceKind', 'home')), **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'sourceKind'))

    descriptorForHomeSection = None(descriptorForHomeSection)
    
    def _descriptorForFeaturedHomeSection(cls = None, sectionKey = None):
        '''
        根据动态 Featured 首页 section 创建 See All 描述。

        :param sectionKey: 动态 Featured 区块标识。
        :return: 描述对象或 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        prefix = 'featured-'
        suffix_mapping = {
            '-albums': ('albums', 'album', 'Albums'),
            '-tracks': ('tracks', 'track', 'Tracks'),
            '-playlists': ('playlists', 'playlist', 'Playlists') }
        for resource_type, item_type, resource_title in suffix_mapping.items():
            if not section_key.startswith(prefix) or section_key.endswith(suffix):
                continue
            path_segment = section_key[len(prefix):-len(suffix)].strip()
            if not path_segment:
                return None
            category_title = None._featuredCategoryTitle(path_segment)
            return LPTidalSeeAllDescriptor(section_key, f'''{category_title} {resource_title}''', item_type, f'''/v1/featured/{path_segment}/{resource_type}''', 'token', False, 'home', **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'sourceKind'))
            return None

    _descriptorForFeaturedHomeSection = None(_descriptorForFeaturedHomeSection)
    
    def _featuredCategoryTitle(cls = None, pathSegment = None):
        '''
        返回 Featured path 的展示标题。

        :param pathSegment: Featured 分类 path。
        :return: 展示标题。
        '''
        mapping = {
            'new': 'New',
            'recommended': 'Staff Picks',
            'top': 'Top 20',
            'exclusive': 'Exclusive' }
        if not pathSegment:
            pass
        normalized = str('').strip().lower()
        return mapping.get(normalized, normalized.replace('-', ' ').title())

    _featuredCategoryTitle = None(_featuredCategoryTitle)
    
    def descriptorForGenreSection(cls = None, genreId = None, genreTitle = classmethod, sectionKey = {
        'genreId': str,
        'genreTitle': str,
        'sectionKey': str,
        'return': Optional[LPTidalSeeAllDescriptor] }):
        '''
        根据流派详情 section 创建 See All 描述。

        :param genreId: 流派路径、slug 或 ID。
        :param genreTitle: 流派展示标题。
        :param sectionKey: 流派详情区块标识。
        :return: 描述对象或 None。
        '''
        genre_id = cls._normalizeGenrePath(genreId)
        if not sectionKey:
            pass
        section_key = str('').strip()
        spec = {
            'genre-playlists': ('Playlists', 'playlist', 'playlists'),
            'genre-tracks': ('New Tracks', 'track', 'tracks'),
            'genre-albums': ('New Albums', 'album', 'albums'),
            'genre-videos': ('Videos', 'video', 'videos') }.get(section_key)
        if genre_id or spec is None:
            return None
        (title, item_type, endpoint_suffix) = None
        if not genreTitle:
            pass
        page_title = f'''{str(genre_id).strip()} - {title}'''
        return LPTidalSeeAllDescriptor(f'''genre-{genre_id}-{endpoint_suffix}''', page_title, item_type, f'''/v1/genres/{genre_id}/{endpoint_suffix}''', 'token', False, 'home', **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'sourceKind'))

    descriptorForGenreSection = None(descriptorForGenreSection)
    
    def descriptorForMoodSection(cls = None, moodId = None, moodTitle = classmethod, sectionKey = {
        'moodId': str,
        'moodTitle': str,
        'sectionKey': str,
        'return': Optional[LPTidalSeeAllDescriptor] }):
        '''
        根据心情详情 section 创建 See All 描述。

        :param moodId: 心情路径、slug 或 ID。
        :param moodTitle: 心情展示标题。
        :param sectionKey: 心情详情区块标识。
        :return: 描述对象或 None。
        '''
        mood_id = cls._normalizeMoodPath(moodId)
        if not sectionKey:
            pass
        section_key = str('').strip()
        spec = {
            'mood-playlists': ('Playlists', 'playlist', 'playlists') }.get(section_key)
        if mood_id or spec is None:
            return None
        (title, item_type, endpoint_suffix) = None
        if not moodTitle:
            pass
        page_title = f'''{str(mood_id).strip()} - {title}'''
        return LPTidalSeeAllDescriptor(f'''mood-{mood_id}-{endpoint_suffix}''', page_title, item_type, f'''/v1/moods/{mood_id}/playlists''', 'token', False, 'home', **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'sourceKind'))

    descriptorForMoodSection = None(descriptorForMoodSection)
    
    def descriptorForCollectionSection(cls = None, sectionKey = None, userId = classmethod):
        '''
        根据收藏页 section 创建 See All 描述。

        :param sectionKey: 收藏页区块标识。
        :param userId: TIDAL 用户 ID。
        :return: 描述对象或 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not userId:
            pass
        user_id = str('').strip()
        if not user_id:
            return None
        spec = None.COLLECTION_DESCRIPTORS.get(section_key)
        if not spec:
            return None
        endpoint_path = None(spec.get('endpointPath', '')).replace('{userId}', user_id)
        sort_options = LPTidalCollectionSortPreference.sortOptions(section_key)
        default_sort = LPTidalCollectionSortPreference.sortForSection(section_key, user_id)
        return LPTidalSeeAllDescriptor(section_key, str(spec.get('title', section_key)), str(spec.get('itemType', '')), endpoint_path, 'token', True, default_sort.get('order', LPTidalCollectionSortPreference.DEFAULT_ORDER), default_sort.get('direction', LPTidalCollectionSortPreference.DEFAULT_DIRECTION), 'collection', sort_options, **('sectionKey', 'title', 'itemType', 'endpointPath', 'authMode', 'supportsSort', 'defaultOrder', 'defaultOrderDirection', 'sourceKind', 'sortOptions'))

    descriptorForCollectionSection = None(descriptorForCollectionSection)
    
    def descriptorForRecentlySection(cls = None, sectionKey = None, userId = classmethod):
        '''
        根据 Recently 记录的列表标识重建 See All 描述。

        Recently 快照用播放列表占位 id 记录列表身份：收藏曲为带源前缀的
        TIDAL_FAVORITE_TRACKS_ID（0.2.10a 及更早为无前缀的 favoriteTracks），
        Home 曲目列表为首页 sectionKey。这里把占位 id 还原成 See All 描述，
        供从 Recently 跳回 See All 页面使用。

        :param sectionKey: Recently 记录中的列表标识（header.headId/streamId）。
        :param userId: 当前 TIDAL 账号 id，用于收藏曲 See All 接口路径。
        :return: 描述对象；无法重建时返回 None。
        '''
        if not sectionKey:
            pass
        normalized_key = str('').strip()
        if not normalized_key:
            return None
        if None in (TIDAL_FAVORITE_TRACKS_ID, TIDAL_FAVORITE_TRACKS_SECTION_KEY):
            return cls.descriptorForCollectionSection(TIDAL_FAVORITE_TRACKS_SECTION_KEY, userId)
        return None.descriptorForHomeSection(normalized_key)

    descriptorForRecentlySection = None(descriptorForRecentlySection)
    
    def _saveCollectionSortPreference(self = None, order = None, direction = None):
        '''
        保存当前收藏 See All 排序偏好。

        :param order: 排序字段。
        :param direction: 排序方向。
        :return: None。
        '''
        descriptor = self._descriptor
        if not getattr(descriptor, 'sectionKey', ''):
            pass
        section_key = str('').strip()
        if not getattr(descriptor, 'sourceKind', ''):
            pass
        source_kind = str('').strip().lower()
        if source_kind != 'collection':
            return None
        account = None._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        LPTidalCollectionSortPreference.saveSort(section_key, user_id, order, direction)

    
    def _normalizeGenrePath(genreId = None):
