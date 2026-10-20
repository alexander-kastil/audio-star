# Source Generated with Decompyle++
# File: LPDeviceSettingDeviceViewController.pyc (Python 3.9)

import json
import re
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication
from PyQt6.sip import isdeleted
from threading import Thread
import time
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import DeviceSettings_Subtitle
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter

class LPDeviceSettingDeviceViewController(QWidget):
    updateNetworkStatusSignal = pyqtSignal()
    finishRenameSignal = pyqtSignal(object)
    
    def __init__(self = None, deviceId = None, showLoadingButtonSignal = None, renameCallback = None):
        super(LPDeviceSettingDeviceViewController, self).__init__()
        self.deviceId = deviceId
        self.showLoadingButtonSignal = showLoadingButtonSignal
        self.renameCallback = renameCallback
        self.standbyTimeArray = [
            30,
            120,
            300,
            900,
            1800,
            3600,
            -1]
        self.fiveGHzBand = False
        self.preferDNS = False
        self.wlanRoam = False
        self.enableIPv6 = False
        self.hasStandbyMode = True
        self.powerModeTime = -1
        self.asyncThread = None
        self.updateStandbyTimeArray()

    
    def updateStandbyTimeArray(self):
        device = LPGlobalUI.deviceManager.deviceForUUID(self.deviceId)
        if not device:
            return None
        if None.isWiiMAMP:
            self.standbyTimeArray = [
                30,
                120,
                300,
                900,
                1800,
                3600]

    
    def setupUi(self = None, ui = None):
