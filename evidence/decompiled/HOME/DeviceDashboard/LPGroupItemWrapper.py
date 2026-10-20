# Source Generated with Decompyle++
# File: LPGroupItemWrapper.pyc (Python 3.9)

'''
@Time ： 2026/3/13 17:46
@Auth ： Chris
@File ：LPGroupItemWrapper.py
@Desc:
'''
import threading
import time
from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QCoreApplication, pyqtSlot, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QPixmap, QImage
import LPGlobalUI
from HOME.DeviceDashboard.LPDeviceCoverImageHelper import coverCanvasPixmap
from HOME.DeviceDashboard.LPGroupMemberListModel import LPGroupMemberListModel
from HOME.DeviceSetting.LPDeviceSettingViewController import LPDeviceSettingViewController
from HOME.DeviceSetting.LPDeviceSettingViewController_ui import Ui_deviceSettingViewWidget
from LPClientFramework import LPUtility, LPStreamServiceManager
from LPClientFramework.LPConfig import LPUIPath, LPFontConfig
from LPClientFramework.LPDeviceManager.LPDeviceGroupManager import LPDeviceGroupManager
from LPClientFramework.LPDeviceManager.LPGroup import LPGroupType, LPGroupType_Temp, LPGroupObject
from LPClientFramework.LPPalette import extractThemeColorRgbFromImage
from LPClientFramework.LPUtility import logger

class LPGroupItemWrapper(QObject):
    updateUISignal = pyqtSignal()
    deviceNameChanged = pyqtSignal()
    groupTitleChanged = pyqtSignal()
    groupSubtitleChanged = pyqtSignal()
    groupPrimaryNameChanged = pyqtSignal()
    groupSecondaryNameChanged = pyqtSignal()
    isUserGroupChanged = pyqtSignal()
    memberRowsChanged = pyqtSignal()
    trackNameChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    playStateChanged = pyqtSignal()
    artistNameChanged = pyqtSignal()
    coverChanged = pyqtSignal()
    bgColorChanged = pyqtSignal()
    sourceIconChanged = pyqtSignal()
    muteChanged = pyqtSignal()
    fixedVolumeChanged = pyqtSignal()
    groupVolumeLockedChanged = pyqtSignal()
    
    def __init__(self = None, groupNode = None):
        super().__init__()
        self.node = groupNode
        self.device = groupNode.masterDevice
        self._memberModel = LPGroupMemberListModel(self, **('parent',))
        self.deviceGroupManager = LPDeviceGroupManager.instance()
        self.updateUISignal.connect(self._updateItem)
        self.originalBackgroundColor = QColor(77, 77, 77)
        self._bgColor = self.originalBackgroundColor
        self.artwork = ''
        self.isSourceShow = False
        self._mute = False
        self._fixedVolume = False
        self._coverCache = ''
        self._coverPixmapKey = None
        self._hasArtwork = False
        self._coverUpdateTimer = QTimer(self)
        self._coverUpdateTimer.setSingleShot(True)
        self._coverUpdateTimer.timeout.connect(self._updateCoverImageAsync)
        self._groupVolumeLastSendTs = 0
        self._groupVolumeSendInterval = 0.15
        self._memberVolumeLastSendTs = { }
        self._memberVolumeSendInterval = 0.15
        self._memberDragging = False
        self._memberDragRecoverTimer = QTimer(self)
        self._memberDragRecoverTimer.setSingleShot(True)
        self._memberDragRecoverTimer.timeout.connect(self._onMemberDragRecover)
        self._memberPreventUntil = { }
        self._memberVolumePostInFlight = { }
        self._memberVolumePostPending = { }
        self._memberVolumePostLock = threading.Lock()
        self._createdAt = time.monotonic()
        self._inView = False
        self._mute = self._computeGroupMute()
        self._refreshMemberModel()
        LPUtility.registerDeviceInfoChanged(self)
        self._updateCoverImageAsync()

    
    def updateProjection(self, groupNode):
        if groupNode is None:
            return None
        self.node = None
        self.device = getattr(groupNode, 'masterDevice', None)
        self._updateItem()

    
    def dispose(self):
        pass
    # WARNING: Decompyle incomplete

    
    def nameFont(self):
        return LPFontConfig.Main_Text

    nameFont = pyqtProperty(float, True, **('constant',))(nameFont)
    
    def trackNameFont(self):
        return LPFontConfig.Main_Text

    trackNameFont = pyqtProperty(float, True, **('constant',))(trackNameFont)
    
    def artistNameFont(self):
        return LPFontConfig.Sub_Text

    artistNameFont = pyqtProperty(float, True, **('constant',))(artistNameFont)
    
    def volNumFont(self):
        return LPFontConfig.Sub_Text

    volNumFont = pyqtProperty(float, True, **('constant',))(volNumFont)
    
    def memberFont(self):
        return LPFontConfig.Sub_Text

    memberFont = pyqtProperty(float, True, **('constant',))(memberFont)
    
    def _child_count(self):
        child_count = 0
        device = self.device
        group_info = getattr(device, 'groupInfo', None) if device is not None else None
        if group_info is not None:
            if not getattr(group_info, 'slaveList', []):
                pass
            child_count = len([])
            if child_count == 0:
                if not getattr(group_info, 'slaveBoxArray', []):
                    pass
                child_count = len([])
        if child_count == 0 and self.node is not None:
            if not getattr(self.node, 'onlineSlaveList', []):
                pass
            child_count = len([])
        return child_count

    
    def _master_plus_count(self):
        device = self.device
        if device is None:
            return ''
        if not None(device, 'name', ''):
            pass
        master_name = ''.strip()
        if not master_name:
            return ''
        child_count = None._child_count()
        if child_count > 0:
            return f'''{master_name} +{child_count}'''

    
    def _named_group_title(self):
        device = self.device
        group_info = getattr(device, 'groupInfo', None) if device is not None else None
        if group_info is None:
            return ''
        if not None(group_info, 'groupTitle', ''):
            pass
        named = ''.strip()
        if named:
            return named
        if not None(group_info, 'groupName', ''):
            pass
        named = ''.strip()
        if named:
            return named

    
    def _active_group(self):
        device = self.device
        if device is None:
            return None
        :
            device = self.device
            if device is None:
                return None
            
            return self.deviceGroupManager.getActiveGroupWithDevice(device)
        return self.deviceGroupManager.getActiveGroupWithDevice(device)
    # WARNING: Decompyle incomplete

    
    def _online_slave_list(self):
        if not getattr(self.node, 'onlineSlaveList', []):
            pass
        return list([])

    
    def _volume_group_object(self):
        group = self._active_group()
        if group is not None and getattr(group, 'masterDevice', None) is not None:
            return group
        master = None.device
        group_info = getattr(master, 'groupInfo', None) if master is not None else None
        return LPGroupObject(getattr(group_info, 'groupName', '') if group_info is not None else '', master, '', list([]) if group_info is not None else [], bool(getattr(group_info, 'roomState', '') == 'master') if group_info is not None else False, LPGroupType.normalize(getattr(group_info, 'currentGroupType', LPGroupType.Default) if group_info is not None else LPGroupType.Default, LPGroupType.Default), **('groupName', 'masterDevice', 'groupId', 'slaveList', 'active', 'createGroupType'))

    
    def isUserGroup(self):
        group = self._active_group()
        if group is None:
            return False
        return None(group, 'createGroupType', LPGroupType_Temp) != LPGroupType_Temp

    isUserGroup = pyqtProperty(bool, isUserGroupChanged, **('notify',))(isUserGroup)
    
    def groupPrimaryName(self):
