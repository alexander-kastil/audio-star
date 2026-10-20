# Source Generated with Decompyle++
# File: LPDeviceSettingBtSourceViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction, QColor
from enum import IntEnum
from threading import Thread
import time
import json
import LPGlobalUI
from HOME.LPSuperTableWidget import LPSuperTableWidgetDelegate
from HOME.LPWaitingSpinner import LPWaitingSpinner
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title
from LPClientFramework.LPUtility import logger

class LPBTPairStatusEnum(IntEnum):
    GET_BT_PAIR_STATUS_DISCONNECTING = 0
    GET_BT_PAIR_STATUS_NOT_PAIR = 1
    GET_BT_PAIR_STATUS_PAIRING = 2
    GET_BT_PAIR_STATUS_PAIR_SUCCESS = 3
    GET_BT_PAIR_STATUS_PAIR_FAILED = 4


class LPDeviceSettingBtSourceViewController(QWidget):
    updateHistorySignal = pyqtSignal()
    updateDiscoverySignal = pyqtSignal()
    showLoadingButtonSignal = pyqtSignal(object)
    
    def __init__(self = None, deviceId = None):
        super(LPDeviceSettingBtSourceViewController, self).__init__()
        self.deviceId = deviceId
        self.loadingSpinner = None
        self.keepGetBluetoothHistory = False
        self.BTHistoryArray = []
        self.BTDiscoverArray = []
        self.discoveryBTDeviceTime = 5
        self.keepSearchingBTDevice = False
        self.discoveryCount = 0
        self.keepGetPairStatus = False
        self.pairCheckCount = 0
        
        def _updateHistoryUI():
