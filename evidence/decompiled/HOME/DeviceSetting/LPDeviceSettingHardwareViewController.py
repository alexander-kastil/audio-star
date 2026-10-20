# Source Generated with Decompyle++
# File: LPDeviceSettingHardwareViewController.pyc (Python 3.9)

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

class LPDeviceSettingHardwareViewController(QWidget):
    updateHardwareSignal = pyqtSignal()
    
    def __init__(self = None, deviceId = None, showLoadingButtonSignal = None):
        super(LPDeviceSettingHardwareViewController, self).__init__()
        self.deviceId = deviceId
        self.showLoadingButtonSignal = showLoadingButtonSignal
        self.statusLight = False
        self.volumeIndicator = False
        self.touchControls = False
        self.overrideVolumeButtons = None

    
    def setupUi(self = None, ui = None):
