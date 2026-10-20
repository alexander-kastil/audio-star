# Source Generated with Decompyle++
# File: LPDeviceSettingApCastViewController.pyc (Python 3.9)

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

class LPDeviceSettingApCastViewController(QWidget):
    updateTableSignal = pyqtSignal()
    showLoadingButtonSignal = pyqtSignal(object)
    
    def __init__(self = None, deviceId = None):
        super(LPDeviceSettingApCastViewController, self).__init__()
        self.deviceId = deviceId
        self.loadingSpinner = None
        self.apList = []
        
        def _updateTableUI():
            showList = []
            for index, itemDict in enumerate(self.apList):
                showItem = [
                    itemDict.get('name', ''),
                    itemDict.get('selected', False),
                    index]
                showList.append(showItem)
            rowCount = len(showList)
            self.tableWidget.setRowCount(rowCount)
            for i in range(rowCount):
                for j in range(3):
                    if j == 0:
                        data = QTableWidgetItem(showList[i][j])
                        self.tableWidget.setItem(i, j, data)
                        continue
                    if j == 1:
                        data = QTableWidgetItem()
                        if showList[i][j] is True:
                            data.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('checkmark.png')))
                    self.tableWidget.setItem(i, j, data)
            self.tableWidget.resizeRowsToContents()

        self.updateTableSignal.connect(_updateTableUI)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        device = LPGlobalUI.deviceManager.deviceForUUID(self.deviceId)
        if device is not None:
            if device.supportDLNACast:
                self.titleLabel.setText(QCoreApplication.translate('ApCast', '%s - DLNA Out') % device.name)
                self.apNoteLabel.setText(QCoreApplication.translate('ApCast', 'Cast audio from %s to DLNA-enabled speakers.') % device.productShowName)
                self.tableHeaderNoteLabel.setText(QCoreApplication.translate('ApCast', 'DLNA-enabled Speakers'))
            else:
                self.titleLabel.setText(QCoreApplication.translate('ApCast', '%s - WiiM Cast') % device.name)
                self.apNoteLabel.setText(QCoreApplication.translate('ApCast', 'Cast audio from %s to HomePod and other AirPlay or AirPlay 2 enabled speakers.') % device.productShowName)
                self.tableHeaderNoteLabel.setText(QCoreApplication.translate('ApCast', 'Airplay-enabled Speakers'))
        delegate = LPSuperTableWidgetDelegate()
        self.tableWidget.hoverIndexChanged.connect(delegate.onHoverIndexChanged)
        self.tableWidget.leaveTableEvent.connect(delegate.onLeaveTableEvent)
        self.tableWidget.setItemDelegate(delegate)
        self.tableWidget.horizontalHeader().resizeSection(0, 400)
        self.tableWidget.horizontalHeader().resizeSection(1, 50)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tableWidget.verticalScrollBar().setSingleStep(1)
        self.tableWidget.cellClicked.connect(self.tableClicked)
        self.tableWidget.setStyleSheet('\n            QTableWidget::item {color: white}\nQTableWidget::item:selected{\nselection-color: white;\nbackground-color: transparent;\n}\nQTableWidget{selection-background-color: transparent; border: none;}\nQTableWidget::item:hover{background: transpar