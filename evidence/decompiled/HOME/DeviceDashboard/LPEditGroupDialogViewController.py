# Source Generated with Decompyle++
# File: LPEditGroupDialogViewController.pyc (Python 3.9)

'''
@Time ： 2026/3/30 9:49
@Auth ： Chris
@File ：LPEditGroupDialogViewController.py
@Desc:
'''
import threading
from PyQt6.QtCore import QCoreApplication, QEvent, QPoint, Qt, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
import LPGlobalUI
from HOME.DeviceDashboard.LPDeviceItemWrapper import LPDeviceItemWrapper
from LPClientFramework import LPUtility
from LPClientFramework.LPDeviceManager.LPGroupEditState import is_group_edit_no_change, normalize_uuid, uuid_from_group_item
from LPClientFramework.LPDeviceManager.LPDeviceNodeManager import LPDeviceNodeManager
from LPClientFramework.LPDeviceManager.LPGroupManager import LPGroupManager, LPNewGroupEditType
from LPClientFramework.LPUtility import logger

def _diagnose_device_summary(device):
    '''生成设备诊断摘要。

    Args:
        device (object): 设备对象。

    Returns:
        dict: 设备名称、uuid、组态和成员摘要。
    '''
    if device is None:
        return { }
    group_info = None(device, 'groupInfo', None)
    slave_uuids = []
    if not getattr(group_info, 'slaveList', []):
        pass
    for item in list([]):
        slave_uuid = uuid_from_group_item(item)
        if slave_uuid:
            slave_uuids.append(slave_uuid)
            continue
    return {
        'name': getattr(device, 'name', ''),
        'uuid': normalize_uuid(getattr(device, 'uuid', '')),
        'roomState': getattr(group_info, 'roomState', '') if group_info is not None else '',
        'masterID': normalize_uuid(getattr(group_info, 'masterID', '')) if group_info is not None else '',
        'slaveUuids': slave_uuids }


def _diagnose_group_summary(group):
    '''生成命名组诊断摘要。

    Args:
        group (object): 命名组对象。

    Returns:
        dict: 命名组 id、名称、active 和成员摘要。
    '''
    if group is None:
        return { }
    if not getattr(group, 'slaveList', []):
        pass
    return {
        'groupId': None(group, 'groupId', ''),
        'groupName': getattr(group, 'groupName', ''),
        'active': bool(getattr(group, 'active', False)),
        'masterUuid': normalize_uuid(getattr(getattr(group, 'masterDevice', None), 'uuid', '')),
        'slaveUuids': (lambda .0: [ uuid_from_group_item(item) for item in .0 if uuid_from_group_item(item) ])(list([])) }


class LPEditGroupDialogViewController(QWidget):
    groupEditOptionsChanged = pyqtSignal()
    groupEditInitialSelectedUuidsChanged = pyqtSignal()
    groupEditSelectedGroupIdChanged = pyqtSignal()
    groupEditBusyChanged = pyqtSignal()
    groupEditErrorTextChanged = pyqtSignal()
    groupEditPrimaryRowsChanged = pyqtSignal()
    groupEditOtherRowsChanged = pyqtSignal()
    groupEditCloseRequested = pyqtSignal()
    groupEditPreparedSignal = pyqtSignal(object, object, str)
    groupEditFinishedSignal = pyqtSignal(object)
    
    def createForHostWindow(cls, parent = (None,)):
        controller = cls(parent, **('parent',))
        controller.setupUi()
        return controller

    createForHostWindow = classmethod(createForHostWindow)
    
    def __init__(self = None, deviceSourceGetter = None, shouldDisplayDevice = None, reclassifyCallback = None, parent = None):
        super().__init__(parent)
        self.setObjectName('editGroupDialogOverlay')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.groupMgr = LPGroupManager.instance()
        self.nodeMgr = LPDeviceNodeManager.instance()
        if not deviceSourceGetter:
            pass
        self._deviceSourceGetter = self._defaultDeviceSourceGetter
        if not shouldDisplayDevice:
            pass
        self._shouldDisplayDevice = self._defaultShouldDisplayDevic