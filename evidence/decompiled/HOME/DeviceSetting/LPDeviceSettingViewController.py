# Source Generated with Decompyle++
# File: LPDeviceSettingViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QColor
import LPGlobalUI
from HOME.DeviceSetting.LPDeviceSettingDeviceViewController import LPDeviceSettingDeviceViewController
from HOME.DeviceSetting.LPDeviceSettingDeviceViewController_ui import Ui_deviceSettingDeviceViewWidget
from HOME.DeviceSetting.LPDeviceSettingHardwareViewController import LPDeviceSettingHardwareViewController
from HOME.DeviceSetting.LPDeviceSettingHardwareViewController_ui import Ui_deviceSettingHardwareViewWidget
from HOME.DeviceSetting.LPDeviceSettingSoundViewController import LPDeviceSettingSoundViewController
from HOME.DeviceSetting.LPDeviceSettingSoundViewController_ui import Ui_deviceSettingSoundViewWidget
from HOME.DeviceSetting.LPDeviceSettingVoiceViewController import LPDeviceSettingVoiceViewController
from HOME.DeviceSetting.LPDeviceSettingVoiceViewController_ui import Ui_deviceSettingVoiceViewWidget
from HOME.LPWaitingSpinner import LPWaitingSpinner
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title

class LPDeviceSettingViewController(QWidget):
    updateCurrentSelectSignal = pyqtSignal(object)
    showLoadingButtonSignal = pyqtSignal(object)
    
    def __init__(self = None, device = None):
        super(LPDeviceSettingViewController, self).__init__()
        self.deviceId = device.uuid
        self.topLevelItemId = 'devicesetting_device'
        self.loadingSpinner = None
        self.deviceViewController = None
        self.lastSelectIndex = 0

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        device = LPGlobalUI.deviceManager.deviceForUUID(self.deviceId)
        if device is None:
            return None
        None.titleLabel.setText(device.name)
        self.deviceViewController = LPGlobalUI.loadUI(LPUIPath.DeviceSettingDeviceViewControllerUI, Ui_deviceSettingDeviceViewWidget, LPDeviceSettingDeviceViewController, self.deviceId, self.showLoadingButtonSignal, self.renameCallback)
        self.topLevelStackedWidget.addWidget(self.deviceViewController)
        self.dataArray = [
            {
                'id': 'devicesetting_device',
                'title': QCoreApplication.translate('DeviceSetting', 'Device'),
                'method': self.deviceViewController.requestData }]
        if device.deviceSetting.configDict:
            soundViewController = LPGlobalUI.loadUI(LPUIPath.DeviceSettingSoundViewControllerUI, Ui_deviceSettingSoundViewWidget, LPDeviceSettingSoundViewController, self.deviceId, self.showLoadingButtonSignal)
            self.topLevelStackedWidget.addWidget(soundViewController)
            voiceViewController = LPGlobalUI.loadUI(LPUIPath.DeviceSettingVoiceViewControllerUI, Ui_deviceSettingVoiceViewWidget, LPDeviceSettingVoiceViewController, self.deviceId, self.showLoadingButtonSignal)
            self.topLevelStackedWidget.addWidget(voiceViewController)
            hardwareViewController = LPGlobalUI.loadUI(LPUIPath.DeviceSettingHardwareViewControllerUI, Ui_deviceSettingHardwareViewWidget, LPDeviceSettingHardwareViewController, self.deviceId, self.showLoadingButtonSignal)
            self.topLevelStackedWidget.addWidget(hardwareViewController)
            self.dataArray.extend([
                {
                    'id': 'devicesetting_sound',
                    'title': QCoreApplication.translate('DeviceSetting', 'Sound'),
                    'method': soundViewController.requestData },
                {
                    'id': 'devicesetting_voice',
                    'title': QCoreApplication.translate('DeviceSetting', 'Voice'),
                    'method': voiceViewController.requestData },
                {
                    'id': 'devicesetting_hardware',
                    'title': QCoreApplication.translate('DeviceSetting', 'Hardware'),
                    'method': hardwareViewController.requestData }])
        self.updateCurrentSelectSignal.connect(self.updateCurrentSelect)
        self.showLoadingButtonSignal.connect(self._showLoadingButton)
        self._setupTopLevelTable()
        self.updateCurrentSelectSignal.emit(self.dataArray[0]['id'])
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))

    
    def viewWillAppear(self):
        pass

    
    def viewWillDisappear(self):
        pass

    
    def _setupTopLevelTable(self):
        rowCount = len(self.dataArray)
        self.topLevelTableWidget.setRowCount(rowCount)
        for i in range(rowCount):
            data = QTableWidgetItem(self.dataArray[i]['title'])
            self.topLevelTableWidget.setItem(i, 0, data)
        self.topLevelTableWidget.resizeRowsToContents()
        self.topLevelTableWidget.setStyleSheet('\n            QTableWidget::item {color: rgb(108,108,108)}\nQTableWidget::item:selected{\nselection-color: white;\nbackground-color: transparent;\n}\nQTableWidget{selection-background-color: transparent; border: none;}\nQTableWidget::item:hover{background: transparent; color: white}\nQScrollBar {\n        border: 0px;\n        background: transparent;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle {\n        background: rgb(82,82,82);\n        min-height: 0px;\n\tborder-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        border: 0px;\n}\nQHeaderView::section {\nbackground-color: transparent;\ncolor: white;\n}\n')
        self.topLevelTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.topLevelTableWidget.verticalScrollBar().setSingleStep(1)
        self.topLevelTableWidget.itemClicked.connect(self.itemSelect)
        self.topLevelTableWidget.selectionModel().selectionChanged.connect(self.topTableWidgetSelectChanged)

    
    def topTableWidgetSelectChanged(self, selected, deselected):
        pass
    # WARNING: Decompyle incomplete

    
    def updateCurrentSelect(self, itemId):
        for index, itemDict in enumerate(self.dataArray):
            if itemDict['id'] == itemId:
                self.topLevelTableWidget.selectRow(index)
                self.topLevelStackedWidget.setCurrentIndex(index)
                method = itemDict['method']
                method()
                return None
            self.topLevelTableWidget.clearSelection()
            return None

    
    def itemSelect(self, item):
        selectedIndex = item.row()
        self.lastSelectIndex = selectedIndex
        dataDict = self.dataArray[selectedIndex]
        itemId = dataDict['id']
        self.topLevelItemId = itemId
        self.updateCurrentSelectSignal.emit(itemId)

    
    def mousePressEvent(self = None, event = None):
        super().mousePressEvent(event)
        self.deviceViewController.mousePressEvent(event)

    
    def _showLoadingButton(self, show):
        if show:
            self.loadingButton.show()
            if self.loadingSpinner is None:
                self.loadingSpinner = LPWaitingSpinner(self.loadingButton, 30, 40, 6, 50, 3, 1, 1.5, QColor(255, 255, 255), **('roundness', 'fade', 'radius', 'lines', 'line_length', 'line_width', 'speed', 'color'))
            if not self.loadingSpinner.is_spinning:
                self.loadingSpinner.show()
                self.loadingSpinner.start()
            else:
                self.loadingButton.hide()
                if self.loadingSpinner and self.loadingSpinner.is_spinning:
                    self.loadingSpinner.stop()

    
    def renameCallback(self, newName):
        self.titleLabel.setText(newName)

    __classcell__ = None

