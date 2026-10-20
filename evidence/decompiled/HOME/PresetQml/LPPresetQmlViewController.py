# Source Generated with Decompyle++
# File: LPPresetQmlViewController.pyc (Python 3.9)

__doc__ = '\nPreset（预设快捷键）QML 版页面控制器。\n\n职责：\n- 作为 QWidget 宿主，内嵌 QQuickWidget 加载 LPPresetQmlPage.qml。\n- 把自身作为 QML contextProperty("controller") 暴露，提供页面状态、数据模型与交互槽。\n- viewWillAppear 时向设备请求 GetKeyMapping，解析后刷新模型。\n- 处理卡片点击（MCUKeyShortClick）与右键删除（弹通用确认框 + SetKeyMapping）。\n\n业务逻辑迁移自 HOME/LPPresetViewController.py，但与之完全解耦，开发期并行对比。\n'
import copy
from typing import Optional
from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from bs4 import BeautifulSoup
import LPGlobalUI
from LPClientFramework import LPStreamServiceManager, LPUtility
from LPClientFramework.LPDeviceStreamServiceManager import DEVICE_ACCOUNT_UNKNOWN
from HOME.PresetQml.LPPresetQmlStore import LPPresetListModel, LPPresetQmlStore, presetSourceCanPlay, presetSourceNeedsDeviceAccount
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title
from LPClientFramework.LPUtility import logger
# WARNING: Decompyle incomplete
