# Source Generated with Decompyle++
# File: LPIPDiscoverDeviceDialog.pyc (Python 3.9)

'''
@Time ： 2025/1/6 16:43
@Auth ： Chris
@File ：LPIPDiscoverDeviceDialog.py
@Desc:
'''
import ipaddress
import json
import threading
from enum import Enum
from string import Template
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, pyqtSlot, QSize, QTimer, QEvent, QPoint
from PyQt6.QtGui import QPainterPath, QRegion, QCursor, QColor, QIcon, QPainter
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QSizePolicy, QWidget, QFrame
import LPGlobalUI
from LPClientFramework import LPUtility, UPnPTool
from LPClientFramework.LPConfig.LPUIPath import IconToastUI, ToolTipUI
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.tip.LPToolTip import LPToolTip
from LPCommonWidgets.tip.ToolTip_ui import Ui_toolTip
from LPCommonWidgets.toast.LPIconToast import IconToast
from LPCommonWidgets.toast.LPIconToast_ui import Ui_IconToast

class ConnectStatus(Enum):
    DEFAULT = 'Connect'
    CONNECTING = 'Connecting'
    CONNECTED = 'Connected'
    FAILED = 'Connected Failed'


class LPIPDiscoverDeviceDialog(QDialog):
    discoverSignal = pyqtSignal(str)
    discoverSuccessSignal = pyqtSignal()
    discoverFailSignal = pyqtSignal()
    connectStatusChangeSignal = pyqtSignal(object)
    showIPWarningToastSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.discoverSuccessSignal.connect(self.discoverSuccess)
        self.discoverFailSignal.connect(self.discoverFail)
        self.discoverSignal.connect(self.attemptDiscover)
        self.connectStatusChangeSignal.connect(self.updateConnectButton)
        self.closeTimer = QTimer(self)
        self.closeTimer.setSingleShot(True)
        self.closeTimer.timeout.connect(self.accept)
        self.showIPWarningToastSignal.connect(self.showIPWarningToast)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qssTemplate = Template('\n                QFrame{\n                    border:none;\n                    background-color: transparent;\n                }\n                QFrame#mainFrame{\n                    border-radius: 20px;\n                    background-color: $dialogBg;\n                }\n                QLabel {\n                    color: $fontColor;\n                    background-color: transparent;\n                }\n                QPushButton#closeButton {\n                    background-color: transparent;\n                }\n                \n                QPushButton#connectButton {\n                    background-color: $buttonBg;\n                    color: $fontColor;\n                    border: 0;\n                    border-radius: 17px;\n                    font-weight: bold;\n                }\n                QPushButton#connectButton:pressed{\n                    background-color: $buttonPressBg;\n                }\n                QPushButton#tipButton {\n                    background-color: transparent;\n                    color: $fontColor;\n                    text-decoration: none;\n                }\n                QPushButton#tipButton:hover {\n                    text-decoration: underline;\n                }\n                QLineEdit {\n                    border: 0;\n                    border-radius: 8px;\n                    padding-left: 16px;\n                }\n                ')
        self.setStyleSheet(qssTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, **('fontColor', 'dialogBg', 'buttonBg', 'buttonPressBg')))
        failedTipLabelText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'Unable to connect to the device. Please verify that the IP address is correct and that the device is powered on and connected to the network.')
        self.failedTipLabel.setText(failedTipLabelText)
        self.hideFailedTip(True)
        self.closeButton.setIcon(QIcon(LPGlobalUI.imagePath('dialog_close.png')))
        self.closeButton.clicked.connect(self.reject)
        labelText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'Enter the IP address of your WiiM device to establish a connection.')
        self.label.setText(labelText)
        placeholderText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'e.g., 192.168.1.100')
        self.IPLineEdit.setPlaceholderText(placeholderText)
        self.IPLineEdit.installEventFilter(self)
        tipButtonText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'Find My Device’s IP')
        self.tipButton.setText(tipButtonText)
        loadingIcon = LPGlobalUI.imagePath('btn_loading.png')
        failedIcon = LPGlobalUI.imagePath('btn_failed.png')
        successIcon = LPGlobalUI.imagePath('btn_success.png')
        idleText = QCoreApplication.translate('IPDiscoverDeviceDialog', ConnectStatus.DEFAULT.value)
        loadingText = QCoreApplication.translate('IPDiscoverDeviceDialog', ConnectStatus.CONNECTING.value)
        failedText = QCoreApplication.translate('IPDiscoverDeviceDialog', ConnectStatus.FAILED.value)
        successText = QCoreApplication.translate('IPDiscoverDeviceDialog', ConnectStatus.CONNECTED.value)
        self.connectButton.setup(loadingIcon, failedIcon, successIcon, idleText, loadingText, failedText, successText)
        self.connectButton.setIdle()
        self.connectButton.clicked.connect(self._preDiscover)
        learnMoreUrl = 'https://faq.wiimhome.com/en/support/solutions/articles/72000531116-advanced-troubleshooting-to-find-your-device'
        textTemplate = Template('\n                <style>\n                    ol, li {\n                        line-height: 100%;\n                    }\n                </style>\n                <ol style="padding-left:0;line-height: 100%;">\n                  <li>Open the <span style="color: $fontBoldColor; font-weight: bold;">WiiM Home</span> app on your mobile device.</li>\n                  <li>Navigate to the Device tab, tap the gear icon for <span style="color: $fontBoldColor; font-weight: bold;">Device Settings</span>.</li>\n                  <li>Select <span style="color: $fontBoldColor; font-weight: bold;">Network Status</span> to view your device’s IP address. <a href=$url style="color:$linkColor; font-weight: bold;">Learn More></a></li>\n                </ol>\n            ')
        text = textTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), learnMoreUrl, LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('fontBoldColor', 'url', 'linkColor'))
        self.deviceDiscoverTip = LPGlobalUI.loadUI(ToolTipUI, Ui_toolTip, LPToolTip, text, self.tipButton)
        self.deviceDiscoverTip.textLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.deviceDiscoverTip.textLabel.setOpenExternalLinks(True)
        self.deviceDiscoverTip.textLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.deviceDiscoverTip.setFixedSize(QSize(380, 190))
        self.tipButton.clicked.connect(self.toggleTipPopup)

    
    def toggleTipPopup(self):
        if self.deviceDiscoverTip.isVisible():
            self.deviceDiscoverTip.hide()
        else:
            global_pos = self.tipButton.mapToGlobal(QPoint(0, 0))
            x = global_pos.x() + (self.tipButton.width() - self.deviceDiscoverTip.width()) // 2
            y = global_pos.y() - self.deviceDiscoverTip.height() - 10
            self.deviceDiscoverTip.move(x, y)
            self.deviceDiscoverTip.show()

    
    def eventFilter(self = None, source = None, event = None):
        if event.type() == QEvent.Type.FocusIn and self.focusWidget() == self.IPLineEdit and self.connectButton.state == 'failed':
            self.connectStatusChangeSignal.emit(ConnectStatus.DEFAULT)
        return super().eventFilter(source, event)

    
    def _preDiscover(self):
        self.IPLineEdit.clearFocus()
        self.connectStatusChangeSignal.emit(ConnectStatus.CONNECTING)
        ip = self.IPLineEdit.text()
        if ip and self.validateIP(ip) and LPGlobalUI.deviceManager:
            self.discoverSignal.emit(ip)
        else:
            self.showIPWarningToastSignal.emit()
            self.connectStatusChangeSignal.emit(ConnectStatus.DEFAULT)

    
    def exec(self = None):
        super().exec()

    
    def showEvent(self = None, event = None):
        super().showEvent(event)
        if self.parent:
            parent_center = self.parent.geometry().center()
            self.move(parent_center - self.rect().center())

    
    def discoverSuccess(self):
        self.connectStatusChangeSignal.emit(ConnectStatus.CONNECTED)
        self.closeTimer.start(3000)
        logger.debug('IP discover success')

    discoverSuccess = pyqtSlot()(discoverSuccess)
    
    def discoverFail(self):
        self.connectStatusChangeSignal.emit(ConnectStatus.FAILED)
        logger.debug('IP discover fail')

    discoverFail = pyqtSlot()(discoverFail)
    
    def attemptDiscover(self, ip):
        
        def _target():
            command = 'GetControlDeviceInfo'
            response = UPnPTool.upnpPost('http://%s:59152/upnp/control/rendercontrol1' % ip, 'RenderingControl:1', command, {
                'InstanceID': '0' }, [
                'Status'], 5, **('timeout',))
            if response and response.get('error', None) is None:
                statusDict = json.loads(response['Status'])
                uuid = statusDict.get('uuid', None)
                if uuid:
                    LPGlobalUI.deviceManager.deviceCome(uuid, ip, 59152, 'manual', **('serviceType',))
                    self.discoverSuccessSignal.emit()
                else:
                    self.discoverFailSignal.emit()
            else:
                self.discoverFailSignal.emit()

        t = threading.Thread(_target, **('target',))
        t.start()

    attemptDiscover = pyqtSlot(str)(attemptDiscover)
    
    def validateIP(self, ip):
        pass
    # WARNING: Decompyle incomplete

    
    def updateConnectButton(self, status):
        if status == ConnectStatus.CONNECTING:
            self.connectButton.setLoading()
            self.hideFailedTip(True)
        elif status == ConnectStatus.CONNECTED:
            self.connectButton.setSuccess()
            self.hideFailedTip(True)
        elif status == ConnectStatus.FAILED:
            self.connectButton.setFailed()
            self.hideFailedTip(False)
        else:
            self.connectButton.setIdle()
            self.hideFailedTip(True)

    updateConnectButton = pyqtSlot(object)(updateConnectButton)
    
    def showIPWarningToast(self):
        warningIconPath = LPGlobalUI.imagePath('error_ico_toast.png')
        titleText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'Invalid IP address format.')
        tipText = QCoreApplication.translate('IPDiscoverDeviceDialog', 'Please enter a valid IP address (e.g., 192.168.1.100).')
        IPWarningToast = LPGlobalUI.loadUI(IconToastUI, Ui_IconToast, IconToast, warningIconPath, titleText, tipText, LPGlobalUI.mainWindow)
        IPWarningToast.showToast()

    showIPWarningToast = pyqtSlot()(showIPWarningToast)
    
    def hideFailedTip(self, isHide):
        self.failedTipFrame.setHidden(isHide)
        QTimer.singleShot(0, self.adjustSize)

    __classcell__ = None

