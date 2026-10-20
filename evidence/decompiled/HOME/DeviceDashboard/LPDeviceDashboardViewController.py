# Source Generated with Decompyle++
# File: LPDeviceDashboardViewController.pyc (Python 3.9)

'''
@Time ： 2025/11/17 11:59
@Auth ： Chris
@File ：LPDeviceDashboardViewController.py
@Desc:
'''
from queue import Queue
from PyQt6.QtCore import pyqtSignal, pyqtProperty, pyqtSlot, QCoreApplication, Qt, QUrl, QObject, QTimer
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import LPGlobalUI
from HOME.DeviceDashboard.LPGroupItemWrapper import LPGroupItemWrapper
from HOME.DeviceDashboard.LPDeviceItemWrapper import LPDeviceItemWrapper
from HOME.DeviceDashboard.LPEditGroupDialogViewController import LPEditGroupDialogViewController
from HOME.DeviceDashboard.LPDeviceListModel import LPDeviceListModel
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Sub_Text, StackWidget_Title
from LPClientFramework.LPDeviceManager.LPDeviceNodeManager import LPDeviceNodeManager
from LPClientFramework.LPDeviceManager.LPGroupManager import LPGroupManager
from LPClientFramework.LPUtility import logger, logAcctBifurcate
from LPCommonWidgets.dialog.LPIPDiscoverDeviceDialog import LPIPDiscoverDeviceDialog
from LPCommonWidgets.dialog.LPIPDiscoverDeviceDialog_ui import Ui_Dialog

class LPDeviceDashboardViewController(QWidget):
    selectDeviceSignal = pyqtSignal(object)
    pauseAllCheckedChanged = pyqtSignal()
    pauseAllTextChanged = pyqtSignal()
    displayDeviceCountChanged = pyqtSignal()
    checkPauseAllSignal = pyqtSignal(object)
    
    def __init__(self = None, deviceListGetMethod = None, currentDeviceChanged = None, searchingViewSyncMethod = None, parent = None):
        super().__init__(parent)
        self.selectDeviceSignal.connect(self._onSelectDeviceRequest)
        self.deviceListGetMethod = deviceListGetMethod
        self.currentDeviceChanged = currentDeviceChanged
        self.searchingViewSyncMethod = searchingViewSyncMethod
        self.deviceModel = None
        self.rawDeviceModel = None
        self.groupModel = None
        self.nodeMgr = LPDeviceNodeManager.instance()
        self.lastDevice = LPUtility.settings.value('lastDevice', None)
        self._deviceGridSignalsBound = False
        self.rawDeviceWrapperMap = { }
        self.groupWrappers = []
        self.editGroupDialogViewController = None
        LPGlobalUI.signalBus.DeviceDashboardProjectionChanged.connect(self._onDashboardProjectionChanged)
        self.pauseAllUserClicked = False
        self._pauseAllChecked = False
        self._pauseAllText = QCoreApplication.translate('Device Dashboard', 'Play All')
        self._displayDeviceCount = 0
        self.checkPauseAllSignal.connect(self.checkPauseAll)
        self.dashboardActive = True
        self.pendingDevices = []

    
    def titleFontSize(self):
        return StackWidget_Title

    titleFontSize = pyqtProperty(float, True, **('constant',))(titleFontSize)
    
    def numFontSize(self):
        return Sub_Text

    numFontSize = pyqtProperty(float, True, **('constant',))(numFontSize)
    
    def buttonFontSize(self):
        return Sub_Text

    buttonFontSize = pyqtProperty(float, True, **('constant',))(buttonFontSize)
    
    def sectionTitleFontSize(self):
        return Sub_Text

    sectionTitleFontSize = pyqtProperty(float, True, **('constant',))(sectionTitleFontSize)
    
    def displayDeviceCount(self):
        '''返回仪表盘展示的物理设备总数（含组内从设备）。

        返回:
            int: 物理设备总数，等于各组(主设备 + 在线从设备)与独立设备之和。
        '''
        return self._displayDeviceCount

    displayDeviceCount = pyqtProperty(int, displayDeviceCountChanged, **('notify',))(displayDeviceCount)
    
    def _upsertRawWrapper(self, device):
        raw_uuid = device.uuid
        wrapper = self.rawDeviceWrapperMap.get(raw_uuid)
        existing_device = getattr(wrapper, 'device', None) if wrapper is not None else None
        if wrapper is None or existing_device is not device:
            if wrapper is not None:
                wrapper.dispose()
            wrapper = LPDeviceItemWrapper(device)
            wrapper.selectionKey = f'''device:{raw_uuid}'''
            wrapper.itemType = 'device'
            self.rawDeviceWrapperMap[raw_uuid] = wrapper
        return wrapper

    
    def _scheduleReclassify(self):
        self.addDevices([])

    
    def _canSelectGroupOption(self, currentEditdevice, groupObj):
        if currentEditdevice is None or groupObj is None:
            return False
        currentUuid = None.uuid
        if currentUuid == groupObj.masterDevice.uuid:
            return True
        if not None.slaveList:
            pass
        for item in []:
            if currentUuid == self._memberUuidFromGroupItem(item):
                return True
            return False

    
    def _shouldDisplayDevice(self, device):
        return not getattr(device, 'isWiiMSub', False)

    
    def _setCurrentDevice(self, device):
        if device is None:
            LPGlobalUI.currentDevice = None
            return None
        oldDevice = None.currentDevice
        LPGlobalUI.currentDevice = device
        self.lastDevice = device.uuid
        if oldDevice != device and self.currentDeviceChanged:
            LPUtility.settings.setValue('lastDevice', device.uuid)
            self.currentDeviceChanged(device)

    
    def _ensureCurrentDevice(self):
        wrappers = []
        if self.deviceModel is not None:
            if not getattr(self.deviceModel, 'deviceWrapperList', []):
                pass
            wrappers.extend(list([]))
        if self.groupModel is not None:
            if not getattr(self.groupModel, 'deviceWrapperList', []):
                pass
            wrappers.extend(list([]))
        if not wrappers:
            LPGlobalUI.currentDevice = None
            return None
        current = None.currentDevice
        current_uuid = getattr(current, 'uuid', None) if current else None
        if current_uuid:
            for wrapper in wrappers:
                candidate = getattr(wrapper, 'device', None)
                if getattr(candidate, 'uuid', None) != current_uuid:
                    continue
                if candidate is current:
                    return None
                None._setCurrentDevice(candidate)
                return None
                preferred_uuid = self.lastDevice
                target_wrapper = None
                if preferred_uuid:
                    for w in wrappers:
                        if getattr(getattr(w, 'device', None), 'uuid', None) == preferred_uuid:
                            target_wrapper = w
                        
                        if target_wrapper is None:
                            for w in wrappers:
                                if getattr(w, 'device', None) is not None:
                                    target_wrapper = w
                                
                                if target_wrapper is None:
                                    LPGlobalUI.currentDevice = None
                                    return None
                                None._setCurrentDevice(target_wrapper.device)
                                return None

    
    def _ensureAndSyncSelection(self):
        self._ensureCurrentDevice()
        QTimer.singleShot(0, self._syncQmlSelectionToCurrentDevice)

    _ensureAndSyncSelection = pyqtSlot()(_ensureAndSyncSelection)
    
    def _syncQmlSelectionToCurrentDevice(self):
        quick = getattr(self, 'deviceDashboardQuickWidget', None)
        if quick is None:
            return None
        root = None.rootObject()
        if root is None:
            return None
        device_grid = None.findChild(QObject, 'deviceGridView')
        group_area = root.findChild(QObject, 'groupArea')
        if device_grid is None or group_area is None:
            return None
        current = None.currentDevice
        current_uuid = getattr(current, 'uuid', '') if current is not None else ''
        if not current_uuid:
            group_area.setProperty('currentIndex', -1)
            device_grid.setProperty('currentIndex', -1)
            return None
        group_index = None
        if not self.groupWrappers:
            pass
        for idx, wrapper in enumerate(list([])):
            wrapper_device = getattr(wrapper, 'device', None)
            if wrapper_device is None:
                continue
            if getattr(wrapper_device, 'uuid', '') == current_uuid:
                group_index = idx
            
            if group_index >= 0:
                group_area.setProperty('currentIndex', group_index)
                device_grid.setProperty('currentIndex', -1)
                return None
            device_index = None
        wrappers = list([]) if self.deviceModel is not None else []
        for idx, wrapper in enumerate(wrappers):
            wrapper_device = getattr(wrapper, 'device', None)
            if wrapper_device is None:
                continue
            if getattr(wrapper_device, 'uuid', '') == current_uuid:
                device_index = idx
            
            group_area.setProperty('currentIndex', -1)
            device_grid.setProperty('currentIndex', device_index)
            return None

    
    def _onSelectDeviceRequest(self, device):
        if device is None:
            return None
        if None.currentDevice is None:
            self._setCurrentDevice(device)

    _onSelectDeviceRequest = pyqtSlot(object)(_onSelectDeviceRequest)
    
    def _onDashboardProjectionChanged(self, projection):
        if not projection:
            pass
        projection = { }
        if not projection.get('rawDevices', []):
            pass
        raw_devices = (lambda .0 = None: [ device for device in .0 if self._shouldDisplayDevice(device) ])([])
        if not projection.get('singleDevices', []):
            pass
        single_devices = (lambda .0 = None: [ device for device in .0 if self._shouldDisplayDevice(device) ])([])
        if not projection.get('groupProjections', []):
            pass
        group_projections = list([])
        raw_wrappers = []
        live_raw_ids = set()
        for device in raw_devices:
            wrapper = self._upsertRawWrapper(device)
            if wrapper is None:
                continue
            raw_wrappers.append(wrapper)
            live_raw_ids.add(device.uuid)
        stale_raw_ids = (lambda .0 = None: [ device_id for device_id in .0 if device_id not in live_raw_ids ])(list(self.rawDeviceWrapperMap.keys()))
        for device_id in stale_raw_ids:
            wrapper = self.rawDeviceWrapperMap.pop(device_id, None)
            dispose = getattr(wrapper, 'dispose', None)
            if callable(dispose):
                dispose()
                continue
                single_wrappers = []
                for device in single_devices:
                    wrapper = self._upsertRawWrapper(device)
                    if wrapper is not None:
                        single_wrappers.append(wrapper)
                        continue
                        if not self.groupWrappers:
                            pass
        old_group_wrappers = list([])
        old_group_map = (lambda .0: pass# WARNING: Decompyle incomplete
)(old_group_wrappers)
        next_group_wrappers = []
        for projection_item in group_projections:
            master = getattr(projection_item, 'masterDevice', None)
            if not master is None or self._shouldDisplayDevice(master):
                continue
            master_uuid = master.uuid
            wrapper = old_group_map.pop(master_uuid, None)
            if wrapper is None:
                wrapper = LPGroupItemWrapper(projection_item)
                wrapper.selectionKey = f'''group:{master_uuid}'''
                wrapper.itemType = 'group'
            else:
                wrapper.updateProjection(projection_item)
            next_group_wrappers.append(wrapper)
        for wrapper in old_group_map.values():
            dispose = getattr(wrapper, 'dispose', None)
            if callable(dispose):
                dispose()
                continue
                self.groupWrappers = next_group_wrappers
                if self.rawDeviceModel is not None:
                    self.rawDeviceModel.setItems(raw_wrappers)
        if self.groupModel is not None:
            self.groupModel.setItems(next_group_wrappers)
        if self.deviceModel is not None:
            self.deviceModel.setItems(single_wrappers)
        group_physical_count = sum((lambda .0: for w in .0:
if not getattr(getattr(w, 'node', None), 'onlineSlaveList', []):
pass1 + len([]))(next_group_wrappers))
        display_count = group_physical_count + len(single_wrappers)
        logger.info('[device dashboard] reclassify raw=%s display=%s groups=%s', len(raw_wrappers), display_count, len(next_group_wrappers))
        self._setDisplayDeviceCount(display_count)
        self._syncSearchingView(display_count, 'dashboardProjection')
        self._ensureAndSyncSelection()
        self._refreshPauseAllState()

    _onDashboardProjectionChanged = pyqtSlot(object)(_onDashboardProjectionChanged)
    
    def addDevices(self, devices):
        for device in devices:
            if not self._shouldDisplayDevice(device):
                logger.debug('skip sub device in dashboard: %s' % getattr(device, 'name', ''))
                continue
            self._upsertRawWrapper(device)
            self.checkPauseAllSignal.emit(device)
        self.nodeMgr.updateShowGroups()

    
    def removeAll(self):
        for wrapper in self.groupWrappers:
            dispose = getattr(wrapper, 'dispose', None)
            if callable(dispose):
                dispose()
                continue
                self.groupWrappers = []
                for wrapper in self.rawDeviceWrapperMap.values():
                    dispose = getattr(wrapper, 'dispose', None)
                    if callable(dispose):
                        dispose()
                        continue
                        self.rawDeviceWrapperMap = { }
                        if self.deviceModel:
                            self.deviceModel.clear()
        if self.rawDeviceModel:
            self.rawDeviceModel.clear()
        if self.groupModel:
            self.groupModel.clear()
        LPGlobalUI.currentDevice = None
        self.pauseAllUserClicked = False
        self.pauseAllChecked = False
        self.pauseAllText = QCoreApplication.translate('Device Dashboard', 'Play All')
        self._setDisplayDeviceCount(0)
        self._syncSearchingView(0, 'dashboardRemoveAll')

    
    def _setDisplayDeviceCount(self, count):
        '''更新仪表盘展示的物理设备总数并通知 QML 刷新。

        参数:
            count (int): 物理设备总数（含组内从设备）。
        返回:
            None。
        '''
        if self._displayDeviceCount != count:
            self._displayDeviceCount = count
            self.displayDeviceCountChanged.emit()

    
    def _syncSearchingView(self, displayDeviceCount, reason):
        if callable(self.searchingViewSyncMethod):
            self.searchingViewSyncMethod(displayDeviceCount, reason)

    
    def setupUi(self):
        self.deviceModel = LPDeviceListModel(self, **('parent',))
        self.rawDeviceModel = LPDeviceListModel(self, **('parent',))
        self.groupModel = LPDeviceListModel(self, **('parent',))
        None((lambda : QTimer.singleShot(0, self._ensureAndSyncSelection)))
        self.setupEditGroupDialog()
        self.setupQmlDashboard()
        self.syncExistingDevices()

    
    def syncExistingDevices(self):
        '''Backfill devices discovered before dashboard controller is created.'''
        pass
    # WARNING: Decompyle incomplete

    
    def setupQmlDashboard(self):
        quick = QQuickWidget(self)
        quick.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        quick.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        quick.setClearColor(LPGlobalUI.THEME_BACKGROUND_COLOR_UI)
        quick.setStyleSheet(f'''background-color: {LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name()};''')
        ctx = quick.rootContext()
        ctx.setContextProperty('deviceModel', self.deviceModel)
        ctx.setContextProperty('rawDeviceModel', self.rawDeviceModel)
        ctx.setContextProperty('groupModel', self.groupModel)
        ctx.setContextProperty('controller', self)
        ctx.setContextProperty('groupEditController', self.editGroupDialogViewController)
        ctx.setContextProperty('dashboardBgColor', LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name())
        quick.setSource(QUrl(LPGlobalUI.qmlPath('DeviceDashboard/LPDeviceDashboard.qml')))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''Dashboard QML load failed! status: {quick.status()}''')
            for err in quick.errors():
                logger.error(f'''err.toString(): {err.toString()}''')
        else:
            logger.debug('Dashboard QML loaded successfully!')
        self._bindDeviceGridSignals(quick)
        None((lambda _status = None: self._bindDeviceGridSignals(quick)))
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        if hasattr(self, 'mainFrame'):
            self.mainFrame.setVisible(False)
        layout.addWidget(quick)
        self.deviceDashboardQuickWidget = quick

    
    def setupEditGroupDialog(self):
        if self.editGroupDialogViewController is None:
            self.editGroupDialogViewController = LPEditGroupDialogViewController.createForHostWindow(LPGlobalUI.mainWindow, **('parent',))

    
    def _syncEditGroupDialogGeometry(self):
        if self.editGroupDialogViewController is None:
            return None
        sync_method = None(self.editGroupDialogViewController, '_syncToHostGeometry', None)
        if callable(sync_method):
            sync_method()

    
    def openEditGroupDialog(self, wrapper):
        if self.editGroupDialogViewController is None:
            return None
        None.editGroupDialogViewController.openDialog(wrapper)

    openEditGroupDialog = pyqtSlot('QVariant')(openEditGroupDialog)
    
    def _bindDeviceGridSignals(self, quick):
        if quick.status() != QQuickWidget.Status.Ready:
            return None
        root = None.rootObject()
        if root is None:
            return None
        if not None(self, '_deviceGridSignalsBound', False):
            signal = getattr(root, 'itemSelected', None)
            if signal:
                signal.connect(self.onItemSelected)
            self._deviceGridSignalsBound = True
        self._ensureAndSyncSelection()

    
    def onItemSelected(self, selectionKey, device):
        selectedDevice = device
        if selectedDevice is None and isinstance(selectionKey, str) and selectionKey.startswith('group:'):
            target_uuid = selectionKey.split(':', 1)[1]
            if not self.groupWrappers:
                pass
            for wrapper in []:
                wrapper_device = getattr(wrapper, 'device', None)
                if wrapper_device is None:
                    continue
                if getattr(wrapper_device, 'uuid', '') == target_uuid:
                    selectedDevice = wrapper_device
                
                if selectedDevice is None:
                    return None
                None.debug(f'''[device dashboard] qml selected item={selectionKey} device={selectedDevice.name} uuid={selectedDevice.uuid}''')
                self._setCurrentDevice(selectedDevice)
                return None

    
    def viewWillAppear(self):
        LPUtility.registerDeviceInfoChanged(self)
        self.dashboardActive = True
        if self.pendingDevices:
            self.addDevices(self.pendingDevices)
            self.pendingDevices = []
        self.nodeMgr.updateShowGroups()
        self._ensureAndSyncSelection()
        self._refreshPauseAllState()
        self.refreshVisibleItems()

    
    def viewWillDisappear(self):
        self.dashboardActive = False

    
    def refreshVisibleItems(self):
        if not self.rawDeviceWrapperMap and self.groupWrappers:
            return None
    # WARNING: Decompyle incomplete

    
    def _dashboardControlDevices(self):
        targets = []
        seen = set()
        
        def append_device(dev = None):
            if dev is None:
                return None
            if not None(dev, 'uuid', ''):
                pass
            uuid = ''
            if uuid or uuid in seen:
                return None
            if not None._shouldDisplayDevice(dev):
                return None
            None.add(uuid)
            targets.append(dev)

        if not self.groupWrappers:
            pass
        for wrapper in list([]):
            append_device(getattr(wrapper, 'device', None))
        single_wrappers = list([]) if self.deviceModel is not None else []
        for wrapper in single_wrappers:
            append_device(getattr(wrapper, 'device', None))
        return targets

    
    def _refreshPauseAllState(self):
        if self.pauseAllUserClicked:
            return None
        any_playing = None
        for device in self._dashboardControlDevices():
            if not getattr(getattr(device, 'mediaInfo', None), 'playState', ''):
                pass
            play_state = str('').upper()
            if play_state == 'PLAYING':
                any_playing = True
            
            self.pauseAllChecked = any_playing
        self.pauseAllText = QCoreApplication.translate('Device Dashboard', 'Pause All') if any_playing else QCoreApplication.translate('Device Dashboard', 'Play All')

    
    def deviceList(self):
        deviceList = self.deviceListGetMethod()
        deviceList.sort((lambda d: d.name.lower()), **('key',))
        return deviceList

    deviceList = property(deviceList)
    
    def addMethod(self, device):
        if not self._shouldDisplayDevice(device):
            logger.info('UI device ignore(sub): %s' % getattr(device, 'name', ''))
            return None
        if None.currentDevice is None:
            self.selectDeviceSignal.emit(device)
        self.addDevices([
            device])
        logger.info('UI device add: %s' % device.name)

    
    def rmvMethod(self, device):
        raw_uuid = self._rawUUID(getattr(device, 'uuid', ''))
        self.nodeMgr.removeRawDevice(raw_uuid)
        wrapper = self.rawDeviceWrapperMap.pop(raw_uuid, None)
        if wrapper is not None:
            dispose = getattr(wrapper, 'dispose', None)
            if callable(dispose):
                dispose()
        self.addDevices([])
        logger.info('UI device rmv: %s' % device.name)

    
    def closeEvent(self = None, event = None):
        self._stopRefreshThread = True
        self.deviceQueue.put(None)
    # WARNING: Decompyle incomplete

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        self._syncEditGroupDialogGeometry()

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if infoType == 'media' and detail and set(detail.keys()) == {
            'progress'}:
            return None
        if None == 'media':
            self._refreshPauseAllState()
        if infoType == 'multiroom':
            self.nodeMgr.updateShowGroups()

    
    def onAddDeviceButtonClicked(self):
        dialog = LPGlobalUI.loadUI(LPUIPath.LPIPDiscoverDeviceDialogUI, Ui_Dialog, LPIPDiscoverDeviceDialog, LPGlobalUI.mainWindow)
        dialog.exec()

    onAddDeviceButtonClicked = pyqtSlot()(onAddDeviceButtonClicked)
    
    def onNetworkChanged(self, oldGW, newGW):
        logger.debug('[device dashboard] onNetworkChanged ')

    
    def onPauseAllButtonPressed(self, checked):
        self.pauseAllUserClicked = True
        self.pauseAllChecked = checked
        if checked:
            self.pauseAllText = QCoreApplication.translate('Device Dashboard', 'Pause All')
        else:
            self.pauseAllText = QCoreApplication.translate('Device Dashboard', 'Play All')
        self.playAll(checked)

    onPauseAllButtonPressed = pyqtSlot(bool)(onPauseAllButtonPressed)
    
    def playAll(self, isPlay = (True,)):
        for device in self._dashboardControlDevices():
            if isPlay:
                device.asyncUpnpPost('Play', None)
                continue
            device.asyncUpnpPost('Pause', None)

    
    def checkPauseAll(self, device):
        self._refreshPauseAllState()

    
    def pauseAllChecked(self):
        return self._pauseAllChecked

    pauseAllChecked = pyqtProperty(bool, pauseAllCheckedChanged, **('notify',))(pauseAllChecked)
    
    def pauseAllChecked(self, value):
        if self._pauseAllChecked != value:
            self._pauseAllChecked = value
            self.pauseAllCheckedChanged.emit()

    pauseAllChecked = pauseAllChecked.setter(pauseAllChecked)
    
    def pauseAllText(self):
        return self._pauseAllText

    pauseAllText = pyqtProperty(str, pauseAllTextChanged, **('notify',))(pauseAllText)
    
    def pauseAllText(self, value):
        if self._pauseAllText != value:
            self._pauseAllText = value
            self.pauseAllTextChanged.emit()

    pauseAllText = pauseAllText.setter(pauseAllText)
    __classcell__ = None

