# Source Generated with Decompyle++
# File: LPWiiMRadioStore.pyc (Python 3.9)

'''
WiiMRadio 统一数据状态管理。
'''
import copy
import json
import time
import weakref
from typing import Any, Dict, List, Optional, Tuple
from PyQt6.QtCore import QAbstractListModel, QCoreApplication, QModelIndex, QObject, QTimer, Qt, pyqtProperty, pyqtSignal, pyqtSlot
import LPGlobalUI
from LPClientFramework.LPFavoriteCacheManager import LPFavoriteCacheManager, WIIMRADIO_LOCAL_USER_ID
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioFavoriteStorage import ensureLoaded as _ensure_wiimradio_favorites_loaded, extractStationLocationFields as _extract_station_location_fields, normalizeFavoriteItem as _normalize_wiimradio_favorite_item, saveFavorites as _save_wiimradio_favorites
from HOME.StreamService.WiiMRadio.utils import LPWiiMRadioDataProvider, WIIM_RADIO_CATEGORY_DEFINITIONS
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioRequestScheduler import LPWiiMRadioRequestScheduler
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioStationListModel import LPWiiMRadioStationListModel
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioThumbnailService import LPWiiMRadioThumbnailService
from LPClientFramework.LPUtility import logger

def _is_popular_section_key(sectionKey = None):
    '''
    判断区块标识是否为 popular。

    :param sectionKey: 区块标识。
    :return: popular 区块返回 True。
    '''
    if not sectionKey:
        pass
    return str('').strip() == 'popular'


def _extract_subcountry_code_from_query(query = None):
    '''
    提取查询参数中的 subcountryCode。

    :param query: 查询参数字典。
    :return: 归一化后的 subcountryCode；不存在时为空字符串。
    '''
    if not isinstance(query, dict):
        return ''
    if not query.get('subcountryCode', ''):
        pass
    return None('').strip()


def _build_query_without_subcountry_code(query = None):
    '''
    构造去掉 subcountryCode 的查询参数副本。

    :param query: 原始查询参数字典。
    :return: 去掉 subcountryCode 后的新查询参数字典。
    '''
    fallback_query = copy.deepcopy(query) if isinstance(query, dict) else { }
    fallback_query['subcountryCode'] = None
    return fallback_query


def _build_query_without_location_codes(query = None):
    '''
    构造去掉 countryCode 与 subcountryCode 的查询参数副本。

    :param query: 原始查询参数字典。
    :return: 去掉地区参数后的新查询参数字典。
    '''
    sanitized_query = copy.deepcopy(query) if isinstance(query, dict) else { }
    sanitized_query['countryCode'] = ''
    sanitized_query['subcountryCode'] = None
    return sanitized_query


def _should_retry_popular_without_subcountry(sectionKey = None, result = None, context = None):
    '''
    判断 popular 请求是否需要去掉 subcountryCode 再重试一次。

    :param sectionKey: 区块标识。
    :param result: 当前请求结果。
    :param context: 当前请求上下文。
    :return: 满足回退条件返回 True。
    '''
    if not _is_popular_section_key(sectionKey):
        return False
    if not None(context, dict):
        return False
    if None(context.get('append')):
        return False
    if None(context.get('popularFallbackRetried')):
        return False
    request_payload = None.get('requestPayload', { })
    if not _extract_subcountry_code_from_query(request_payload):
        return False
    if not None(result, dict) or bool(result.get('success')):
        return False
    items = None.get('items', [])
    if isinstance(items, list):
        pass
    return len(items) == 0


class LPWiiMRadioHomeSectionListModel(QAbstractListModel):
    SECTION_KEY_ROLE = int(Qt.ItemDataRole.UserRole) + 101
    TITLE_ROLE = SECTION_KEY_ROLE + 1
    ITEMS_ROLE = SECTION_KEY_ROLE + 2
    IS_LOADING_ROLE = SECTION_KEY_ROLE + 3
    IS_CATEGORY_ROLE = SECTION_KEY_ROLE + 4
    
    def __init__(self = None, parent = None):
        '''
        初始化 Home 区块列表模型。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._sections = []

    
    def rowCount(self = None, parent = None):
        '''
        返回当前区块数量。

        :param parent: 父级索引。
        :return: 区块数量。
        '''
        if parent.isValid():
            return 0
        return None(self._sections)

    
    def data(self = None, index = None, role = None):
        '''
        根据索引和角色返回区块数据。

        :param index: 模型索引。
        :param role: Qt 角色值。
        :return: 对应角色的数据。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._sections):
            return None
        section = None._sections[row]
        if role == self.SECTION_KEY_ROLE:
            return section.get('sectionKey', '')
        if None == self.TITLE_ROLE:
            return section.get('title', '')
        if None == self.ITEMS_ROLE:
            return section.get('items', [])
        if None == self.IS_LOADING_ROLE:
            return bool(section.get('isLoading'))
        if None == self.IS_CATEGORY_ROLE:
            return bool(section.get('isCategory'))

    
    def roleNames(self = None):
        '''
        返回 role 与字段名映射。

        :param: 无。
        :return: role 名称字典。
        '''
        return {
            self.IS_CATEGORY_ROLE: b'isCategory',
            self.IS_LOADING_ROLE: b'isLoading',
            self.ITEMS_ROLE: b'items',
            self.TITLE_ROLE: b'title',
            self.SECTION_KEY_ROLE: b'sectionKey' }

    
    def resetSections(self = None, sections = None):
        '''
        整体重置 Home 区块列表。

        :param sections: 新的区块列表。
        :return: None。
        '''
        if not sections:
            pass
        normalized_sections = (lambda .0: [ dict(section) for section in .0 if isinstance(section, dict) ])([])
        self.beginResetModel()
        self._sections = normalized_sections
        self.endResetModel()

    
    def updateSectionAt(self = None, row = None, section = None):
        '''
        更新指定行的区块数据，并只通知该行刷新。

        :param row: 目标行号。
        :param section: 新区块数据。
        :return: None。
        '''
        if not row < 0 and row >= len(self._sections) or isinstance(section, dict):
            return None
        self._sections[row] = None(section)
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [
            self.SECTION_KEY_ROLE,
            self.TITLE_ROLE,
            self.ITEMS_ROLE,
            self.IS_LOADING_ROLE])

    
    def itemsSnapshot(self = None):
        '''
        返回当前区块列表快照。

        :param: 无。
        :return: 区块列表浅拷贝。
        '''
        return (lambda .0: [ dict(section) for section in .0 ])(self._sections)

    __classcell__ = None


class _LPWiiMRadioBaseState(QObject):
    lifecycleChanged = pyqtSignal()
    pageErrorChanged = pyqtSignal()
    
    def __init__(self = None, cacheKey = None, parent = None):
        '''
        初始化状态基类。

        :param cacheKey: 状态缓存唯一键。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        if not cacheKey:
            pass
        self._cache_key = str('').strip()
        self._active_ref_count = 0
        self._last_access_ms = self._now_ms()
        self._has_page_error = False
        self._page_error_code = 0
        self._page_error_kind = ''
        self._page_error_message = ''

    
    def cacheKey(self = None):
        '''
        返回状态缓存键。

        :param: 无。
        :return: 缓存键字符串。
        '''
        return self._cache_key

    cacheKey = None(cacheKey)
    
    def activeRefCount(self = None):
        '''
        返回当前激活引用计数。

        :param: 无。
        :return: 激活引用计数。
        '''
        return self._active_ref_count

    activeRefCount = None(activeRefCount)
    
    def lastAccessMs(self = None):
        '''
        返回最后访问时间戳（毫秒）。

        :param: 无。
        :return: 毫秒时间戳。
        '''
        return self._last_access_ms

    lastAccessMs = None(lastAccessMs)
    
    def hasPageError(self = None):
        '''
        返回当前状态是否需要显示页级错误。

        :param: 无。
        :return: 需要显示页级错误返回 True。
        '''
        return self._has_page_error

    hasPageError = None(hasPageError)
    
    def pageErrorCode(self = None):
        '''
        返回页级错误状态码。

        :param: 无。
        :return: HTTP 状态码或业务错误码。
        '''
        return self._page_error_code

    pageErrorCode = None(pageErrorCode)
    
    def pageErrorKind(self = None):
        '''
        返回页级错误类型。

        :param: 无。
        :return: 稳定错误类型字符串。
        '''
        return self._page_error_kind

    pageErrorKind = None(pageErrorKind)
    
    def pageErrorMessage(self = None):
        '''
        返回页级错误说明。

        :param: 无。
        :return: 错误说明文本。
        '''
        return self._page_error_message

    pageErrorMessage = None(pageErrorMessage)
    
    def touch(self = None):
        '''
        更新最后访问时间。

        :param: 无。
        :return: None。
        '''
        self._last_access_ms = self._now_ms()

    
    def activate(self = None):
        '''
        增加激活引用计数并在首次激活时触发回调。

        :param: 无。
        :return: None。
        '''
        self._active_ref_count += 1
        self.touch()
        if self._active_ref_count == 1:
            self.onActivated()
        self.lifecycleChanged.emit()

    
    def deactivate(self = None):
        '''
        减少激活引用计数并在计数归零时触发回调。

        :param: 无。
        :return: None。
        '''
        if self._active_ref_count <= 0:
            return None
        None._active_ref_count -= 1
        self.touch()
        if self._active_ref_count == 0:
            self.onDeactivated()
        self.lifecycleChanged.emit()

    
    def canPrune(self = None, ttlMs = None, nowMs = None):
        '''
        判断状态是否可被回收。

        :param ttlMs: 回收 TTL（毫秒）。
        :param nowMs: 当前时间戳（毫秒），为空时自动取当前时间。
        :return: 可回收返回 True，否则返回 False。
        '''
        if self._active_ref_count > 0:
            return False
        now_ms = self._now_ms() if None is None else int(nowMs)
        return now_ms - self._last_access_ms >= int(ttlMs)

    
    def _clear_page_error(self = None):
        '''
        清除当前页级错误状态。

        :param: 无。
        :return: None。
        '''
        if not self._has_page_error and self._page_error_code == 0 and self._page_error_kind and self._page_error_message:
            return None
        self._has_page_error = None
        self._page_error_code = 0
        self._page_error_kind = ''
        self._page_error_message = ''
        self.pageErrorChanged.emit()

    
    def _set_page_error_from_result(self = None, result = None):
        '''
        根据接口失败结果更新页级错误状态。

        :param result: 归一化后的失败结果。
        :return: None。
        '''
        safe_result = result if isinstance(result, dict) else { }
        if not safe_result.get('errorKind', ''):
            pass
        if not str('').strip():
            pass
        error_kind = 'unknown'
        status_code = self._safe_int(safe_result.get('statusCode'), 0)
        error_code = self._safe_int(safe_result.get('errorCode'), 0)
        page_error_code = status_code if status_code > 0 else error_code
        if not safe_result.get('errorDesc', '') and safe_result.get('error', ''):
            pass
        error_message = str('unknown')
        if self._has_page_error and self._page_error_code == page_error_code and self._page_error_kind == error_kind and self._page_error_message == error_message:
            return None
        self._has_page_error = None
        self._page_error_code = page_error_code
        self._page_error_kind = error_kind
        self._page_error_message = error_message
        self.pageErrorChanged.emit()

    
    def _safe_int(self = None, value = None, default = None):
        '''
        将输入值安全转换为整数。

        :param value: 待转换的值。
        :param default: 转换失败时返回的默认值。
        :return: 整数结果。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def onActivated(self = None):
        '''
        激活回调，由子类按需覆盖。

        :param: 无。
        :return: None。
        '''
        pass

    
    def onDeactivated(self = None):
        '''
        失活回调，由子类按需覆盖。

        :param: 无。
        :return: None。
        '''
        pass

    
    def dispose(self = None):
        '''
        回收回调，由子类按需覆盖。

        :param: 无。
        :return: None。
        '''
        pass

    
    def _now_ms(self = None):
        '''
        返回当前时间戳（毫秒）。

        :param: 无。
        :return: 毫秒时间戳。
        '''
        return int(time.time() * 1000)

    __classcell__ = None


class LPWiiMRadioSeeAllState(_LPWiiMRadioBaseState):
    REMOTE_PAGE_SIZE = 100
    DEFAULT_LAYOUT_MODE = 'list'
    VALID_LAYOUT_MODES = {
        'list',
        'grid'}
    metaChanged = pyqtSignal()
    displayItemsChanged = pyqtSignal()
    searchTextChanged = pyqtSignal()
    sortKeyChanged = pyqtSignal()
    layoutModeChanged = pyqtSignal()
    loadingStateChanged = pyqtSignal()
    paginationStateChanged = pyqtSignal()
    
    def __init__(self = None, cacheKey = None, sectionDescriptor = None, parent = None):
        '''
        初始化 SeeAll 状态对象。

        :param cacheKey: 状态缓存唯一键。
        :param sectionDescriptor: 首页传入的展开页描述对象。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(cacheKey, parent)
        self._section_key = ''
        self._page_title = ''
        self._mode = 'local'
        self._base_query = { }
        self._raw_items = []
        self._entry_search_text = ''
        self._display_model = LPWiiMRadioStationListModel(self, **('parent',))
        self._search_text = ''
        self._sort_key = 'default'
        self._layout_mode = self.DEFAULT_LAYOUT_MODE
        self._sort_options = [
            {
                'value': 'default',
                'title': QCoreApplication.translate('WiiMRadio', 'Default') },
            {
                'value': 'name_asc',
                'title': QCoreApplication.translate('WiiMRadio', 'Name A-Z') },
            {
                'value': 'name_desc',
                'title': QCoreApplication.translate('WiiMRadio', 'Name Z-A') }]
        self._is_initial_loading = False
        self._is_loading_more = False
        self._has_loaded_once = False
        self._has_more = False
        self._next_page_no = 1
        self._request_revision = 0
        self._request_inflight = False
        self._deferred_remote_request = None
        self._store = LPWiiMRadioStore.instance()
        self._data_provider = LPWiiMRadioDataProvider(self, **('parent',))
        self._store.favoriteRevisionChanged.connect(self._handle_store_favorite_revision_changed)
        self._apply_descriptor(sectionDescriptor)
        if self._is_remote_mode():
            self._reload_remote_data()
        else:
            self._apply_local_filters()

    
    def pageTitle(self = None):
        '''
        返回页面标题。

        :param: 无。
        :return: 页面标题。
        '''
        return self._page_title

    pageTitle = None(pageTitle)
    
    def sectionKey(self = None):
        '''
        返回当前区块标识。

        :param: 无。
        :return: sectionKey。
        '''
        return self._section_key

    sectionKey = None(sectionKey)
    
    def sortOptions(self = None):
        '''
        返回排序选项列表。

        :param: 无。
        :return: 排序选项列表。
        '''
        return self._sort_options

    sortOptions = None(sortOptions)
    
    def displayItems(self = None):
        '''
        返回当前展示列表模型。

        :param: 无。
        :return: 列表模型对象。
        '''
        return self._display_model

    displayItems = None(displayItems)
    
    def searchText(self = None):
        '''
        返回搜索关键字。

        :param: 无。
        :return: 搜索文本。
        '''
        return self._search_text

    searchText = None(searchText)
    
    def sortKey(self = None):
        '''
        返回当前排序键。

        :param: 无。
        :return: 排序键。
        '''
        return self._sort_key

    sortKey = None(sortKey)
    
    def layoutMode(self = None):
        '''
        返回当前布局模式。

        :param: 无。
        :return: `list` 或 `grid`。
        '''
        return self._layout_mode

    layoutMode = None(layoutMode)
    
    def resultCount(self = None):
        '''
        返回结果数量。

        :param: 无。
        :return: 当前列表条目数。
        '''
        return self._display_model.count()

    resultCount = None(resultCount)
    
    def hasVisibleItems(self = None):
        '''
        返回当前是否已有可见结果。

        :param: 无。
        :return: 模型中存在条目时返回 True。
        '''
        return self._display_model.count() > 0

    hasVisibleItems = None(hasVisibleItems)
    
    def isInitialLoading(self = None):
        '''
        返回是否处于首屏加载状态。

        :param: 无。
        :return: 首屏加载中返回 True。
        '''
        return self._is_initial_loading

    isInitialLoading = None(isInitialLoading)
    
    def isLoadingMore(self = None):
        '''
        返回是否处于追加分页加载状态。

        :param: 无。
        :return: 追加加载中返回 True。
        '''
        return self._is_loading_more

    isLoadingMore = None(isLoadingMore)
    
    def canLoadMore(self = None):
        '''
        返回是否可继续加载下一页。

        :param: 无。
        :return: 可继续加载返回 True。
        '''
        if self._is_remote_mode() and self._has_more and not (self._is_initial_loading) and not (self._is_loading_more):
            pass
        return not self._display_model.isFull()

    canLoadMore = None(canLoadMore)
    
    def showEmptyState(self = None):
        '''
        返回是否展示空态。

        :param: 无。
        :return: 应显示空态返回 True。
        '''
        if self._has_loaded_once and self._display_model.count() == 0 and not (self._is_initial_loading):
            pass
        return not (self._has_page_error)

    showEmptyState = None(showEmptyState)
    
    def setSearchText(self = None, text = None):
        '''
        设置搜索关键字，仅保存输入内容，等待回车后执行搜索。

        :param text: 搜索文本。
        :return: None。
        '''
        if not text:
            pass
        next_text = str('')
        if next_text == self._search_text:
            return None
        self._search_text = None
        self.searchTextChanged.emit()
        self.touch()

    
    def triggerSearch(self = None):
        '''
        立即执行搜索。

        :param: 无。
        :return: None。
        '''
        self._trigger_search()
        self.touch()

    
    def setSortKey(self = None, sortKey = None):
        '''
        设置排序键并刷新结果。

        :param sortKey: 目标排序键。
        :return: None。
        '''
        next_sort_key = self._normalize_sort_key(sortKey)
        if next_sort_key == self._sort_key:
            return None
        self._sort_key = None
        self.sortKeyChanged.emit()
        if self._is_remote_mode():
            self._reload_remote_data()
        else:
            self._apply_local_filters()
        self.touch()

    
    def setLayoutMode(self = None, layoutMode = None):
        '''
        设置当前布局模式。

        :param layoutMode: 目标布局模式。
        :return: None。
        '''
        next_layout_mode = self._normalize_layout_mode(layoutMode)
        if next_layout_mode == self._layout_mode:
            return None
        self._layout_mode = None
        self.layoutModeChanged.emit()
        self.touch()

    
    def resetLayoutMode(self = None):
        '''
        重置布局模式为默认列表布局。

        :param: 无。
        :return: None。
        '''
        self.setLayoutMode(self.DEFAULT_LAYOUT_MODE)

    
    def toggleLayoutMode(self = None):
        '''
        在列表和网格布局间切换。

        :param: 无。
        :return: None。
        '''
        self.setLayoutMode('grid' if self._layout_mode == 'list' else 'list')

    
    def loadNextPage(self = None):
        '''
        在可翻页时加载下一页。

        :param: 无。
        :return: None。
        '''
        if not self.canLoadMore:
            return None
        self._is_loading_more = None
        self.loadingStateChanged.emit()
        self._request_remote_page(self._next_page_no, True, LPWiiMRadioRequestScheduler.PRIORITY_PRELOAD, **('append', 'priority'))
        self.touch()

    
    def retryLoadPage(self = None):
        '''
        重试当前 SeeAll 页第一页数据请求。

        :param: 无。
        :return: None。
        '''
        if self._is_remote_mode():
            self._reload_remote_data()
        else:
            self._clear_page_error()
            self._apply_local_filters()
        self.touch()

    
    def findItemByStationId(self = None, stationId = None):
        '''
        根据 stationId 查找条目。

        :param stationId: 电台唯一标识。
        :return: 找到返回条目副本，否则返回 None。
        '''
        self.touch()
        return self._display_model.findItemByStationId(stationId)

    
    def syncEntrySearchText(self = None, searchText = None):
        '''
        在重复进入同一状态时同步入口搜索词。

        :param searchText: 入口携带的搜索词。
        :return: None。
        '''
        if not searchText:
            pass
        next_text = str('')
        if next_text == self._entry_search_text:
            return None
        self._entry_search_text = None
        if next_text == self._search_text:
            return None
        self._search_text = None
        self.searchTextChanged.emit()
        if self._is_remote_mode():
            self._reload_remote_data()
        else:
            self._apply_local_filters()

    
    def onActivated(self = None):
        '''
        状态激活时恢复模型信号连接。

        :param: 无。
        :return: None。
        '''
        self._display_model.reconnect()

    
    def onDeactivated(self = None):
        '''
        状态失活时断开模型信号连接。

        :param: 无。
        :return: None。
        '''
        self._display_model.cleanup()

    
    def dispose(self = None):
        '''
        回收状态时释放模型数据与信号连接。

        :param: 无。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _apply_descriptor(self = None, sectionDescriptor = None):
        '''
        应用入口描述对象。

        :param sectionDescriptor: 展开页描述对象。
        :return: None。
        '''
        descriptor = sectionDescriptor if isinstance(sectionDescriptor, dict) else { }
        if not descriptor.get('sectionKey', ''):
            pass
        self._section_key = str('').strip()
        if not descriptor.get('title', ''):
            pass
        self._page_title = str('').strip()
        if not descriptor.get('mode', 'local'):
            pass
        self._mode = str('local').strip().lower()
        base_query = descriptor.get('baseQuery', { })
        if not self._mode == 'remote' and _is_popular_section_key(self._section_key):
            self._base_query = _build_query_without_location_codes(base_query)
        elif isinstance(base_query, dict):
            pass
        
        self._base_query = { }
        if not descriptor.get('searchText', ''):
            pass
        self._entry_search_text = str('')
        self._search_text = self._entry_search_text
        self.metaChanged.emit()
        self.searchTextChanged.emit()

    
    def _is_favorites_section(self = None):
        '''
        判断当前 SeeAll 是否为 favorites 页面。

        :param: 无。
        :return: favorites 页面返回 True。
        '''
        return self._section_key == LPWiiMRadioHomeState.FAVORITES_SECTION_KEY

    
    def _sync_favorites_raw_items(self = None):
        '''
        从 Store 同步最新 favorites 快照到本地原始列表。

        :param: 无。
        :return: None。
        '''
        self._raw_items = self._normalize_items(self._store.favoritesSnapshot())

    
    def _handle_store_favorite_revision_changed(self = None):
        '''
        处理 Store favorites 修订变化，保持 favorites SeeAll 实时同步。

        :param: 无。
        :return: None。
        '''
        if not self._is_favorites_section():
            return None
        None._sync_favorites_raw_items()
        self._apply_local_filters()
        self.touch()

    
    def _normalize_items(self = None, rawItems = None):
        '''
        将输入条目转换为统一结构。

        :param rawItems: 原始条目列表。
        :return: 归一化后的条目列表。
        '''
        normalized_items = []
        if not rawItems:
            pass
    # WARNING: Decompyle incomplete

    
    def _normalize_sort_key(self = None, sortKey = None):
        '''
        归一化排序键。

        :param sortKey: 原始排序键。
        :return: 合法排序键。
        '''
        if not sortKey:
            pass
        if not str('default').strip():
            pass
        next_sort_key = 'default'
        valid_keys = (lambda .0: pass# WARNING: Decompyle incomplete
)(self._sort_options)
        if next_sort_key in valid_keys:
            return next_sort_key

    
    def _normalize_layout_mode(self = None, layoutMode = None):
        '''
        归一化布局模式。

        :param layoutMode: 原始布局模式。
        :return: 合法布局模式。
        '''
        if not layoutMode:
            pass
        if not str(self.DEFAULT_LAYOUT_MODE).strip().lower():
            pass
        next_layout_mode = self.DEFAULT_LAYOUT_MODE
        if next_layout_mode in self.VALID_LAYOUT_MODES:
            return next_layout_mode
        return None.DEFAULT_LAYOUT_MODE

    
    def _is_remote_mode(self = None):
        '''
        判断是否远程分页模式。

        :param: 无。
        :return: 远程模式返回 True。
        '''
        return self._mode == 'remote'

    
    def _apply_local_filters(self = None):
        '''
        按本地模式应用搜索与排序过滤。

        :param: 无。
        :return: None。
        '''
        self._clear_page_error()
        search_text = self._search_text.strip().lower()
        filtered_items = []
        for item in self._raw_items:
            if search_text and search_text not in item.get('name', '').lower():
                continue
            filtered_items.append(dict(item))
        if self._sort_key == 'name_asc':
            filtered_items.sort((lambda row: row.get('name', '').lower()), **('key',))
        elif self._sort_key == 'name_desc':
            filtered_items.sort((lambda row: row.get('name', '').lower()), True, **('key', 'reverse'))
        self._display_model.resetItems(filtered_items)
        self._has_loaded_once = True
        self._has_more = False
        self.displayItemsChanged.emit()
        self.paginationStateChanged.emit()

    
    def _trigger_search(self = None):
        '''
        根据模式执行搜索。

        :param: 无。
        :return: None。
        '''
        if self._is_remote_mode():
            self._reload_remote_data()
        else:
            self._apply_local_filters()

    
    def _reload_remote_data(self = None):
        '''
        重置并重新加载第一页远程数据。

        :param: 无。
        :return: None。
        '''
        self._request_revision += 1
        self._clear_page_error()
        self._display_model.clear()
        self._has_loaded_once = False
        self._has_more = False
        self._next_page_no = 1
        self._is_initial_loading = True
        self._is_loading_more = False
        self.displayItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._request_remote_page(1, False, LPWiiMRadioRequestScheduler.PRIORITY_VISIBLE, **('append', 'priority'))

    
    def _request_remote_page(self, pageNo = None, append = None, baseQueryOverride = None, popularFallbackRetried = (None, False, LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND), priority = {
        'pageNo': int,
        'append': bool,
        'baseQueryOverride': Optional[Dict[(str, Any)]],
        'popularFallbackRetried': bool,
        'priority': str,
        'return': None }):
        '''
        请求指定页码的远程数据。

        :param pageNo: 页码。
        :param append: 是否为追加模式。
        :param baseQueryOverride: 可选的临时基础查询参数。
        :param popularFallbackRetried: 是否已经执行过 popular 回退请求。
        :param priority: 调度优先级。
        :return: None。
        '''
        if self._request_inflight:
            if not priority:
                pass
            self._deferred_remote_request = {
                'pageNo': int(pageNo),
                'append': bool(append),
                'baseQueryOverride': copy.deepcopy(baseQueryOverride) if isinstance(baseQueryOverride, dict) else None,
                'popularFallbackRetried': bool(popularFallbackRetried),
                'priority': str(LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND) }
            return None
        self._request_inflight = None
        payload = self._build_remote_payload(pageNo, baseQueryOverride, **('baseQueryOverride',))
        context = {
            'revision': self._request_revision,
            'append': append,
            'pageNo': pageNo,
            'requestPayload': copy.deepcopy(payload),
            'popularFallbackRetried': popularFallbackRetried }
        self._data_provider.fetchStations(payload, self._make_weak_result_callback(), context, priority, **('callback', 'context', 'priority'))

    
    def _make_weak_result_callback(self):
        '''
        构造弱引用回调，避免线程回调强持有状态对象。

        :param: 无。
        :return: 回调函数。
        '''
        state_ref = weakref.ref(self)
        
        def _callback(result = None):
            '''
            处理远程请求回调。

            :param result: 归一化分页结果。
            :return: None。
            '''
            state = state_ref()
            if state is not None:
                state._handle_remote_result(result)

        return _callback

    
    def _build_remote_payload(self = None, pageNo = None, baseQueryOverride = None):
        '''
        构建远程请求体。

        :param pageNo: 页码。
        :param baseQueryOverride: 可选的临时基础查询参数。
        :return: 请求体字典。
        '''
        source_query = baseQueryOverride if isinstance(baseQueryOverride, dict) else self._base_query
        payload = copy.deepcopy(source_query)
        payload['pageNo'] = pageNo
        payload['pageSize'] = self.REMOTE_PAGE_SIZE
        keyword = self._search_text.strip()
        if not keyword:
            pass
        payload['name'] = None
        payload['customName'] = None
        payload['tags'] = None
        payload['customTags'] = []
        if self._sort_key == 'name_asc':
            payload['orderByStr'] = 'name'
            payload['sortStr'] = 'ASC'
        elif self._sort_key == 'name_desc':
            payload['orderByStr'] = 'name'
            payload['sortStr'] = 'DESC'
        return payload

    
    def _handle_remote_result(self = None, result = None):
        '''
        处理远程请求结果。

        :param result: 归一化分页结果。
        :return: None。
        '''
        context = result.get('context', { }) if isinstance(result, dict) else { }
        revision = int(context.get('revision', -1)) if isinstance(context, dict) else -1
        append = bool(context.get('append')) if isinstance(context, dict) else False
        page_no = int(context.get('pageNo', 1)) if isinstance(context, dict) else 1
        self._request_inflight = False
        if revision != self._request_revision:
            logger.debug(f'''[WiiMRadio] ignore stale seeall response section={self._section_key}, revision={revision}''')
            self._flush_deferred_remote_request()
            return None
        if None(self._section_key, result, context):
            request_payload = context.get('requestPayload', { }) if isinstance(context, dict) else { }
            fallback_payload = _build_query_without_subcountry_code(request_payload)
            self._base_query = _build_query_without_subcountry_code(self._base_query)
            logger.info(f'''[WiiMRadio] seeall popular empty with subcountryCode, retry country-only section={self._section_key}''')
            self._request_remote_page(page_no, False, fallback_payload, True, LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND, **('append', 'baseQueryOverride', 'popularFallbackRetried', 'priority'))
            return None
        success = bool(result.get('success')) if None(result, dict) else False
        items = result.get('items', []) if isinstance(result, dict) else []
        has_more = bool(result.get('hasMore')) if isinstance(result, dict) else False
        error = str('') if isinstance(result, dict) else ''
        if append:
            self._is_loading_more = False
        else:
            self._is_initial_loading = False
        had_visible_items = self._display_model.count() > 0
        if success:
            self._clear_page_error()
            if append:
                self._display_model.appendItems(items)
            else:
                self._display_model.resetItems(items)
            self._has_loaded_once = True
            self._has_more = has_more
            self._next_page_no = page_no + 1
        elif not error:
            pass
        '[WiiMRadio] seeall load failed section='(f'''{self._section_key}, error={'unknown'}''')
        self._next_page_no = page_no
        self.displayItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._flush_deferred_remote_request()

    
    def _flush_deferred_remote_request(self = None):
        '''
        在当前远程请求结束后，补发最后一次被覆盖的请求。

        :param: 无。
        :return: None。
        '''
        deferred_request = self._deferred_remote_request
        self._deferred_remote_request = None
        if not isinstance(deferred_request, dict):
            return None
        if not deferred_request.get('priority', LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND):
            pass
        None._request_remote_page(deferred_request.get('pageNo', 1), bool(deferred_request.get('append')), deferred_request.get('baseQueryOverride'), bool(deferred_request.get('popularFallbackRetried')), str(LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND), **('baseQueryOverride', 'popularFallbackRetried', 'priority'))

    __classcell__ = None


class LPWiiMRadioCategoryState(_LPWiiMRadioBaseState):
    stationItemsChanged = pyqtSignal()
    searchTextChanged = pyqtSignal()
    layoutModeChanged = pyqtSignal()
    loadingStateChanged = pyqtSignal()
    paginationStateChanged = pyqtSignal()
    metaChanged = pyqtSignal()
    STATION_PAGE_SIZE = 100
    DEFAULT_LAYOUT_MODE = 'list'
    VALID_LAYOUT_MODES = {
        'list',
        'grid'}
    
    def __init__(self = None, cacheKey = None, categoryDescriptor = None, parent = None):
        '''
        初始化分类详情状态对象。

        :param cacheKey: 状态缓存唯一键。
        :param categoryDescriptor: 分类详情描述对象。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(cacheKey, parent)
        self._category_key = ''
        self._page_title = ''
        self._base_query = { }
        self._requires_country_code = False
        self._station_model = LPWiiMRadioStationListModel(self, **('parent',))
        self._search_text = ''
        self._layout_mode = self.DEFAULT_LAYOUT_MODE
        self._is_station_loading = False
        self._is_loading_more = False
        self._station_has_loaded_once = False
        self._has_more = False
        self._next_page_no = 1
        self._request_revision = 0
        self._is_waiting_for_country_code = False
        self._request_inflight = False
        self._deferred_station_request = None
        self._country_code_resolver = LPGlobalUI.wiimRadioCountryCodeResolver
        self._country_code_resolver.stateChanged.connect(self._handle_country_code_resolver_state_changed)
        self._data_provider = LPWiiMRadioDataProvider(self, **('parent',))
        self._apply_descriptor(categoryDescriptor)
        self._reload_stations()

    
    def pageTitle(self = None):
        '''
        返回页面标题。

        :param: 无。
        :return: 页面标题。
        '''
        return self._page_title

    pageTitle = None(pageTitle)
    
    def categoryKey(self = None):
        '''
        返回分类唯一标识。

        :param: 无。
        :return: categoryKey。
        '''
        return self._category_key

    categoryKey = None(categoryKey)
    
    def stationItems(self = None):
        '''
        返回 stations 列表模型。

        :param: 无。
        :return: 列表模型对象。
        '''
        return self._station_model

    stationItems = None(stationItems)
    
    def hasVisibleItems(self = None):
        '''
        返回当前是否已有可见 station 结果。

        :param: 无。
        :return: station 模型存在条目时返回 True。
        '''
        return self._station_model.count() > 0

    hasVisibleItems = None(hasVisibleItems)
    
    def searchText(self = None):
        '''
        返回搜索文本。

        :param: 无。
        :return: 搜索文本。
        '''
        return self._search_text

    searchText = None(searchText)
    
    def layoutMode(self = None):
        '''
        返回当前布局模式。

        :param: 无。
        :return: `list` 或 `grid`。
        '''
        return self._layout_mode

    layoutMode = None(layoutMode)
    
    def isStationLoading(self = None):
        '''
        返回是否处于首屏 loading。

        :param: 无。
        :return: 首屏 loading 中返回 True。
        '''
        return self._is_station_loading

    isStationLoading = None(isStationLoading)
    
    def isLoadingMore(self = None):
        '''
        返回是否处于追加分页 loading。

        :param: 无。
        :return: 追加 loading 中返回 True。
        '''
        return self._is_loading_more

    isLoadingMore = None(isLoadingMore)
    
    def canLoadMore(self = None):
        '''
        返回是否可继续加载下一页。

        :param: 无。
        :return: 可继续加载返回 True。
        '''
        if self._has_more and not (self._is_station_loading) and not (self._is_loading_more):
            pass
        return not self._station_model.isFull()

    canLoadMore = None(canLoadMore)
    
    def showStationEmptyState(self = None):
        '''
        返回是否显示 stations 空态。

        :param: 无。
        :return: 应显示空态返回 True。
        '''
        if self._station_has_loaded_once and not (self._is_station_loading) and self._station_model.count() == 0:
            pass
        return not (self._has_page_error)

    showStationEmptyState = None(showStationEmptyState)
    
    def setSearchText(self = None, text = None):
        '''
        设置搜索文本，仅保存输入内容，等待回车后执行搜索。

        :param text: 搜索文本。
        :return: None。
        '''
        if not text:
            pass
        next_text = str('')
        if next_text == self._search_text:
            return None
        self._search_text = None
        self.searchTextChanged.emit()
        self.touch()

    
    def triggerSearch(self = None):
        '''
        立即执行搜索。

        :param: 无。
        :return: None。
        '''
        self._reload_stations()
        self.touch()

    
    def setLayoutMode(self = None, layoutMode = None):
        '''
        设置当前布局模式。

        :param layoutMode: 目标布局模式。
        :return: None。
        '''
        next_layout_mode = self._normalize_layout_mode(layoutMode)
        if next_layout_mode == self._layout_mode:
            return None
        self._layout_mode = None
        self.layoutModeChanged.emit()
        self.touch()

    
    def resetLayoutMode(self = None):
        '''
        重置布局模式为默认列表布局。

        :param: 无。
        :return: None。
        '''
        self.setLayoutMode(self.DEFAULT_LAYOUT_MODE)

    
    def toggleLayoutMode(self = None):
        '''
        在列表和网格布局间切换。

        :param: 无。
        :return: None。
        '''
        self.setLayoutMode('grid' if self._layout_mode == 'list' else 'list')

    
    def loadNextPage(self = None):
        '''
        在可翻页时请求下一页。

        :param: 无。
        :return: None。
        '''
        if not self.canLoadMore:
            return None
        self._is_loading_more = None
        self.loadingStateChanged.emit()
        self._request_station_page(self._next_page_no, True, LPWiiMRadioRequestScheduler.PRIORITY_PRELOAD, **('append', 'priority'))
        self.touch()

    
    def retryLoadPage(self = None):
        '''
        重试当前分类详情页第一页 stations 请求。

        :param: 无。
        :return: None。
        '''
        self._clear_page_error()
        self._reload_stations()
        self.touch()

    
    def findItemByStationId(self = None, stationId = None):
        '''
        根据 stationId 查找条目。

        :param stationId: 电台唯一标识。
        :return: 找到返回条目副本，否则返回 None。
        '''
        self.touch()
        return self._station_model.findItemByStationId(stationId)

    
    def onActivated(self = None):
        '''
        激活时恢复模型信号连接。

        :param: 无。
        :return: None。
        '''
        self._station_model.reconnect()

    
    def onDeactivated(self = None):
        '''
        失活时断开模型信号连接。

        :param: 无。
        :return: None。
        '''
        self._station_model.cleanup()

    
    def dispose(self = None):
        '''
        回收状态时释放模型数据与回调有效性。

        :param: 无。
        :return: None。
        '''
        self._station_model.cleanup()
        self._station_model.clear()
        self._request_revision += 1
        self._request_inflight = False
        self._deferred_station_request = None

    
    def _apply_descriptor(self = None, categoryDescriptor = None):
        '''
        应用分类入口描述对象。

        :param categoryDescriptor: 分类详情描述对象。
        :return: None。
        '''
        descriptor = categoryDescriptor if isinstance(categoryDescriptor, dict) else { }
        if not descriptor.get('categoryKey', ''):
            pass
        self._category_key = str('').strip()
        if not descriptor.get('title', ''):
            pass
        self._page_title = str('').strip()
        base_query = descriptor.get('baseQuery', { })
        self._base_query = copy.deepcopy(base_query) if isinstance(base_query, dict) else { }
        self._requires_country_code = bool(descriptor.get('requiresCountryCode'))
        if not descriptor.get('searchText', ''):
            pass
        self._search_text = str('')
        self.metaChanged.emit()
        self.searchTextChanged.emit()

    
    def _reload_stations(self = None):
        '''
        重置并加载第一页 stations。

        :param: 无。
        :return: None。
        '''
        self._clear_page_error()
        if not self._requires_country_code and self._country_code_resolver.hasResolved:
            self._begin_waiting_for_country_code()
            return None
        None._sync_country_code_into_base_query()
        self._request_revision += 1
        self._is_waiting_for_country_code = False
        self._is_station_loading = True
        self._is_loading_more = False
        self._station_has_loaded_once = False
        self._has_more = False
        self._next_page_no = 1
        self._station_model.clear()
        self.stationItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._request_station_page(1, False, LPWiiMRadioRequestScheduler.PRIORITY_VISIBLE, **('append', 'priority'))

    
    def _begin_waiting_for_country_code(self = None):
        '''
        进入等待全局 countryCode 的首屏 loading 状态。

        :param: 无。
        :return: None。
        '''
        self._request_revision += 1
        self._is_waiting_for_country_code = True
        self._is_station_loading = True
        self._is_loading_more = False
        self._station_has_loaded_once = False
        self._has_more = False
        self._next_page_no = 1
        self._station_model.clear()
        self.stationItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._country_code_resolver.ensureLoaded()

    
    def _handle_country_code_resolver_state_changed(self = None):
        '''
        处理全局 countryCode 解析结果并恢复分类数据加载。

        :param: 无。
        :return: None。
        '''
        if not self._requires_country_code or self._country_code_resolver.hasResolved:
            return None
        if not None._is_waiting_for_country_code:
            return None
        None._reload_stations()

    
    def _sync_country_code_into_base_query(self = None):
        '''
        将全局解析出的 countryCode 回填到分类基础查询参数。

        :param: 无。
        :return: None。
        '''
        if not self._requires_country_code:
            return None
        if not self._country_code_resolver.countryCode:
            pass
        normalized = None('').strip().upper()
        self._base_query['countryCode'] = normalized if len(normalized) == 2 else ''

    
    def _request_station_page(self = None, pageNo = None, append = None, priority = (LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND,)):
        '''
        请求指定页码 stations 数据。

        :param pageNo: 页码。
        :param append: 是否追加模式。
        :param priority: 调度优先级。
        :return: None。
        '''
        if self._request_inflight:
            if not priority:
                pass
            self._deferred_station_request = {
                'pageNo': int(pageNo),
                'append': bool(append),
                'priority': str(LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND) }
            return None
        self._request_inflight = None
        payload = self._build_station_query(pageNo)
        context = {
            'revision': self._request_revision,
            'append': append,
            'pageNo': pageNo }
        self._data_provider.fetchStations(payload, self._make_weak_station_callback(), context, priority, **('callback', 'context', 'priority'))

    
    def _make_weak_station_callback(self):
        '''
        构造弱引用回调。

        :param: 无。
        :return: 回调函数。
        '''
        state_ref = weakref.ref(self)
        
        def _callback(result = None):
            '''
            处理 stations 请求回调。

            :param result: 归一化分页结果。
            :return: None。
            '''
            state = state_ref()
            if state is not None:
                state._handle_station_result(result)

        return _callback

    
    def _build_station_query(self = None, pageNo = None):
        '''
        构建 stations 请求体。

        :param pageNo: 页码。
        :return: 请求体字典。
        '''
        payload = copy.deepcopy(self._base_query)
        payload['pageNo'] = pageNo
        payload['pageSize'] = self.STATION_PAGE_SIZE
        payload['customName'] = None
        payload['tags'] = None
        payload['customTags'] = []
        if not self._search_text.strip():
            pass
        payload['name'] = None
        return payload

    
    def _handle_station_result(self = None, result = None):
        '''
        处理 stations 请求结果。

        :param result: 归一化分页结果。
        :return: None。
        '''
        context = result.get('context', { }) if isinstance(result, dict) else { }
        revision = int(context.get('revision', -1)) if isinstance(context, dict) else -1
        append = bool(context.get('append')) if isinstance(context, dict) else False
        page_no = int(context.get('pageNo', 1)) if isinstance(context, dict) else 1
        self._request_inflight = False
        if revision != self._request_revision:
            logger.debug(f'''[WiiMRadio] ignore stale category response revision={revision}''')
            self._flush_deferred_station_request()
            return None
        success = bool(result.get('success')) if None(result, dict) else False
        items = result.get('items', []) if isinstance(result, dict) else []
        has_more = bool(result.get('hasMore')) if isinstance(result, dict) else False
        error = str('') if isinstance(result, dict) else ''
        if append:
            self._is_loading_more = False
        else:
            self._is_station_loading = False
        had_visible_items = self._station_model.count() > 0
        if success:
            self._clear_page_error()
        elif not error:
            pass
        '[WiiMRadio] category stations load failed category='(f'''{self._category_key}, error={'empty'}''')
        self._has_more = False
        self._next_page_no = page_no
        self._station_has_loaded_once = True
        self.stationItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._flush_deferred_station_request()
        return None
        self._station_has_loaded_once = True
        self._has_more = has_more
        self._next_page_no = page_no + 1
        self.stationItemsChanged.emit()
        self.loadingStateChanged.emit()
        self.paginationStateChanged.emit()
        self._flush_deferred_station_request()

    
    def _flush_deferred_station_request(self = None):
        '''
        在当前 stations 请求结束后，补发最后一次被覆盖的请求。

        :param: 无。
        :return: None。
        '''
        deferred_request = self._deferred_station_request
        self._deferred_station_request = None
        if not isinstance(deferred_request, dict):
            return None
        if not deferred_request.get('priority', LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND):
            pass
        None._request_station_page(deferred_request.get('pageNo', 1), bool(deferred_request.get('append')), str(LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND), **('priority',))

    
    def _normalize_layout_mode(self = None, layoutMode = None):
        '''
        归一化布局模式。

        :param layoutMode: 原始布局模式。
        :return: 合法布局模式。
        '''
        if not layoutMode:
            pass
        if not str(self.DEFAULT_LAYOUT_MODE).strip().lower():
            pass
        next_layout_mode = self.DEFAULT_LAYOUT_MODE
        if next_layout_mode in self.VALID_LAYOUT_MODES:
            return next_layout_mode
        return None.DEFAULT_LAYOUT_MODE

    __classcell__ = None


class LPWiiMRadioHomeState(_LPWiiMRadioBaseState):
    sectionDataChanged = pyqtSignal()
    searchTextChanged = pyqtSignal()
    searchStateChanged = pyqtSignal()
    isInitialLoadingChanged = pyqtSignal()
    favoriteRevisionChanged = pyqtSignal()
    FAVORITES_SECTION_KEY = 'favorites'
    CATEGORY_SECTION_KEY = 'category'
    SEARCH_SECTION_KEY = 'homeSearch'
    HOME_SEARCH_PAGE_SIZE = 100
    
    def __init__(self = None, cacheKey = None, parent = None):
        '''
        初始化 Home 状态对象。

        :param cacheKey: 状态缓存唯一键。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(cacheKey, parent)
        self._favorite_revision = 0
        self._favorites = self._load_favorites()
        self._section_data = []
        self._section_model = LPWiiMRadioHomeSectionListModel(self, **('parent',))
        self._country_code_resolver = LPGlobalUI.wiimRadioCountryCodeResolver
        self._country_code_resolver.stateChanged.connect(self._handle_country_code_resolver_state_changed)
        self._remote_sections_initialized = False
        self._remote_section_specs = []
        self._remote_section_items = { }
        self._loaded_remote_sections = set()
        self._category_section = self._build_static_category_section()
        self._search_text = ''
        self._search_results = []
        self._is_search_loading = False
        self._search_has_loaded_once = False
        self._search_request_revision = 0
        self._is_initial_loading = True
        self._thumbnail_service = LPWiiMRadioThumbnailService.instance()
        self._thumbnail_service.thumbnailReady.connect(self._handle_thumbnail_ready)
        self._data_provider = LPWiiMRadioDataProvider(self, **('parent',))
        self._thumbnail_rebuild_timer = QTimer(self)
        self._thumbnail_rebuild_timer.setSingleShot(True)
        self._thumbnail_rebuild_timer.setInterval(200)
        self._thumbnail_rebuild_timer.timeout.connect(self._rebuild_section_data)
        self._section_visible_ranges = { }
        self._rebuild_section_data()
        self._initialize_remote_sections()

    
    def isInitialLoading(self = None):
        '''
        返回首页是否处于首屏加载状态。

        :param: 无。
        :return: 首屏加载中返回 True。
        '''
        return self._is_initial_loading

    isInitialLoading = None(isInitialLoading)
    
    def sectionData(self = None):
        '''
        返回首页区块数据。

        :param: 无。
        :return: 区块模型对象。
        '''
        return self._section_model

    sectionData = None(sectionData)
    
    def favoriteRevision(self = None):
        '''
        返回收藏修订号。

        :param: 无。
        :return: 收藏修订号。
        '''
        return self._favorite_revision

    favoriteRevision = None(favoriteRevision)
    
    def searchText(self = None):
        '''
        返回搜索文本。

        :param: 无。
        :return: 搜索文本。
        '''
        return self._search_text

    searchText = None(searchText)
    
    def isSearchMode(self = None):
        '''
        返回是否处于搜索模式。

        :param: 无。
        :return: 首页内搜索请求处于加载或已加载状态时返回 True。
        '''
        if not self._is_search_loading:
            pass
        return self._search_has_loaded_once

    isSearchMode = None(isSearchMode)
    
    def isSearchLoading(self = None):
        '''
        返回是否处于搜索 loading。

        :param: 无。
        :return: 搜索 loading 中返回 True。
        '''
        return self._is_search_loading

    isSearchLoading = None(isSearchLoading)
    
    def showSearchEmptyState(self = None):
        '''
        返回是否显示搜索空态。

        :param: 无。
        :return: 应显示空态返回 True。
        '''
        if self.isSearchMode and self._search_has_loaded_once and not (self._is_search_loading):
            pass
        return not (self._search_results)

    showSearchEmptyState = None(showSearchEmptyState)
    
    def setSearchText(self = None, text = None):
        '''
        设置首页搜索文本，仅保存输入内容，不在首页内触发搜索结果刷新。

        :param text: 搜索文本。
        :return: None。
        '''
        if not text:
            pass
        next_text = str('')
        if next_text == self._search_text:
            return None
        self._search_text = None
        self._is_search_loading = False
        self._search_has_loaded_once = False
        self._search_results = []
        self.searchTextChanged.emit()
        self.searchStateChanged.emit()
        self.touch()

    
    def triggerSearch(self = None):
        '''
        保留旧入口兼容，不在首页内触发搜索。

        :param: 无。
        :return: None。
        '''
        self.touch()

    
    def isFavorite(self = None, stationId = None):
        '''
        判断电台是否已收藏。

        :param stationId: 电台唯一标识。
        :return: 已收藏返回 True。
        '''
        if not stationId:
            pass
        station_id = str('').strip()
        return None((lambda .0 = None: for item in .0:
item.get('stationId') == station_id)(self._favorites))

    
    def favoritesSnapshot(self = None):
        '''
        返回当前 favorites 快照。

        :param: 无。
        :return: favorites 条目副本列表。
        '''
        return (lambda .0: [ dict(item) for item in .0 ])(self._favorites)

    
    def reloadFavoritesFromCache(self = None):
        '''
        从统一缓存重新加载收藏列表并刷新状态，不写回缓存。

        :param: 无。
        :return: None。
        '''
        next_favorites = _ensure_wiimradio_favorites_loaded()
        if next_favorites == self._favorites:
            return None
        self._favorites = None
        self._favorite_revision += 1
        self._rebuild_section_data()
        self.favoriteRevisionChanged.emit()
        self.touch()

    
    def toggleFavoriteItem(self = None, itemData = None):
        '''
        基于完整电台数据切换收藏状态。

        :param itemData: 电台数据对象。
        :return: favorites 发生变更时返回 True，否则返回 False。
        '''
        item = self._normalize_favorite_item(itemData)
        if not item:
            return False
        station_id = None['stationId']
        if self.isFavorite(station_id):
            changed = self._remove_favorite(station_id)
        else:
            self._favorites.insert(0, item)
            changed = True
        if not changed:
            return False
        None._commit_favorites_change()
        return True

    
    def toggleFavorite(self = None, sectionKey = None, stationId = None):
        '''
        切换收藏状态并刷新区块数据。

        :param sectionKey: 来源区块标识。
        :param stationId: 电台唯一标识。
        :return: None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not stationId:
            pass
        station_id = str('').strip()
        if station_id or section_key == self.CATEGORY_SECTION_KEY:
            return None
        changed = None
        if section_key == self.FAVORITES_SECTION_KEY:
            changed = self._remove_favorite(station_id)
        elif not self.isFavorite(station_id):
            item = self.findStationItem(station_id, section_key)
            if item:
                self._favorites.insert(0, item)
                changed = True
        if not changed:
            return None
        None._commit_favorites_change()

    
    def buildSectionDescriptor(self = None, sectionKey = None):
        '''
        按 sectionKey 构建 SeeAll 描述对象。

        :param sectionKey: 区块唯一标识。
        :return: 描述对象，找不到返回 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not section_key:
            return None
        if None == self.FAVORITES_SECTION_KEY:
            return {
                'sectionKey': section_key,
                'title': QCoreApplication.translate('WiiMRadio', 'Favorites'),
                'mode': 'local',
                'items': list(self._favorites),
                'baseQuery': { } }
        if None == self.SEARCH_SECTION_KEY:
            return self.buildSearchResultDescriptor()
        spec = None._find_remote_section_spec(section_key)
        if not spec:
            return None
        return {
            'sectionKey': None,
            'title': spec.get('title', ''),
            'mode': 'remote',
            'items': list(self._remote_section_items.get(section_key, [])),
            'baseQuery': copy.deepcopy(spec.get('baseQuery', { })) if _is_popular_section_key(section_key) else _build_query_without_location_codes(spec.get('baseQuery', { })) }

    
    def buildSearchResultDescriptor(self = None, keyword = None):
        '''
        构建搜索结果页描述对象，用于从首页 push 到独立搜索结果页。

        :param keyword: 指定搜索词；为空时使用当前首页搜索文本。
        :return: 搜索词有效时返回描述对象，否则返回 None。
        '''
        search_text = str(self._search_text if keyword is None else keyword).strip()
        if not search_text:
            return None
        return {
            'sectionKey': None.SEARCH_SECTION_KEY,
            'title': QCoreApplication.translate('WiiMRadio', 'Search Results'),
            'mode': 'remote',
            'items': [],
            'baseQuery': self._build_global_search_base_query(),
            'searchText': search_text }

    
    def buildCategoryDetailDescriptor(self = None, stationId = None):
        '''
        根据分类卡片 ID 构建分类详情描述对象。

        :param stationId: 分类卡片 ID。
        :return: 描述对象，找不到返回 None。
        '''
        if not stationId:
            pass
        station_id = str('').strip()
        cat_def = None((lambda .0 = None: 