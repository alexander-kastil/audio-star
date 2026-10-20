# Source Generated with Decompyle++
# File: WiiMHome.pyc (Python 3.9)

import getopt
import html
import os
import sys
import threading
import platform
import time
import traceback
import requests_cache
from PyQt6 import uic, QtGui, QtCore, QtWidgets
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QPoint, Qt, pyqtSignal, QEvent, QTranslator, QCoreApplication, QSettings, pyqtSlot, QSize, QTimer, QUrl
from PyQt6.QtGui import QFont, QPainter, QColor, QPixmap, QIcon, QFontInfo
from HOME.DeviceDashboard.LPDeviceDashboardViewController import LPDeviceDashboardViewController
from HOME.HomeShare import LPHomeShareViewController
from HOME.HomeShare.UI.LPHomeShareViewController_ui import Ui_homeShareViewWidget
from HOME.LPDeviceSearchingViewController_ui import Ui_deviceSearchingWidget
from HOME.LPMyMusicViewController import LPMyMusicViewController
from HOME.LPMyMusicViewController_ui import Ui_mymusicViewWidget
from HOME.LPPlayViewController_ui import Ui_playViewWidget
from HOME.LPPresetViewController import LPPresetViewController
from HOME.LPPresetViewController_ui import Ui_presetViewWidget
from HOME.PresetQml.LPPresetQmlViewController import LPPresetQmlViewController
from HOME.LPQueueViewController import LPQueueViewController
from HOME.LPQueueViewController_ui import Ui_queueViewWidget
from HOME.LPWaitingSpinner import LPWaitingSpinner
from HOME.Minibar.LPMiniBarViewController import LPMiniBarViewController
from HOME.Minibar.UI.LPMinibar_ui import Ui_minibarWidget
from HOME.MyMusic.LPMyMusicAlbumsViewController import LPMyMusicAlbumsViewController
from HOME.MyMusic.LPMyMusicAlbumsViewController_ui import Ui_mymusicAlbumsViewWidget
from HOME.MyMusic.LPMyMusicArtistsViewController import LPMyMusicArtistsViewController
from HOME.MyMusic.LPMyMusicArtistsViewController_ui import Ui_mymusicArtistsViewWidget
from HOME.MyMusic.LPMyMusicGenresViewController import LPMyMusicGenresViewController
from HOME.MyMusic.LPMyMusicGenresViewController_ui import Ui_mymusicGenresViewWidget
from HOME.MyMusic.LPMyMusicImportWaitingViewController import LPMyMusicImportWaitingViewController
from HOME.MyMusic.LPMyMusicImportWaitingViewController_ui import Ui_mymusicImportWaitingViewWidget
from HOME.MyMusic.LPMyMusicTracksViewController import LPMyMusicTracksViewController
from HOME.MyMusic.LPMyMusicTracksViewController_ui import Ui_mymusicTracksViewWidget
from HOME.PlayView.LPPlayViewController import LPPlayViewController
from HOME.PlayView.UI.LPPlayViewController_ui import Ui_playviewNormalWidget
from HOME.RecentlyPlayed.LPRecentlyPlayedViewController import LPRecentlyPlayedViewController
from HOME.SideBar.LPSideBarBrowseViewController import LPSideBarBrowseViewController
from HOME.SideBar.LPSideBarCurrentDeviceViewController import LPSideBarCurrentDeviceViewController
from HOME.SideBar.LPSideBarMusicServiceViewController import LPSideBarMusicServiceViewController
from HOME.SideBar.LPSideBarMoreViewController import LPSideBarMoreViewController
from HOME.SideBar.LPSideBarMyLibraryViewController import LPSideBarMyLibraryViewController
from HOME.Menu.LPMenuBarController import LPMenuBarController
from HOME.Menu.LPSearchMoreMenuController import LPSearchMoreMenuController
from HOME.Menu.LPTrayMenuController import LPTrayMenuController
from HOME.StreamService.RadioParadise2.LPRadioParadise2ViewController import LPRadioParadise2ViewController
from HOME.StreamService.RadioParadise2.LPRadioParadise2ViewController_ui import Ui_radioParadiseWidget
from HOME.StreamService.WiiMRadio.LPWiiMRadioHomeViewController import LPWiiMRadioHomeViewController
from LPCommonWidgets.page.LPMSUnsupportedPage import LPMSUnsupportedPage
from LPCommonWidgets.page.UI.LPMSUnsupportedPage_ui import Ui_MSUnsupportedWidget
from HOME.WiiMHome_ui import Ui_MainWindow
from LPClientFramework import LPBeetsWrapper, LPUtility, LPHttpServerManager
from LPClientFramework.LPConfig.LPAppFeatureConfig import isWiiMRadioEnabled
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT, getFontFamily, getStartupApplicationFont
from LPClientFramework.LPConfig.LPUIPath import LPIPDiscoverDeviceDialogUI
from LPClientFramework.LPDeviceDiscoverManager import LPDeviceDiscoverManager
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPEventFilter.LPPlayViewMouseMonitor import LPPlayViewMouseMonitor
from LPClientFramework.LPEventTrack import LPEventsType, logEvent
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPQTSSDPServer import LPQTSSDPServer
from LPClientFramework.LPUpdateCoordinator import LPOTATelemetryTracker, LPUpdateFlowCoordinator
from LPClientFramework.LPUtility import logger
import LPGlobalUI
from LPCommonWidgets.dialog.LPIPDiscoverDeviceDialog_ui import Ui_Dialog
from LPCommonWidgets.dialog.LPIPDiscoverDeviceDialog import LPIPDiscoverDeviceDialog
spinnerSize = 100
app = None
rootUI = None

class CornerGrip(QSizeGrip):
    
    def paintEvent(self, event):
        pass



class SideGrip(QWidget):
    
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == QtCore.Qt.Edge.LeftEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == QtCore.Qt.Edge.TopEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == QtCore.Qt.Edge.RightEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    
    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    
    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    
    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    
    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mousePos = event.pos()

    
    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    
    def mouseReleaseEvent(self, event):
        self.mousePos = None



class LPDeviceSearchingViewController(QWidget):
    '''设备发现搜索页控制器，负责承载旧版 QWidget 与新版 QML 空状态页面。'''
    
    def __init__(self = None):
        super(LPDeviceSearchingViewController, self).__init__()
        self.deviceDiscoveryQuickWidget = None
        self._qmlSearchingSignalsBound = False
        self._qmlSearchingBindingToken = ''
        self._feedbackDialogViewController = None

    
    def setupUi(self = None, ui = None):
        '''
        初始化设备发现页界面。

        :param ui: 由 Qt Designer 或动态 uic 加载得到的当前页面实例。
        :return: None。
        '''
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self._hideLegacySearchingContent()
        self._setupQmlSearchingContent()
        self.titleBar.updateByPlatForm(self)

    
    def windowChangeEvent(self, state):
        '''
        同步主窗口状态变化到自定义标题栏。

        :param state: 当前窗口状态。
        :return: None。
        '''
        self.titleBar.windowStateChangeSignal.emit(state)

    
    def _hideLegacySearchingContent(self):
        '''
        隐藏旧版 QWidget 内容，保留原控件对象给既有主窗口逻辑使用。

        :param: 无。
        :return: None。
        '''
        legacyTitleBar = getattr(self, 'titleBar', None)
        if legacyTitleBar is not None:
            legacyTitleBar.setVisible(False)
        legacyFrame = getattr(self, 'frame', None)
        if legacyFrame is not None:
            legacyFrame.setVisible(False)
        moreButton = getattr(self, 'moreButton', None)
        if moreButton is not None:
            moreButton.setVisible(False)

    
    def _setupQmlSearchingContent(self):
        '''
        创建并加载新版 QML 设备发现空状态页。

        :param: 无。
        :return: None。
        '''
        quick = QQuickWidget(self)
        quick.setObjectName('deviceDiscoveryQuickWidget')
        quick.installEventFilter(self)
        quick.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        quick.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        quick.setClearColor(LPGlobalUI.THEME_BACKGROUND_COLOR_UI)
        quick.setStyleSheet('background-color: %s;' % LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name())
        qmlSource = LPGlobalUI.qmlPath('DeviceDiscovery/LPDeviceDiscoveryEmpty.qml')
        logger.info('[DeviceDiscoveryDebug] create quick widget source=%s parentSize=%sx%s widgetSize=%sx%s', qmlSource, self.width(), self.height(), quick.width(), quick.height())
        quick.setSource(QUrl(qmlSource))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''Device discovery QML load failed! status: {quick.status()}''')
            for err in quick.errors():
                logger.error(f'''Device discovery QML error: {err.toString()}''')
        else:
            self._bindQmlSearchingSignals(quick)
        None((lambda _status = None: self._bindQmlSearchingSignals(quick)))
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        layout.addWidget(quick)
        self.deviceDiscoveryQuickWidget = quick
        None(None, (lambda : self._bindQmlSearchingSignals(quick)))
        logger.info('[DeviceDiscoveryDebug] quick widget added layoutCount=%s quickVisible=%s quickSize=%sx%s', layout.count(), quick.isVisible(), quick.width(), quick.height())

    
    def eventFilter(self = None, watched = None, event = None):
        '''
        记录设备发现 QML 容器收到的鼠标事件，辅助判断点击是否到达 QQuickWidget。

        :param watched: 当前被事件过滤器观察的对象。
        :param event: Qt 投递给被观察对象的事件。
        :return: bool，True 表示事件已被消费；False 表示继续交给默认流程处理。
        '''
        mouseEventTypes = {
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseButtonDblClick}
        if watched.objectName() == 'deviceDiscoveryQuickWidget' and event.type() in mouseEventTypes:
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            root = watched.rootObject() if hasattr(watched, 'rootObject') else None
            rootSizeText = 'None'
            if root is not None:
                rootSizeText = '%sx%s' % (root.property('width'), root.property('height'))
            mainWindow = LPGlobalUI.mainWindow
            loadingBackground = getattr(mainWindow, 'loadingBackground', None) if mainWindow is not None else None
            loadingButton = getattr(mainWindow, 'loadingButton', None) if mainWindow is not None else None
            logger.info('[DeviceDiscoveryDebug] quick mouse event type=%s pos=(%s,%s) quickSize=%sx%s rootSize=%s bindingToken=%s searchingVisible=%s loadingBackgroundVisible=%s loadingButtonVisible=%s', event.type().name, pos.x(), pos.y(), watched.width(), watched.height(), rootSizeText, root.property('debugBindingToken') if root is not None else None, self.isVisible(), loadingBackground.isVisible() if loadingBackground is not None else None, loadingButton.isVisible() if loadingButton is not None else None)
        return super().eventFilter(watched, event)

    
    def _buildQmlSearchingNetworkState(self):
        '''
        生成设备发现空状态页需要展示的当前网络信息。

        :param: 无。
        :return: dict，包含背景色、网络状态文案、说明文案和本机 IP 地址。
        '''
        networkInfo = LPUtility.fetchNetworkInfo()
        networkType = LPUtility.fetchNetworkType()
        ipAddress = 'N/A'
        networkStatusText = 'N/A'
        if networkInfo is not None:
            if not networkInfo.get('localIP', ''):
                pass
            ipAddress = 'N/A'
        if networkType == 'eth':
            networkStatusText = QCoreApplication.translate('MainWindow', 'Ethernet')
            networkDescriptionText = QCoreApplication.translate('MainWindow', 'Your computer is connected via <b>%1</b>.<br>Make sure your device is connected to the same local network.').replace('%1', html.escape(networkStatusText))
        elif networkType == 'wifi':
            if not LPUtility.currentSSID():
                pass
            ssid = QCoreApplication.translate('MainWindow', 'Wi-Fi')
            networkStatusText = ssid
            networkDescriptionText = QCoreApplication.translate('MainWindow', 'Your computer is connected to <b>%1</b>.<br>Make sure your device is connected to the same Wi-Fi network.').replace('%1', html.escape(networkStatusText))
        else:
            networkDescriptionText = QCoreApplication.translate('MainWindow', 'No network info found.<br>Make sure your computer and device are on the same local network.')
        if not QApplication.applicationVersion() and LPUtility.appVersion:
            pass
        appVersionValue = str('').strip()
        return {
            'backgroundColor': LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name(),
            'isMacOS': platform.system() == 'Darwin',
            'themeFontFamily': getFontFamily(),
            'networkStatusText': networkStatusText,
            'networkDescriptionText': networkDescriptionText,
            'ipAddress': ipAddress,
            'appVersionText': appVersionValue }

    
    def _applyQmlSearchingProperties(self, root):
        '''
        将 Python 侧获取到的主题和网络信息注入到 QML 根对象。

        :param root: 设备发现 QML 的根对象。
        :return: None。
        '''
        if root is None:
            return None
        qmlState = None._buildQmlSearchingNetworkState()
        for propertyName, propertyValue in qmlState.items():
            root.setProperty(propertyName, propertyValue)

    
    def _bindQmlSearchingSignals(self, quick):
        '''
        绑定 QML 页面发出的反馈和 IP 连接信号。

        :param quick: 承载设备发现 QML 的 QQuickWidget。
        :return: None。
        '''
        if quick.status() != QQuickWidget.Status.Ready:
            logger.info('[DeviceDiscoveryDebug] skip bind because quick status=%s', quick.status())
            return None
        root = None.rootObject()
        if root is None:
            logger.warning('[DeviceDiscoveryDebug] skip bind because QML root is None')
            return None
        None._applyQmlSearchingProperties(root)
        currentBindingToken = root.property('debugBindingToken')
        logger.info('[DeviceDiscoveryDebug] bind check quickSize=%sx%s rootSize=%sx%s rootObject=%s alreadyBound=%s currentBindingToken=%s', quick.width(), quick.height(), root.property('width'), root.property('height'), root.objectName(), self._qmlSearchingSignalsBound, currentBindingToken)
        if isinstance(currentBindingToken, str) and currentBindingToken.startswith('bound:'):
            logger.info('[DeviceDiscoveryDebug] skip bind because current root already has token=%s', currentBindingToken)
            return None
        bindingToken = None % (id(root), time.monotonic())
        if not root.setProperty('debugBindingToken', bindingToken):
            logger.warning('[DeviceDiscoveryDebug] failed to set debugBindingToken on QML root')
        connectByIpSignal = getattr(root, 'connectByIpRequested', None)
        if connectByIpSignal is not None:
            connectByIpSignal.connect(self._openIPDiscoverDialogFromQml)
            logger.info('[DeviceDiscoveryDebug] connected connectByIpRequested token=%s', bindingToken)
        else:
            logger.warning('[DeviceDiscoveryDebug] missing connectByIpRequested signal')
        sendFeedbackSignal = getattr(root, 'sendFeedbackRequested', None)
        if sendFeedbackSignal is not None:
            sendFeedbackSignal.connect(self._openFeedbackDialogFromQml)
            logger.info('[DeviceDiscoveryDebug] connected sendFeedbackRequested token=%s', bindingToken)
        else:
            logger.warning('[DeviceDiscoveryDebug] missing sendFeedbackRequested signal')
        closeWindowSignal = getattr(root, 'closeWindowRequested', None)
        if closeWindowSignal is not None:
            closeWindowSignal.connect(self._closeWindowFromQml)
        minimizeWindowSignal = getattr(root, 'minimizeWindowRequested', None)
        if minimizeWindowSignal is not None:
            minimizeWindowSignal.connect(self._minimizeWindowFromQml)
        maximizeWindowSignal = getattr(root, 'maximizeWindowRequested', None)
        if maximizeWindowSignal is not None:
            maximizeWindowSignal.connect(self._maximizeWindowFromQml)
        fullscreenWindowSignal = getattr(root, 'fullscreenRequested', None)
        if fullscreenWindowSignal is not None:
            fullscreenWindowSignal.connect(self._fullscreenFromQml)
        startWindowMoveSignal = getattr(root, 'startWindowMoveRequested', None)
        if startWindowMoveSignal is not None:
            startWindowMoveSignal.connect(self._startWindowMoveFromQml)
        self._qmlSearchingSignalsBound = True
        self._qmlSearchingBindingToken = bindingToken

    
    def _closeWindowFromQml(self):
        '''
        响应 QML 标题栏关闭按钮，复用主窗口关闭策略。

        :param: 无。
        :return: None。
        '''
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is None:
            return None
        if None(mainWindow, 'enableMemoryResident', False):
            mainWindow.hide()
        elif hasattr(mainWindow, 'quitApp'):
            mainWindow.quitApp()
        else:
            mainWindow.close()

    _closeWindowFromQml = pyqtSlot()(_closeWindowFromQml)
    
    def _minimizeWindowFromQml(self):
        '''
        响应 QML 标题栏最小化按钮。

        :param: 无。
        :return: None。
        '''
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is not None:
            mainWindow.showMinimized()

    _minimizeWindowFromQml = pyqtSlot()(_minimizeWindowFromQml)
    
    def _maximizeWindowFromQml(self):
        '''
        响应 QML 标题栏最大化按钮，双击标题栏或点击最大化按钮时触发。
        在所有平台（macOS / Windows / Linux）上统一切换最大化/还原，
        与 LPTitleBar.mouseDoubleClickEvent 行为保持一致。

        :param: 无。
        :return: None。
        '''
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is None:
            return None
        if None.windowState() & QtCore.Qt.WindowState.WindowMaximized:
            mainWindow.showNormal()
        else:
            mainWindow.showMaximized()

    _maximizeWindowFromQml = pyqtSlot()(_maximizeWindowFromQml)
    
    def _fullscreenFromQml(self):
        '''
        响应 QML 标题栏全屏按钮（macOS 绿色按钮），进入或退出全屏模式。

        :param: 无。
        :return: None。
        '''
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is None:
            return None
        if None.isFullScreen():
            mainWindow.showNormal()
        else:
            mainWindow.showFullScreen()

    _fullscreenFromQml = pyqtSlot()(_fullscreenFromQml)
    
    def _startWindowMoveFromQml(self):
        '''
        响应 QML 标题栏拖动，启动系统窗口移动。

        :param: 无。
        :return: None。
        '''
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is None or mainWindow.isFullScreen():
            return None
        windowHandle = None.windowHandle()
        if windowHandle is not None:
            windowHandle.startSystemMove()

    _startWindowMoveFromQml = pyqtSlot()(_startWindowMoveFromQml)
    
    def _openIPDiscoverDialogFromQml(self):
        '''
        响应 QML 的手动 IP 连接入口，打开原有 IP 发现弹窗。

        :param: 无。
        :return: None。
        '''
        logger.info('[DeviceDiscoveryDebug] Python slot reached: _openIPDiscoverDialogFromQml')
        mainWindow = LPGlobalUI.mainWindow
        if mainWindow is not None and hasattr(mainWindow, '_openIPDiscoverDialog'):
            mainWindow._openIPDiscoverDialog()

    _openIPDiscoverDialogFromQml = pyqtSlot()(_openIPDiscoverDialogFromQml)
    
    def _openLogDirFromQml(self):
        '''
        响应 QML 的反馈入口，复用现有打开日志目录逻辑（兜底保留）。

        :param: 无。
        :return: None。
        '''
        logger.info('[DeviceDiscoveryDebug] Python slot reached: _openLogDirFromQml')
        LPUtility.openFileInSystem(LPUtility.logDir)

    _openLogDirFromQml = pyqtSlot()(_openLogDirFromQml)
    
    def _openFeedbackDialogFromQml(self):
        '''
        响应 QML 的反馈入口，打开用户反馈弹窗。

        懒加载 LPFeedbackDialogViewController 并挂在主窗口上，
        避免设备发现页销毁导致弹窗丢失。

        :param: 无。
        :return: None。
        '''
        logger.info('[Feedback] Python slot reached: _openFeedbackDialogFromQml')
    # WARNING: Decompyle incomplete

    _openFeedbackDialogFromQml = pyqtSlot()(_openFeedbackDialogFromQml)
    __classcell__ = None


class LPStreamServiceMainWindow(QMainWindow):
    '''主应用窗口控制器。

    负责无边框窗口（macOS 通过 updateWindowMask 实现四角圆角裁剪）、
    自定义 grips 调整、播放视图/搜索视图叠加、托盘/最小化恢复、
    以及 macOS 特有的 Sparkle 更新与菜单桥接。
    '''
    _gripSize = 8
    deviceInfoUpdateSignal = pyqtSignal(object, object, object)
    showSearchingViewSignal = pyqtSignal(object)
    showGlobalLoadingSignal = pyqtSignal(object)
    libraryTaskUpdateSignal = pyqtSignal(object)
    deferredBeetsInitFinishedSignal = pyqtSignal(bool, str)
    winSparkleShutdownRequestSignal = pyqtSignal()
    updateFoundSignal = pyqtSignal(object)
    noUpdateFoundSignal = pyqtSignal(object)
    _SEARCHING_NETWORK_REFRESH_INTERVAL_MS = 1500
    _SEARCHING_NETWORK_REFRESH_MAX_ATTEMPTS = 6
    
    def __init__(self = None, parent = None):
        super(LPStreamServiceMainWindow, self).__init__(parent, **('parent',))
        LPGlobalUI.deviceManager = LPDeviceDiscoverManager(self.deviceAddMethod, self.deviceRmvMethod, self.mediaServerAddMethod, self.mediaServerRmvMethod, self.rmvAllMethod)
        LPGlobalUI.signalBus.Network_Changed_Signal.connect(self.networkChanged)
        self.miniBarViewController = None
        self.deviceDashboardViewController = None
        self.recentlyViewController = None
        self.presetQmlViewController = None
        self.sideLibListViewController = None
        self.sideBrowseViewController = None
        self.sideMoreViewController = None
        self.sideMusicServiceListViewController = None
        self.wiimRadioHomeViewController = None
        self.contentViewDict = { }
        self.lastSidebarItem = 'device_dashboard'
        self.trayMenuController = LPTrayMenuController(self, self.showApp, self.quitApp)
        self.menuBarController = None(None, (lambda : self.updateFlowCoordinator.isMacReady()), self._checkForUpdatesAction, self._openFeedbackDialogFromSideBar)
        self.searchMoreMenuController = None
        self.playViewController = None
        self.isPlayViewShow = False
        self.otaTelemetryTracker = LPOTATelemetryTracker()
        self.updateFlowCoordinator = LPUpdateFlowCoordinator(self.otaTelemetryTracker)
        self._isQuitting = False
        self._winUpdateShutdownRequested = False
        self.winSparkleShutdownRequestSignal.connect(self._handleWinSparkleShutdownRequestOnMainThread, Qt.ConnectionType.QueuedConnection)
        self.updateFlowCoordinator.setWinShutdownHooks(self._canShutdownForWinUpdate, self._onWinSparkleShutdownRequest)
        self.sparkleTimer = None
        self._SPARKLE_FIXED_INTERVAL_MS = 7200000
        self._OTA_TIMEOUT_MONITOR_INTERVAL_MS = 30000
        self._otaTimeoutMonitorTimer = None
        self._hasUpdateAvailable = False
        self.updateFoundSignal.connect(self._onUpdateFoundOnMainThread, Qt.ConnectionType.QueuedConnection)
        self.noUpdateFoundSignal.connect(self._onNoUpdateFoundOnMainThread, Qt.ConnectionType.QueuedConnection)
        self.searchingViewController = None
        self.isSearchingViewShow = False
        self._dashboardDisplayDeviceCount = None
        self._searchingNetworkRefreshAttempts = 0
        self._searchingNetworkRefreshLastState = None
        self._searchingNetworkRefreshTimer = QTimer(self)
        self._searchingNetworkRefreshTimer.setSingleShot(True)
        self._searchingNetworkRefreshTimer.setInterval(self._SEARCHING_NETWORK_REFRESH_INTERVAL_MS)
        self._searchingNetworkRefreshTimer.timeout.connect(self._retrySearchingNetworkRefresh)
        self.importWaitingWidget = None
        self._cachedImportWaitingState = None
        self._libraryTaskStateByKind = { }
        self.loadingBackground = None
        self.loadingButton = None
        self.loadingSpinner = None
        LPBeetsWrapper.initBeets()
        LPUtility.imageCache.setCacheLimit(1024000)
        LPUtility.registerDeviceInfoChanged(self)
        QtCore.QThreadPool.globalInstance().setMaxThreadCount(2)
        self.deviceInfoUpdateSignal.connect(self._deviceInfoUpdateSlot)
        self.showSearchingViewSignal.connect(self._showSearchingViewSlot)
        self.showGlobalLoadingSignal.connect(self.showGlobalLoadingSlot)
        self.libraryTaskUpdateSignal.connect(self._applyLibraryTaskUIUpdate, Qt.ConnectionType.QueuedConnection)
        LPUtility.addNotificationObserver(LPBeetsWrapper.LIBRARY_TASK_UI_NOTIFICATION_NAME, self._handleLibraryTaskUINotification)
        self._last_window_state = self.windowState()
        self.maximized_before_fullscreen = False
        self.enableMemoryResident = LPUtility.settings.value('memoryResident', True, bool, **('type',))
        self.hideSidebarScrollBarTimer = QTimer(self)
        self.hideSidebarScrollBarTimer.setSingleShot(True)
        self.hideSidebarScrollBarTimer.setInterval(1000)
        self._sideBarScrolling = False
        self._last_mask_size = None
        self._displayWindowHandle = None
        self._displayMoveSettledTimer = QTimer(self)
        self._displayMoveSettledTimer.setSingleShot(True)
        self._displayMoveSettledTimer.setInterval(350)
        self._displayMoveSettledTimer.timeout.connect(self._handleSettledDisplayMove)
        self._displayLastStableLogicalSize = QSize()
        self._displayScreenReconcileInProgress = False
        self._displayImmediateReconcileScheduled = False
        self._displayQuickScreenSyncTimer = QTimer(self)
        self._displayQuickScreenSyncTimer.setInterval(1000)
        self._displayQuickScreenSyncTimer.timeout.connect(self._syncQuickWidgetScreensToHost)

    
    def _displayScreenWithLargestIntersection(self, windowGeometry = (None,)):
