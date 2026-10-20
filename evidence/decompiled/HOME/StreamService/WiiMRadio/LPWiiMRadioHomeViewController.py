# Source Generated with Decompyle++
# File: LPWiiMRadioHomeViewController.pyc (Python 3.9)

'''
WiiM Radio 首页控制器（动作层）。
'''
from typing import Any, Dict, Optional
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtNetwork import QNetworkDiskCache
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import LPGlobalUI
from LPClientFramework import LPUtility
from HOME.StreamService.WiiMRadio.LPWiiMRadioCategoryDetailViewController import LPWiiMRadioCategoryDetailViewController
from HOME.StreamService.WiiMRadio.LPWiiMRadioPlayController import LPWiiMRadioPlayController
from HOME.StreamService.WiiMRadio.LPWiiMRadioSeeAllViewController import LPWiiMRadioSeeAllViewController
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioStore import LPWiiMRadioHomeState, LPWiiMRadioStore
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPUtility import cacheDir, logger

class LPWiiMRadioHomeViewController(QWidget, LPWiiMRadioPlayController):
    
    def __init__(self = None, parent = None):
        '''
        初始化首页控制器。

        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPWiiMRadioStore.instance()
        self._state = self._store.homeState()
        self._state_active = False
        self.quickWidget = None
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.destroyed.connect(self._onDestroyed)
        self._setup_qml_page()
        self._ensure_state_active()

    
    def __del__(self):
        '''
        析构时兜底失活 Home 状态。

        :param: 无。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _onDestroyed(self = None, destroyedObject = None):
        '''
        QObject 销毁回调，兜底失活 Home 状态。

        :param destroyedObject: Qt 销毁信号透传对象。
        :return: None。
        '''
        _ = destroyedObject
        self._ensure_state_inactive()

    
    def onSeeAllClicked(self = None, sectionKey = None):
        '''
        处理首页 See All 点击并进入展开页。

        :param sectionKey: 区块唯一标识。
        :return: None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        logger.debug(f'''[WiiMRadio] onSeeAllClicked section={section_key}''')
        if section_key or section_key == LPWiiMRadioHomeState.CATEGORY_SECTION_KEY:
            return None
        if not None.guardWiiMRadioSupported():
            return None
        descriptor = None._state.buildSectionDescriptor(section_key)
        if not descriptor:
            logger.warning(f'''[WiiMRadio] onSeeAllClicked missing descriptor section={section_key}''')
            return None
        page = None(descriptor, self)
        LPGlobalUI.navigationManager.push(page, 'wiimradio_see_all')

    onSeeAllClicked = None(onSeeAllClicked)
    
    def onCardClicked(self = None, sectionKey = None, stationId = pyqtSlot(str, str)):
        '''
        处理首页卡片点击。

        :param sectionKey: 当前区块唯一标识。
        :param stationId: 被点击电台/分类卡片唯一标识。
        :return: None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not stationId:
            pass
        station_id = str('').strip()
        logger.debug(f'''[WiiMRadio] onCardClicked section={section_key}, stationId={station_id}''')
        if section_key == LPWiiMRadioHomeState.CATEGORY_SECTION_KEY:
            if not self.guardWiiMRadioSupported():
                return None
            descriptor = None._state.buildCategoryDetailDescriptor(station_id)
            if not descriptor:
                logger.warning(f'''[WiiMRadio] missing category descriptor stationId={station_id}''')
                return None
            page = None(descriptor, self)
            LPGlobalUI.navigationManager.push(page, 'wiimradio_category_detail')
            return None
        item = None._state.findStationItem(station_id, section_key)
        if item:
            self.playOrToggleStation(item)
            return None
        None.warning(f'''[WiiMRadio] onCardClicked: item not found section={section_key}, stationId={station_id}''')

    onCardClicked = None(onCardClicked)
    
    def setSearchText(self = None, text = None):
        '''
        更新首页搜索关键字。

        :param text: 搜索文本。
        :return: None。
        '''
        self._state.setSearchText(text)

    setSearchText = None(setSearchText)
    
    def triggerSearch(self = None):
        '''
        提交首页搜索并进入独立搜索结果页。

        :param: 无。
        :return: None。
        '''
        keyword = self._state.searchText.strip()
        if not keyword:
            self._state.triggerSearch()
            return None
        if not None.guardWiiMRadioSupported():
            return None
        descriptor = None._state.buildSearchResultDescriptor(keyword)
        if not descriptor:
            return None
        page = None(descriptor, self)
        LPGlobalUI.navigationManager.push(page, 'wiimradio_search_results')

    triggerSearch = None(triggerSearch)
    
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
            logger.warning(f'''[WiiMRadio] toggleFavoriteItem ignored invalid payload type={type(payload)}''')
            return None
        None._store.toggleFavoriteItem(payload)

    toggleFavoriteItem = None(toggleFavoriteItem)
    
    def toggleFavorite(self = None, sectionKey = None, stationId = pyqtSlot(str, str)):
        '''
        切换电台收藏状态。

        :param sectionKey: 来源区块唯一标识。
        :param stationId: 电台唯一标识。
        :return: None。
        '''
        self._state.toggleFavorite(sectionKey, stationId)

    toggleFavorite = None(toggleFavorite)
    
    def viewWillAppear(self = None):
        '''
        页面显示时激活 Home 状态并注册设备信息监听。

        :param: 无。
        :return: None。
        '''
        self._ensure_qml_page()
        self._ensure_state_active()
        LPUtility.registerDeviceInfoChanged(self)
        self._syncPlayingInfoFromCurrentDevice()

    
    def viewWillDisappear(self = None):
        '''
        页面隐藏时失活 Home 状态并注销设备信息监听。

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
        确保 Home 状态处于激活态。

        :param: 无。
        :return: None。
        '''
        if self._state_active:
            return None
        None._store.activateHomeState()
        self._state_active = True

    
    def _ensure_state_inactive(self = None):
        '''
        确保 Home 状态处于失活态。

        :param: 无。
        :return: None。
        '''
        if not self._state_active:
            return None
        None._store.deactivateHomeState()
        self._state_active = False

    
    def _setup_qml_page(self = None):
        '''
        初始化首页 QML 宿主与上下文。

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
        ctx.setContextProperty('wiimRadioHomeState', self._state)
        ctx.setContextProperty('wiimRadioHomeActions', self)
        ctx.setContextProperty('wiimRadioController', self._state)
        self._applySharedQmlContext(ctx)
        img_cache = QNetworkDiskCache(quick)
        img_cache.setCacheDirectory(str(cacheDir / 'wiimradio_image_cache'))
        img_cache.setMaximumCacheSize(209715200)
        quick.engine().networkAccessManager().setCache(img_cache)
        quick.setSource(self._resolveWiiMRadioQmlUrl(LPUIPath.WiiMRadioHomeQML, 'WiiMRadioHome.qml'))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''[WiiMRadio] QML load failed, status={quick.status()}''')
            for err in quick.errors():
                logger.error(f'''[WiiMRadio] {err.toString()}''')
        else:
            logger.debug('[WiiMRadio] QML loaded successfully')
        self._main_layout.addWidget(quick)
        self.quickWidget = quick

    
    def _ensure_qml_page(self = None):
        '''
        确保首页 QML 视图已经创建。

        :param: 无。
        :return: None。
        '''
        if self.quickWidget is not None:
            return None
        None._setup_qml_page()

    
    def _release_qml_page(self = None):
        '''
        释放首页 QML 视图，隐藏页面时主动回收 QML 树与纹理资源。

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
        清理首页 QML 上下文属性，避免旧 root object 持有 Python 对象引用。

        :param quick: 待清理的 QQuickWidget。
        :return: None。
        '''
        ctx = quick.rootContext()
        ctx.setContextProperty('wiimRadioHomeState', None)
        ctx.setContextProperty('wiimRadioHomeActions', None)
        ctx.setContextProperty('wiimRadioController', None)
        self._clearSharedQmlContext(ctx)

    __classcell__ = None

