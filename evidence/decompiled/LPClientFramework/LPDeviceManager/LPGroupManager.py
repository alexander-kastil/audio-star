# Source Generated with Decompyle++
# File: LPGroupManager.pyc (Python 3.9)

'''
@Time ： 2026/3/17 15:44
@Auth ： Chris
@File ：LPGroupManager.py
@Desc: Group manager singleton
'''
import enum
import json
import threading
import time
import uuid
from threading import RLock
from PyQt6.QtCore import QObject, pyqtSlot
import LPGlobalUI
from LPClientFramework import LPPublicDefine, LPUtility
from LPClientFramework.LPDeviceManager.LPDeviceGroupManager import LPDeviceGroupManager
from LPClientFramework.LPDeviceManager.LPDeviceNodeManager import LPDeviceNodeManager
from LPClientFramework.LPDeviceManager.LPGroup import LPGroupObject, LPGroupType_Temp
from LPClientFramework.LPUtility import logger
UnsupportedChangeMusicMediaType = [
    LPPublicDefine.MEDIATYPE_LINEIN,
    LPPublicDefine.MEDIATYPE_BLUETOOTH,
    LPPublicDefine.MEDIATYPE_EXTERNAL_USB,
    LPPublicDefine.MEDIATYPE_USB_DAC,
    LPPublicDefine.MEDIATYPE_EXTERNAL_TF,
    LPPublicDefine.MEDIATYPE_OPTICAL,
    LPPublicDefine.MEDIATYPE_OPTICAL2,
    LPPublicDefine.MEDIATYPE_AIRPLAY,
    LPPublicDefine.MEDIATYPE_CO_AXIAL,
    LPPublicDefine.MEDIATYPE_CO_AXIAL2,
    LPPublicDefine.MEDIATYPE_HDMI,
    LPPublicDefine.MEDIATYPE_PHONO]

def _diagnose_device_summary(device):
    '''生成设备分组诊断摘要。

    Args:
        device (object): 设备对象。

    Returns:
        dict: 设备名称、uuid、roomState、masterID 和 slaveUuids。
    '''
    if device is None:
        return { }
    groupInfo = None(device, 'groupInfo', None)
    slaveUuids = []
    if not getattr(groupInfo, 'slaveList', []):
        pass
    for item in list([]):
        if isinstance(item, dict):
            uuidValue = item.get('uuid', '')
        else:
            uuidValue = getattr(item, 'uuid', '')
        normalized = LPUtility.pureUUID(uuidValue)
        if normalized:
            slaveUuids.append(normalized)
            continue
    return {
        'name': getattr(device, 'name', ''),
        'uuid': LPUtility.pureUUID(getattr(device, 'uuid', '')),
        'roomState': getattr(groupInfo, 'roomState', '') if groupInfo is not None else '',
        'masterID': LPUtility.pureUUID(getattr(groupInfo, 'masterID', '')) if groupInfo is not None else '',
        'slaveUuids': slaveUuids }


def _diagnose_group_summary(group):
