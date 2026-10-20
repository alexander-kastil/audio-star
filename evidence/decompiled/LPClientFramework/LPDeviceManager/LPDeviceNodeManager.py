# Source Generated with Decompyle++
# File: LPDeviceNodeManager.pyc (Python 3.9)

'''
@Time ： 2026/3/12 18:48
@Auth ： Chris
@File ：LPDeviceNodeManager.py
@Desc:
'''
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from typing import Dict, List
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPDevice import LPDevice
from LPClientFramework.LPDeviceManager.LPDeviceGroupManager import LPDeviceGroupManager
from LPClientFramework.LPUtility import logger, logAcctBifurcate

def _raw_uuid(raw_uuid = None):
    return LPUtility.pureUUID(raw_uuid)


def _diagnose_device_ref(device):
    '''生成设备引用诊断摘要。

    Args:
        device (object): 设备对象。

    Returns:
        dict: 设备名称、uuid 和当前组态字段摘要。
    '''
    if device is None:
        return { }
    groupInfo = None(device, 'groupInfo', None)
    return {
        'name': getattr(device, 'name', ''),
        'uuid': _raw_uuid(getattr(device, 'uuid', '')),
        'roomState': getattr(groupInfo, 'roomState', '') if groupInfo is not None else '',
        'masterID': _raw_uuid(getattr(groupInfo, 'masterID', '')) if groupInfo is not None else '',
        'slaveUuids': (lambda .0: for item in .0:
passcontinue_raw_uuid[_raw_uuid(item.get('uuid', '') if item.get('uuid', '')(getattr(item, 'uuid', '')) or isinstance(item, dict) else getattr(item, 'uuid', ''))])(list([])) if groupInfo is not None else [] }


def _diagnose_named_groups(groups):
    '''生成命名组 active 诊断摘要。

    Args:
        groups (list): 命名组对象数组。

    Returns:
        list: 命名组摘要数组。
    '''
    result = []
    if not groups:
        pass
    for group in list([]):
        if not getattr(group, 'slaveList', []):
            pass
        result.append({
            'groupId': getattr(group, 'groupId', ''),
            'groupName': getattr(group, 'groupName', ''),
            'active': bool(getattr(group, 'active', False)),
            'masterUuid': _raw_uuid(getattr(getattr(group, 'masterDevice', None), 'uuid', '')),
            'slaveUuids': (lambda .0: for item in .0:
passcontinue_raw_uuid[_raw_uuid(item.get('uuid', '') if item.get('uuid', '')(getattr(item, 'uuid', '')) or isinstance(item, dict) else getattr(item, 'uuid', ''))])(list([])) })
    return result


class LPDeviceDisplayGroup:
    
    def __init__(self, masterDevice, onlineSlaveList = (None, None)):
        self.masterDevice = masterDevice
        if not onlineSlaveList:
            pass
        self.onlineSlaveList = list([])



class LPDeviceNodeManager:
    _instance = None
    _instanceLock = RLock()
    
    def __new__(cls = None, *args, **kwargs):
        if cls._instance is None:
            with cls._instanceLock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                None(None, None, None)
            with None:
                if not None:
                    pass
        return cls._instance

    
    def __init__(self):
        if getattr(self, '_initialized', False):
            return None
        self._lock = None()
        LPUtility.registerDeviceInfoChanged(self)
        self._executor = ThreadPoolExecutor(5, 'node-group', **('max_workers', 'thread_name_prefix'))
        self.deviceGroupMgr = LPDeviceGroupManager().instance()
        self._rawDevices = []
        self._initialized = True

    
    def instance(cls):
        return cls()

    instance = classmethod(instance)
    
    def _syncChildStateFromMasterSlaveList(self, detail):
        if not detail:
            pass
        slaveAction = { }.get('slaveAction', None)
        if not isinstance(slaveAction, dict):
            return False
        if not slaveAction.get('action', ''):
            pass
        action = None('').lower()
        masterDevice = slaveAction.get('master', None)
        targetSlaveId = slaveAction.get('slaveId', '')
        if masterDevice is None and targetSlaveId or action not in frozenset({'add', 'rm'}):
            return False
        masterGroupInfo = None(masterDevice, 'groupInfo', None)
        if masterGroupInfo is None:
            return False
        changed = None
        slaveDevice = self.findRawDeviceByUuid(targetSlaveId)
        if not getattr(masterGroupInfo, 'slaveList', []):
            pass
        memberIds = (lambda .0 = None: pass# WARNING: Decompyle incomplete
)(list([]))
        beforeStates = (lambda .0: [ _diagnose_device_ref(device) for device in .0 ])(self.getRawDevicesSnapshot())
        logger.debug('[group-diagnose][_syncChildStateFromMasterSlaveList.enter] action=%s master=%s targetSlaveId=%s memberIds=%s before=%s', action, _diagnose_device_ref(masterDevice), _raw_uuid(targetSlaveId), sorted((lambda .0: [ memberId for memberId in .0 if memberId ])(memberIds)), beforeStates)
        if masterGroupInfo.roomState != 'master':
            masterGroupInfo.roomState = 'master'
            changed = True
        if _raw_uuid(getattr(masterGroupInfo, 'masterID', '')) != masterDevice.uuid:
            masterGroupInfo.masterID = masterDevice.uuid
            changed = True
        for onlineDevice in self.getRawDevicesSnapshot():
            onlineUuid = _raw_uuid(getattr(onlineDevice, 'uuid', ''))
            if onlineUuid or onlineUuid == masterDevice.uuid:
                continue
            onlineGroupInfo = getattr(onlineDevice, 'groupInfo', None)
            if onlineGroupInfo is None:
                continue
            if onlineUuid in memberIds:
                if onlineGroupInfo.roomState != 'slave':
                    onlineGroupInfo.roomState = 'slave'
                    changed = True
                if _raw_uuid(getattr(onlineGroupInfo, 'masterID', '')) != masterDevice.uuid:
                    onlineGroupInfo.masterID = masterDevice.uuid
                    changed = True
                    continue
                    if onlineGroupInfo.roomState == 'slave' and _raw_uuid(getattr(onlineGroupInfo, 'masterID', '')) == masterDevice.uuid:
                        onlineGroupInfo.roomState = 'master'
                        if onlineGroupInfo.masterID != onlineDevice.uuid:
                            onlineGroupInfo.masterID = onlineDevice.uuid
            changed = True
        if changed:
            if not getattr(masterGroupInfo, 'slaveList', []):
                pass
            logger.debug('[node manager] sync slaveAction action=%s master=%s slave=%s childCount=%s', action, getattr(masterDevice, 'name', ''), getattr(slaveDevice, 'name', '') if slaveDevice is not None else targetSlaveId, len([]))
        logger.debug('[group-diagnose][_syncChildStateFromMasterSlaveList.exit] action=%s changed=%s master=%s slave=%s after=%s', action, changed, _diagnose_device_ref(masterDevice), _diagnose_device_ref(slaveDevice) if slaveDevice is not None else {
            'uuid': _raw_uuid(targetSlaveId) }, (lambda .0: [ _diagnose_device_ref(device) for device in .0 ])(self.getRawDevicesSnapshot()))
        return changed

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if infoType != 'multiRoom':
            return None
        if not None:
            pass
        detail = { }
        if 'slaveAction' in detail:
            self._syncChildStateFromMasterSlaveList(detail)
            self.updateShowGroups()
        if 'lpmrm' in detail:
            body = detail['lpmrm']
            self._handleNamedGroupNotify(device, body)

    
    def _handleNamedGroupNotify(self, device, body):
        if not device is None or isinstance(body, dict):
            return False
        changed = None
        if not body.get('group_relationship_changed', ''):
            pass
        relationChanged = str('')
        if not body.get('group_id', ''):
            pass
        groupId = str('')
        deviceId = getattr(device, 'uuid', '')
        bucket = self.deviceGroupMgr._bucket(deviceId, False, **('create',))
        beforeGroups = bucket.currentDeviceGroups() if bucket is not None else []
        logger.debug('[group-diagnose][_handleNamedGroupNotify.enter] device=%s uuid=%s relationChanged=%s groupId=%s body=%s activeBefore=%s', getattr(device, 'name', ''), deviceId, relationChanged, groupId, body, _diagnose_named_groups(beforeGroups))
        if relationChanged == '1':
            logger.debug('[node manager] lpmrm relationship changed device=%s', getattr(device, 'name', ''))
            changed = bool(self.deviceGroupMgr.readyGroupWithDevice(device))
            bucket = self.deviceGroupMgr._bucket(deviceId, False, **('create',))
            afterGroups = bucket.currentDeviceGroups() if bucket is not None else []
            logger.debug('[group-diagnose][_handleNamedGroupNotify.relationshipChanged] device=%s uuid=%s changed=%s activeAfter=%s', getattr(device, 'name', ''), deviceId, changed, _diagnose_named_groups(afterGroups))
            self.updateShowGroups()
            return changed
        if None:
            changed = bool(self.deviceGroupMgr.updateGroupActive(groupId, deviceId))
            bucket = self.deviceGroupMgr._bucket(deviceId, False, **('create',))
            afterGroups = bucket.currentDeviceGroups() if bucket is not None else []
            logger.debug('[node manager] lpmrm active changed device=%s groupId=%s changed=%s', getattr(device, 'name', ''), groupId, changed)
            logger.debug('[group-diagnose][_handleNamedGroupNotify.activeChanged] device=%s uuid=%s groupId=%s changed=%s activeAfter=%s', getattr(device, 'name', ''), deviceId, groupId, changed, _diagnose_named_groups(afterGroups))
            self.updateShowGroups()
            return changed

    
    def appendDeviceOrderByName(self, targetList, obj):
        if targetList is None or obj is None:
            return False
        obj_uuid = None(getattr(obj, 'uuid', ''))
        if not getattr(obj, 'name', ''):
            pass
        obj_name = ''.lower()
        if obj_uuid:
            for idx, item in enumerate(targetList):
                if _raw_uuid(getattr(item, 'uuid', '')) == obj_uuid:
                    targetList.pop(idx)
                
                insert_at = len(targetList)
                for idx, item in enumerate(targetList):
                    if not getattr(item, 'name', ''):
                        pass
                    item_name = ''.lower()
                    if obj_name < item_name:
                        insert_at = idx
                    
                    targetList.insert(insert_at, obj)
                    return True

    
    def deviceOnline(self = None, onlineDevice = None):
        with self._lock:
            self.appendDeviceOrderByName(self._rawDevices, onlineDevice)
            None(None, None, None)
        with None:
            if not None:
                pass
        self.dealDeviceOnline(onlineDevice)

    
    def dealDeviceOnline(self, onlineDevice):
        self._asyncMakeGroupWithDevice(onlineDevice)

    
    def _asyncMakeGroupWithDevice(self, onlineDevice):
        
        def worker(target_device = None):
            logger.debug('[group-diagnose][_asyncMakeGroupWithDevice.worker] device=%s uuid=%s', getattr(target_device, 'name', ''), getattr(target_device, 'uuid', ''))
            return self.deviceGroupMgr.makeGroupWithDevice(target_device)

        
        def cb(future = None):
            pass
        # WARNING: Decompyle incomplete

        fut = self._executor.submit(worker, onlineDevice)
        fut.add_done_callback(cb)

    
    def _updateDeviceGroupTitles(self, rawDeviceMap):
        self.deviceGroupMgr.updateDeviceGroupTitles(rawDeviceMap)

    
    def _memberUuidFromGroupItem(self, item):
        if item is None:
            return ''
        if None(item, dict):
            return _raw_uuid(item.get('uuid', ''))
        return None(getattr(item, 'uuid', ''))

    
    def _buildOwnerMembers(self, rawDeviceMap):
