# Source Generated with Decompyle++
# File: LPSideBarCurrentDeviceViewController.pyc (Python 3.9)

'''
@Time ： 2025/11/18 10:15
@Auth ： Chris
@File ：LPSideBarCurrentDeviceViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication
import LPGlobalUI
from HOME.DeviceDashboard.LPDeviceDashboardViewController import LPDeviceDashboardViewController
from HOME.SideBar.LPSideBarListView import LPSideBarListModel, LPSideBarListDelegate
from LPClientFramework.LPConfig.LPFontConfig import Sub_Text, Min_Text
from LPClientFramework.LPDeviceManager.LPGroupManager import LPGroupManager

class LPSideBarCurrentDeviceViewController(QObject):
    updateUISignal = pyqtSignal()
    updateCurrentSelectSignal = pyqtSignal(object)
    
    def __init__(self = None, mainUI = None, displaySelectMethod = None):
        super().__init__()
        self.groupMgr = LPGroupManager.instance()
        self.deviceButton = mainUI.currentDeviceButton
        self.currentDeviceWidget = mainUI.currentDeviceFrame
        sideBarLayout = mainUI.verticalLayout_10
        currentMargins = sideBarLayout.contentsMargins()
        sideBarLayout.setContentsMargins(currentMargins.left(), 12, currentMargins.right(), currentMargins.bottom())
        self.currentDeviceWidget.setMinimumHeight(36)
        self.currentDeviceWidget.setMaximumHeight(36)
        self.deviceButton.setMinimumHeight(36)
        self.deviceButton.setMaximumHeight(36)
        self.currentDeviceFrame = mainUI.sideBarMainFrame
        stylesheetTemplate = Template('\n                QFrame {\n                    background: transparent;\n                    border:none;\n                }\n                QPushButton#currentDeviceButton {\n                    color: rgb(255, 255, 255);\n                    text-align: left;\n                    font-size: ${deviceButtonFontSize}pt;\n                    font-weight: bold;\n                }\n                ')
        self.currentDeviceFrame.setStyleSheet(stylesheetTemplate.substitute(f'''{Sub_Text}''', **('deviceButtonFontSize',)))
        self.deviceTitleLabel = mainUI.deviceTitleLabel
        self.deviceTitleLabel.setText(QCoreApplication.translate('SiderBar', 'Devices'))
        self.displaySelectMethod = displaySelectMethod
        self.dataArray = [
            {
                'id': 'device_dashboard',
                'icon': 'sidebar/devices.png',
                'title': QCoreApplication.translate('SideBarBrowse', 'Devices') }]
        self.displayList = mainUI.deviceListView
        model = LPSideBarListModel(self.dataArray, self.displayList)
        delegate = LPSideBarListDelegate(self.displayList)
        self.displayList.setModel(model)
        self.displayList.setItemDelegate(delegate)
        self.displayList.clicked.connect(self.itemSelect)
        self.deviceSectionFrame = mainUI.deviceSectionFrame
        stylesheetTemplate = Template('\n                QFrame {\n                    background: transparent;\n                    border:none;\n                }\n                QLabel#deviceTitleLabel {\n                    color: ${titleColor};\n                    font-size: ${deviceTitleLabelFontSize}pt;\n                }\n                ')
        self.deviceSectionFrame.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.QSS_THEME_LIGHT_COLOR_UI, f'''{Min_Text}''', **('titleColor', 'deviceTitleLabelFontSize')))
        self.displayList.setMaximumHeight(45 * len(self.dataArray))
        self.updateCurrentSelectSignal.connect(self.updateCurrentSelect)

    
    def updateCurrentSelect(self, itemId):
        for row, itemDict in enumerate(self.dataArray):
            if itemDict['id'] == itemId:
                model = self.displayList.model()
                index = model.index(row, 0)
                self.displayList.setCurrentIndex(index)
                return None
            self.displayList.clearSelection()
            return None

    
    def itemSelect(self, index):
        selectedIndex = index.row()
        dataDict = self.dataArray[selectedIndex]
        if self.displaySelectMethod:
            self.displaySelectMethod(dataDict['id'])

    
    def update(self, device):
        self.updateUISignal.emit()

    
    def updateUI(self, device, infoType, detail):
        if device is None or LPGlobalUI.currentDevice is None:
            return None
        if None.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if not infoType:
            pass
        infoTypeLower = None('').lower()
        detailDict = detail if isinstance(detail, dict) else { }
        if infoTypeLower == 'media':
            if detailDict.get('deviceName', None):
                self.changeShowName(device)
            return None
        if None in ('device', 'multiroom'):
            self.changeShowName(device)

    
    def deviceChanged(self, device):
        if device:
            self.changeShowName(device)

    
    def changeShowName(self, device):
        if device is None:
            self.deviceButton.setText('')
            return None
        if not None(device, 'name', ''):
            pass
        showName = ''
        activeGroup = self.groupMgr.getActiveGroupWithDevice(device)
        activeGroupFullName = ''.strip() if activeGroup is not None else ''
        activeGroupName = ''.strip() if activeGroup is not None else ''
        if (activeGroupFullName or activeGroupName) and len(device.groupInfo.slaveList) > 0:
            if not activeGroupFullName:
                pass
            showName = activeGroupName
        self.deviceButton.setText(showName)

    
    def onDeviceButtonClicked(self):
        topWidget = LPGlobalUI.getTopWidget()
        if isinstance(topWidget, LPDeviceDashboardViewController):
            return None
        deviceDashboardViewController = None.mainWindow.deviceDashboardViewController
        if deviceDashboardViewController:
            LPGlobalUI.navigationManager.push(deviceDashboardViewController, 'device_dashboard')

    __classcell__ = None

