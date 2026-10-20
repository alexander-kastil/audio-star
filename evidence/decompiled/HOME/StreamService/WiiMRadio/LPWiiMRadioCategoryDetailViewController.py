# Source Generated with Decompyle++
# File: LPWiiMRadioCategoryDetailViewController.pyc (Python 3.9)

'''
WiiM Radio 分类详情页控制器（动作层）。
'''
from typing import Any, Dict, Optional
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import LPGlobalUI
from HOME.StreamService.WiiMRadio.LPWiiMRadioPlayController import LPWiiMRadioPlayController
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioStore import LPWiiMRadioStore
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPUtility import logger

class LPWiiMRadioCategoryDetailViewController(QWidget, LPWiiMRadioPlayController):
    
    def __init__(self = None, categoryDescriptor = None, parent = None):
        '''
        初始化分类详情页控制器。

        :param categoryDescriptor: 分类详情描述对象。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPWiiMRadioStore.instance()
        if not categoryDescriptor:
            pass
        self._descriptor = dict({ })
        (self._state_cache_key, self._state) = self._store.acquireCategoryState(categoryDescriptor)
        self._state.resetLayoutMode()
        self._state_active = False
        self.quickWidget = None
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._onDestroyed)
        self.deleteOnPrune = True
        self._setup_qml_page()
        self._ensure_state_active()

    
    def __del__(self):
        '''
        析构时兜底失活状态，避免激活计数泄漏。

        :param: 无。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _onDestroyed(self = None, destroyedObject = None):
        '''
        QObject 销毁回调，兜底失活状态。

        :param destroyedObject: Qt 销毁信号透传对象。
        :return: None。
        '''
        _ = destroyedObject
        self._ensure_state_inactive()

    
    def onBackClicked(self = None):
        '''
        返回上一级页面。

        :param: 无。
        :return: None。
        '''
        logger.debug(f'''[WiiMRadio] category detail back clicked category={self._state.categoryKey}''')
        LPGlobalUI.navigationManager.pop(self)

    onBackClicked = None(onBackClicked)
    
    def setSearchText(self = None, text = None):
        '''
        设置搜索关键字。

        :param text: 搜索文本。
        :return: None。
        '''
        previous_text = getattr(self._state, 'searchText', '')
        should_restore_stations = self._shouldRestoreStationsAfterSearchCleared(previous_text, text)
        self._state.setSearchText(text)
        if should_restore_stations:
            self._restoreStationsAfterSearchCleared()

    setSearchText = None(setSearchText)
    
    def triggerSearch(self = None):
        '''
        立即执行搜索。

        :param: 无。
        :return: None。
        '''
        self._state.triggerSearch()

    triggerSearch = None(triggerSearch)
    
    def _shouldRestoreStationsAfterSearchCleared(self = None, previousText = None, nextText = None):
        '''
        判断分类详情页是否需要在清空搜索词后恢复默认 stations 列表。

        :param previousText: 清空前的搜索框文本。
        :param nextText: 当前搜索框文本。
        :return: 搜索词从非空变为空时返回 True。
        '''
        if not previousText:
            pass
        previous_keyword = str('').strip()
        if not nextText:
            pass
        next_keyword = str('').strip()
        if bool(previous_keyword):
            pass
        return not next_keyword

    
    def _restoreStationsAfterSearchCleared(self = None):
        '''
        清空分类搜索词后重新加载当前分类的默认 stations 列表。

        :param: 无。
        :return: None。
        '''
        logger.debug(f'''[WiiMRadio] category search cleared, reload category={self._state.categoryKey}''')
        self._state.triggerSearch()

    
    def loadNextPage(self = None):
        '''
        触发下一页加载。

        :param: 无。
        :return: None。
        '''
        self._state.loadNextPage()

    loadNextPage = None(loadNextPage)
    
    def retryLoadPage(self = None):
        '''
        重试当前分类详情页第一页 stations 请求。

        :param: 无。
        :return: None。
        '''
        self._state.retryLoadPage()

    retryLoadPage = None(retryLoadPage)
    
    def toggleLayoutMode(self = None):
        '''
        在列表和网格布局间切换。

        :param: 无。
        :return: None。
        '''
        self._state.toggleLayoutMode()

    toggleLayoutMode = None(toggleLayoutMode)
    
    def onStationClicked(self = None, stationId = None):
        '''
        处理 station 卡片点击并触发播放。

        :param stationId: 电台唯一标识。
        :return: None。
        '''
        if not stationId:
            pass
        station_id = str('').strip()
        logger.debug(f'''[WiiMRadio] station clicked category={self._state.categoryKey}, stationId={station_id}''')
        if not self.guardWiiMRadioSupported():
            return None
        item = None._state.findItemByStationId(station_id)
        if item:
            self.playOrToggleStation(item)
            return None
        None.warning(f'''[WiiMRadio] onStationClicked: item not found stationId={station_id}''')

    onStationClicked = None(onStationClicked)
    
    def isFavorite(self = None, stationId = None):
        '''
        判断电台是否已收藏。

        :param stationId: 电台唯一标识。
        :return: 已收藏返回 True。
        '''
        return self._store.isFavorite(stationId)

    isFavorite = None(isFavorite)
    
    def toggleFavoriteItem(self = None, itemData = None):
        '''
        基于完整电台数据切换收藏状态。

        :param itemData: 电台数据对象。
        :return: None。
        '''
        payload = itemData.toVariant() if hasattr(itemData, 'toVariant') else itemData
        if not isinstance(payload, dict):
            logger.warning(f'''[WiiMRadio] category toggleFavoriteItem ignored invalid payload type={type(payload)}''')
            return None
        None._store.toggleFavoriteItem(payload)

    toggleFavoriteItem = None(toggleFavoriteItem)
    
    def viewWillAppear(self = None):
        '''
        页面显示时激活状态并注册设备信息监听；若 state 已被 TTL 回收则原地替换为全新页面。

        :param: 无。
        :return: None。
        '''
        if not self._store.hasCategoryState(self._state_cache_key):
            logger.debug(f'''[WiiMRadio] CategoryDetail state expired, replacing page key={self._state_cache_key}''')
            QTimer = QTimer
            import PyQt6.QtCore
            QTimer.singleShot(0, self._replaceWithFreshPage)
            return None
        None._ensure_qml_page()
        self._state.resetLayoutMode()
        self._ensure_state_active()
        LPUtility.registerDeviceInfoChanged(self)
        self._syncPlayingInfoFromCurrentDevice()

    
    def _replaceWithFreshPage(self = None):
        '''
        将当前过期页面原地替换为一个全新的 CategoryDetail 页面并触发数据加载。

        :param: 无。
        :return: None。
        '''
        current_idx = LPGlobalUI.rootStackedWidget.indexOf(self)
        if current_idx < 0:
            return None
        stacked_item_id = None(self, 'stackedItemId', 'wiimradio_category_detail')
        fresh = LPWiiMRadioCategoryDetailViewController(self._descriptor)
        LPGlobalUI.rootStackedWidget.insertWidget(current_idx, fresh)
        LPGlobalUI.rootStackedWidget.setCurrentWidget(fresh)
        LPGlobalUI.rootStackedWidget.removeWidget(self)
        fresh.stackedItemId = stacked_item_id
        fresh.viewWillAppear()
        self.deleteLater()

    
    def viewWillDisappear(self = None):
        '''
        页面隐藏时失活状态并注销设备信息监听。

        :param: 无。
        :return: None。
        '''
        self.clearHoverCursorStates()
        self._ensure_state_inactive()
        LPUtility.deRegisterDeviceInfoChanged(self)

    
    def deviceInfoUpdate(self = None, device = None, infoType = None, detail = {
        'infoType': str,
        'detail': dict,
        'return': None }):
        '''
        设备信息变更回调，同步更新 Store 中的播放状态。

        :param device: 触发更新的设备对象。
        :param infoType: 信息类型标识。
        :param detail: 变更详情字典。
        :return: None。
        '''
        if LPGlobalUI.currentDevice or device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None not in detail and 'trackId' not in detail and 'trackSource' not in detail:
            return None
        None._syncPlayingInfoFromDevice(device)

    
    def _ensure_state_active(self = None):
        '''
        确保状态处于激活态。

        :param: 无。
        :return: None。
        '''
        if self._state_active:
            return None
        None._store.activateCategoryState(self._state_cache_key)
        self._state_active = True

    
    def _ensure_state_inactive(self = None):
        '''
        确保状态处于失活态。

        :param: 无。
        :return: None。
        '''
        if not self._state_active:
            return None
        None._store.deactivateCategoryState(self._state_cache_key)
        self._state_active = False

    
    def _setup_qml_page(self = None):
        '''
        初始化分类详情页 QML 宿主与上下文。

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
        quick.setClearColor(LPGlobalUI.THEME_BACKGROUND_COLOR)
        quick.setStyleSheet(f'''background-color: {LPGlobalUI.THEME_BACKGROUND_COLOR.name()};''')
        ctx = quick.rootContext()
        ctx.setContextProperty('wiimRadioCategoryDetailState', self._state)
        ctx.setContextProperty('wiimRadioCategoryDetailActions', self)
        ctx.setContextProperty('wiimRadioCategoryDetailController', self._state)
        self._applySharedQmlContext(ctx)
        quick.setSource(self._resolveWiiMRadioQmlUrl(LPUIPath.WiiMRadioCategoryDetailQML, 'WiiMRadioCategoryDetail.qml'))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''[WiiMRadio] Category detail QML load failed, status={quick.status()}''')
            for err in quick.errors():
                logger.error(f'''[WiiMRadio] {err.toString()}''')
        else:
            logger.debug(f'''[WiiMRadio] Category detail QML loaded successfully, category={self._state.categoryKey}''')
        self._main_layout.addWidget(quick)
        self.quickWidget = quick

    
    def _ensure_qml_page(self = None):
        '''
        确保分类详情页 QML 视图已经创建。

        :param: 无。
        :return: None。
        '''
        if self.quickWidget is not None:
            return None
        None._setup_qml_page()

    
    def _release_qml_page(self = None):
        '''
        释放分类详情页 QML 视图，隐藏页面时主动回收 QML 树与纹理资源。

        :param: 无。
        :return: None。
        '''
        quick = self.quickWidget
        if quick is None:
            return None
        None.clearHoverCursorStates()
        self._clear_qml_context_properties(quick)
        quick.setSource(QUrl())
        self._main_layout.removeWidget(quick)
        quick.setParent(None)
        quick.deleteLater()
        self.quickWidget = None

    
    def _clear_qml_context_properties(self = None, quick = None):
        '''
        清理分类详情页 QML 上下文属性，避免旧 root object 持有 Python 对象引用。

        :param quick: 待清理的 QQuickWidget。
        :return: None。
        '''
        ctx = quick.rootContext()
        ctx.setContextProperty('wiimRadioCategoryDetailState', None)
        ctx.setContextProperty('wiimRadioCategoryDetailActions', None)
        ctx.setContextProperty('wiimRadioCategoryDetailController', None)
        self._clearSharedQmlContext(ctx)

    __classcell__ = None

