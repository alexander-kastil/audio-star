# Source Generated with Decompyle++
# File: LPDeviceGroupManager.pyc (Python 3.9)

'''
@Time ： 2026/3/19 15:33
@Auth ： Chris
@File ：LPDeviceGroupManager.py
@Desc: Device Group manager singleton
'''
import copy
import json
import time
from threading import RLock
from LPClientFramework.LPDeviceManager.LPGroup import LPGroupObject, LPGroupType, LPGroupType_User, LPGroupType_Temp
from LPClientFramework.LPDeviceManager.LPGroupEditState import device_matches_group
from LPClientFramework.LPUtility import logger

def _diagnose_group_summary(group):
    '''生成命名组诊断摘要。

    Args:
        group (object): LPGroupObject 或命名组字典。

    Returns:
        dict: 仅包含排查 active/member 所需字段的摘要。
    '''
    if isinstance(group, dict):
        if not group.get('slavelist', []):
            pass
        slaveList = list([])
        master = None
        active = group.get('active', False)
        groupId = group.get('group_id', '')
        groupName = group.get('group_name', '')
        groupType = group.get('group_type', '')
    elif not getattr(group, 'slaveList', []):
        pass
    slaveList = getattr(group, 'slaveList', [])([])
    master = getattr(group, 'masterDevice', None)
    active = getattr(group, 'active', False)
    groupId = getattr(group, 'groupId', '')
    groupName = getattr(group, 'groupName', '')
    groupType = getattr(group, 'createGroupType', '')
    slaveUuids = []
    for item in slaveList:
        if uuidValue:
            slaveUuids.append(uuidValue)
            continue
    return {
        'group_id': groupId,
        'group_name': groupName,
        'group_type': groupType,
        'active': bool(active),
        'master_uuid': getattr(master, 'uuid', '') if master is not None else '',
        'slave_count': len(slaveList),
        'slave_uuids': slaveUuids }


def _diagnose_group_list(groups):
    '''生成命名组数组诊断摘要。

    Args:
        groups (list): 命名组对象或字典数组。

    Returns:
        list: 摘要数组。
    '''
    if not groups:
        pass
    return (lambda .0: [ _diagnose_group_summary(group) for group in .0 ])(list([]))


def _normalized_group_type_from_data(data, fallback):
    '''从命名组数据中提取并归一化 group_type。

    Args:
        data (dict): 命名组数据。
        fallback (int): 缺少 group_type 时采用的默认值。

    Returns:
        int: 归一化后的 group_type。
    '''
    fallback_value = LPGroupType.normalize(fallback, LPGroupType.Default)
    if not isinstance(data, dict):
        return fallback_value
    if None not in data:
        return fallback_value
    return None.normalize(data.get('group_type'), LPGroupType.Default)


class LPDeviceGroupObject(object):
    '''单台设备的命名组缓存桶，维护业务组对象和设备原始 group payload。'''
    
    def __init__(self, device_id):
        self.groupList = []
        self.editGroupList = []
        self.rawGroupInfo = { }
        self.rawEditGroupInfo = { }
        self.rawGroupList = []
        self.rawEditGroupList = []
        self._lock = RLock()

    
    def deviceAddGroupObj(self, groupObj, isFirst = (False,)):
        with self._lock:
            if isFirst:
                self.editGroupList.insert(0, groupObj)
                self.rawEditGroupList.insert(0, self.covertGroupObjToDictionary(groupObj))
            else:
                self.editGroupList.append(groupObj)
                self.rawEditGroupList.append(self.covertGroupObjToDictionary(groupObj))
            self._syncRawEditInfoList()
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def convertGroupToDictionaryArray(self):
        with self._lock:
            if self.rawEditGroupList:
                pass
            None(None, None, None)
            return None
            groups = (lambda .0: [ obj.copy() for obj in .0 ])(self.editGroupList)
            None(None, None, None)
        with None:
            if not None:
                pass
        return (lambda .0 = None: [ self.covertGroupObjToDictionary(group) for group in .0 ])(groups)

    
    def covertGroupObjToDictionary(self, group, baseGroup = (None,)):
        '''把命名组对象转换为设备保存接口使用的字典。

        Args:
            group (LPGroupObject): 需要序列化的命名组对象。
            baseGroup (dict): 设备返回的原始 group 字典，用于保留未知字段。

        Returns:
            dict: 可下发给设备的命名组字典。
        '''
        groupDict = copy.deepcopy(baseGroup) if isinstance(baseGroup, dict) else { }
        if not group.groupName:
            pass
        groupDict['group_name'] = ''
        if not getattr(group, 'groupFullName', '') and group.groupName:
            pass
        groupDict['fullName'] = ''
        if not group.groupId:
            pass
        groupDict['group_id'] = ''
        groupDict['group_type'] = LPGroupType.normalize(getattr(group, 'createGroupType', LPGroupType.Default), LPGroupType.Default)
        if not group.updateTime:
            pass
        groupDict['update_time'] = ''
        groupDict['channel'] = int(group.channel)
        if not groupDict.get('slavelist', []):
            pass
        baseSlaves = list([])
        baseSlaveMap = { }
        for item in baseSlaves:
            if not isinstance(item, dict):
                continue
            if not item.get('uuid', ''):
                pass
            uuid = str('').lower()
            if uuid:
                baseSlaveMap[uuid] = item
                continue
                groupDict['slavelist'] = []
                if not group.slaveList:
                    pass
        for slave in []:
            if isinstance(slave, dict):
                if not slave.get('name', ''):
                    pass
                name = ''
                if not slave.get('uuid', ''):
                    pass
                uuid = ''
                slaveData = dict(slave)
            elif not getattr(slave, 'name', ''):
                pass
            name = ''
            if not getattr(slave, 'uuid', ''):
                pass
            uuid = ''
            slaveData = {
                'name': name,
                'uuid': uuid }
            if not uuid:
                pass
            entry = copy.deepcopy(baseSlaveMap.get(str('').lower(), { }))
            entry.update(slaveData)
            entry['name'] = name
            entry['uuid'] = uuid
            if not slaveData.get('ip', ''):
                pass
            slaveIp = slaveData.get('ipv4', '')
            if slaveIp:
                entry['ipv4'] = slaveIp
            groupDict['slavelist'].append(entry)
        return groupDict

    
    def confirmGroupChanges(self, success):
        with self._lock:
            logger.debug('[group-diagnose][debug][LPDeviceGroupObject.confirmGroupChanges] success=%s beforeGroupList=%s beforeEditGroupList=%s', success, _diagnose_group_list(self.groupList), _diagnose_group_list(self.editGroupList))
            if success:
                self.groupList = (lambda .0: [ obj.copy() for obj in .0 ])(self.editGroupList)
                self.rawGroupList = copy.deepcopy(self.rawEditGroupList)
                self.rawGroupInfo = copy.deepcopy(self.rawEditGroupInfo)
            else:
                self.editGroupList = (lambda .0: [ obj.copy() for obj in .0 ])(self.groupList)
                self.rawEditGroupList = copy.deepcopy(self.rawGroupList)
                self.rawEditGroupInfo = copy.deepcopy(self.rawGroupInfo)
            logger.debug('[group-diagnose][debug][LPDeviceGroupObject.confirmGroupChanges.after] success=%s groupList=%s editGroupList=%s', success, _diagnose_group_list(self.groupList), _diagnose_group_list(self.editGroupList))
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def currentDeviceGroups(self):
        with self._lock:
            None(None, None, None)
            return (lambda .0: [ obj.copy() for obj in .0 ])(self.groupList)
            with None:
                if not None:
                    pass

    
    def currentRawGroupInfo(self):
        '''返回当前确认态的设备原始 group 信息。

        Args:
            无。

        Returns:
            dict: 设备 getnamegrouplist 返回信息的深拷贝。
        '''
        with self._lock:
            None(None, None, None)
            return copy.deepcopy(self.rawGroupInfo)
            with None:
                if not None:
                    pass

    
    def currentRawGroupList(self):
        '''返回当前确认态的设备原始 grouplist。

        Args:
            无。

        Returns:
            list: 原始 grouplist 深拷贝。
        '''
        with self._lock:
            None(None, None, None)
            return copy.deepcopy(self.rawGroupList)
            with None:
                if not None:
                    pass

    
    def _rawInfoFromGroupList(self, groupList):
        '''用业务组对象生成兜底 raw group 信息。

        Args:
            groupList (list): 业务组对象数组。

        Returns:
            dict: 包含 grouplist 的设备保存结构。
        '''
        if not groupList:
            pass
        return {
            None: (lambda .0 = None: [ self.covertGroupObjToDictionary(group) for group in .0 ])(list([])) }

    
    def _syncRawEditInfoList(self):
        '''把编辑态 raw group 列表同步回 rawEditGroupInfo。

        Args:
            无。

        Returns:
            None。
        '''
        if not isinstance(self.rawEditGroupInfo, dict):
            self.rawEditGroupInfo = { }
        self.rawEditGroupInfo['grouplist'] = copy.deepcopy(self.rawEditGroupList)

    
    def _findRawEditGroupIndex(self, groupId):
        '''按 group_id 查找编辑态 raw group 下标。

        Args:
            groupId (str): 目标 group_id。

        Returns:
            int: 命中时返回下标，未命中返回 -1。
        '''
        if not groupId:
            pass
        target = str('')
        if not target:
            return -1
        for index, item in None(self.rawEditGroupList):
            if not isinstance(item, dict) or item.get('group_id', ''):
                pass
            if str('') == target:
                return index
            return -1

    
    def updateGroupList(self, groupList, rawGroupInfo = (None,)):
        with self._lock:
            logger.debug('[group-diagnose][debug][LPDeviceGroupObject.updateGroupList] oldGroupList=%s newGroupList=%s', _diagnose_group_list(self.groupList), _diagnose_group_list(groupList))
            self.editGroupList = (lambda .0: [ obj.copy() for obj in .0 ])(groupList)
            self.groupList = (lambda .0: [ obj.copy() for obj in .0 ])(groupList)
            if isinstance(rawGroupInfo, dict):
                rawInfo = copy.deepcopy(rawGroupInfo)
            else:
                rawInfo = self._rawInfoFromGroupList(groupList)
            if not rawInfo.get('grouplist', []):
                pass
            rawGroupList = list([])
            self.rawEditGroupInfo = copy.deepcopy(rawInfo)
            self.rawGroupInfo = copy.deepcopy(rawInfo)
            self.rawEditGroupList = copy.deepcopy(rawGroupList)
            self.rawGroupList = copy.deepcopy(rawGroupList)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def getTempGroup(self):
        with self._lock:
            for obj in self.groupList:
                if obj.createGroupType == LPGroupType_Temp:
                    pass
                None(None, None, None)
                return None
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def deviceUpdateGroupObj(self, groupObj):
        with self._lock:
            for index, obj in enumerate(self.editGroupList):
                if obj.groupId == groupObj.groupId:
                    self.editGroupList[index] = groupObj
                    rawIndex = self._findRawEditGroupIndex(groupObj.groupId)
                baseGroup = self.rawEditGroupList[rawIndex] if rawIndex >= 0 else None
                rawGroup = self.covertGroupObjToDictionary(groupObj, baseGroup)
                if rawIndex >= 0:
                    self.rawEditGroupList[rawIndex] = rawGroup
                else:
                    self.rawEditGroupList.insert(index, rawGroup)
                self._syncRawEditInfoList()
            else:
                return None
            None(None, None, None)
        with None:
            if not None:
                pass



class LPDeviceGroupManager:
    '''设备命名组管理器，负责拉取、缓存、保存和查询设备命名组。'''
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
        self._groupsListLock = None()
        self._groupsArrayLock = RLock()
        self.groupListDict = { }
        self.allDevicesGroups = []
        self._initialized = True

    
    def instance(cls):
        return cls()

    instance = classmethod(instance)
    
    def makeGroupWithDevice(self, device):
        if not device.supportNamedGroup:
            logger.debug('[group-diagnose][debug][makeGroupWithDevice.skip] reason=notSupportNamedGroup device=%s uuid=%s', getattr(device, 'name', ''), getattr(device, 'uuid', ''))
            return False
        None.debug('[group-diagnose][debug][makeGroupWithDevice.enter] device=%s uuid=%s', getattr(device, 'name', ''), getattr(device, 'uuid', ''))
        changed = self.refreshDeviceGroups(device)
        logger.debug('[group-diagnose][debug][makeGroupWithDevice.exit] device=%s uuid=%s changed=%s', getattr(device, 'name', ''), getattr(device, 'uuid', ''), changed)
        return changed

    
    def _bucket(self, deviceId, create = (False,)):
        if not deviceId:
            return None
        with None._groupsListLock:
            bucket = self.groupListDict.get(deviceId)
            if bucket is None and create:
                bucket = LPDeviceGroupObject(deviceId)
                self.groupListDict[deviceId] = bucket
            None(None, None, None)
            return bucket
            with None:
                if not None:
                    pass

    
    def addGroup(self, groupObj):
        bucket = self._bucket(groupObj.masterDevice.uuid, True, **('create',))
        logger.debug('[group-diagnose][debug][deviceGroupManager.addGroup.enter] group=%s currentBucketGroups=%s', _diagnose_group_summary(groupObj), _diagnose_group_list(bucket.currentDeviceGroups()) if bucket is not None else [])
        bucket.deviceAddGroupObj(groupObj, True, **('isFirst',))
        groupList = bucket.convertGroupToDictionaryArray()
        if bool(groupList):
            pass
        success = self.saveGroupList(groupObj.masterDevice, groupList)
        bucket.confirmGroupChanges(success)
        self._rebuildAllGroups()
        logger.debug('[group-diagnose][debug][deviceGroupManager.addGroup.exit] success=%s savedGroupList=%s bucketGroups=%s', success, _diagnose_group_list(groupList), _diagnose_group_list(bucket.currentDeviceGroups()) if bucket is not None else [])
        return success

    
    def _allDeviceBuckets(self):
        with self._groupsListLock:
            None(None, None, None)
            return list(self.groupListDict.values())
            with None:
                if not None:
                    pass

    
    def _rebuildAllGroups(self):
        groups = []
        for bucket in self._allDeviceBuckets():
            groups.extend(bucket.currentDeviceGroups())
        with self._groupsArrayLock:
            self.allDevicesGroups = groups
            None(None, None, None)
        with None:
            if not None:
           