# Source Generated with Decompyle++
# File: LPMyMusicSettingViewController.pyc (Python 3.9)

import re
import time
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QCoreApplication, QEvent
from PyQt6.QtGui import QColor
from HOME.LPSuperTableWidget import LPSuperTableWidgetDelegate
from HOME.LPWaitingSpinner import LPWaitingSpinner
from LPClientFramework import LPUtility, LPBeetsWrapper, LPHttpServerManager
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, DeviceSettings_Subtitle
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPUtility import logger
import LPGlobalUI

class LPMyMusicSettingViewController(QWidget):
    showLoadingButtonSignal = pyqtSignal(object)
    updateUPnPSignal = pyqtSignal()
    trackedDirRefreshSignal = pyqtSignal()
    
    def __init__(self = None, myMusicDirAddCallback = None, myMusicDirRemoveCallback = None):
        '''
        初始化 My Music 设置页控制器。

        参数:
            myMusicDirAddCallback (callable | None): 添加目录回调。
            myMusicDirRemoveCallback (callable | None): 删除目录回调。
        返回:
            无
        '''
        super(LPMyMusicSettingViewController, self).__init__()
        self.myMusicDirAddCallback = myMusicDirAddCallback
        self.myMusicDirRemoveCallback = myMusicDirRemoveCallback
        self.upnpLoadingSpinner = None
        upnpDict = LPUtility.objectForUserconfig('upnpserver')
        self.upnpEnable = upnpDict.get('enable', False)
        self.lastUPnPUpdateTime = upnpDict.get('lastUpdate', None)
        self.upnpName = upnpDict.get('name', '')
        self.showLoadingButtonSignal.connect(self._showLoadingButton)
        self.updateUPnPSignal.connect(self.updateUPnP)
        self.trackedDirRefreshSignal.connect(self.setupTable)
        self.preventSleepEnable = upnpDict.get('preventSleep', False)
        self._myMusicDirObserverRegistered = False
        self._hiddenBetaTapTimestamps = []
        self._hiddenBetaTapWindowSeconds = 5
        self._hiddenBetaTapThreshold = 10
        self.destroyed.connect(self._onDestroyed)

    
    def setupUi(self = None, ui = None):
        '''
        绑定界面控件行为并初始化样式/状态。

        参数:
            ui (QWidget): 已加载 UI 的宿主控件实例。
        返回:
            无
        '''
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self._registerMyMusicDirObserver()
        for toggle in (self.upnpToggle, self.sleepToggle, self.memoryResidentToggle):
            toggle.setCheckedColor(LPGlobalUI.THEME_ACCENT_COLOR)
        self.addDirButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('lib/mymusic_add.png')))
        self.addDirButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n\nQPushButton:hover {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}        ' % (LPGlobalUI.THEME_BUTTON_BACK_COLOR.name(), LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name()))
        self.addDirButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.addDirButton.clicked.connect(self.showAddDirectoryBox)
        delegate = LPSuperTableWidgetDelegate()
        self.folderTableWidget.hoverIndexChanged.connect(delegate.onHoverIndexChanged)
        self.folderTableWidget.leaveTableEvent.connect(delegate.onLeaveTableEvent)
        self.folderTableWidget.setItemDelegate(delegate)
        self.folderTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folderTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.folderTableWidget.verticalScrollBar().setSingleStep(1)
        self.folderTableWidget.horizontalHeader().resizeSection(1, 30)
        self.folderTableWidget.setStyleSheet('\n            QTableWidget::item {color: white}\nQTableWidget::item:selected{\nselection-color: white;\nbackground-color: transparent;\n}\nQTableWidget{selection-background-color: transparent; border: none;}\nQTableWidget::item:hover{background: rgb(31,31,31); color: white}\nQScrollBar {\n        border: 0px;\n        background: transparent;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle {\n        background: rgb(82,82,82);\n        min-height: 0px;\n\tborder-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        border: 0px;\n}\nQHeaderView::section {\nbackground-color: transparent;\ncolor: white;\n}\n')
        self.setupTable()
        self.upnpNameField.setText(self.upnpName)
        self.upnpNameField.returnPressed.connect(self._upnpNameButtonClicked)
        None((lambda : self.upnpNameButton.show()))
        self.upnpNameButton.hide()
        self.upnpNameButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n\nQPushButton:hover {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}        ' % (LPGlobalUI.THEME_BUTTON_BACK_COLOR.name(), LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name()))
        self.upnpNameButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    # WARNING: Decompyle incomplete

    
    def setupTable(self):
