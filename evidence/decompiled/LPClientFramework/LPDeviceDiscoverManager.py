# Source Generated with Decompyle++
# File: LPDeviceDiscoverManager.pyc (Python 3.9)

from collections import OrderedDict
import os
import re
import json
from enum import Enum
from socket import *
import struct
import threading
import time
from datetime import datetime
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPCache.LPDeviceFileCache import LPDeviceFileCache
from LPClientFramework.LPCache.LPFileCache import FileCache
from LPClientFramework.LPDevice import LPDevice
from LPClientFramework.LPDeviceManager.LPDeviceNodeManager import LPDeviceNodeManager
from LPClientFramework.LPDiscoveryTelemetry import LPDiscoveryTelemetry
from LPClientFramework.LPMediaServer import LPMediaServer
from LPClientFramework.LPUPnPObserverManager import LPUPnPObserverManager
from LPClientFramework.LPUtility import logger
MCAST_IP = '239.255.255.250'
MCAST_PORT = 1900

class CacheType(Enum):
    Device = 'device'
    MediaServer = 'mediaServer'


class LPDeviceDiscoverManager(ServiceListener):
    
    def __init__(self, addMethod, rmvMethod, mediaServerAddMethod, mediaServerRmvMethod, removeAllMethod, searchKey = ('ssdp:wiimudevice',)):
        '''通过SSDP发现设备
        addMethod: 设备发现回调
        rmvMethod: 设备丢失回调，超时100s
        searchKey: SSDP search key
        '''
        self.searchKey = searchKey
        self.deviceListLock = threading.RLock()
        self.deviceRecordList = OrderedDict()
        self.mediaServerRecordList = []
        self.searchThread = None
        self.msearchSocket = None
        self.notifySocket = None
        self.dealWithResponseThread = None
        self.dealWithNotifyThread = None
        self.checkThread = None
        self.addMethod = addMethod
        self.rmvMethod = rmvMethod
        self.mediaServerAddMethod = mediaServerAddMethod
        self.mediaServerRmvMethod = mediaServerRmvMethod
        self.internetConnection = None
        if not LPUtility.fetchNetworkInfo():
            pass
        networkInfo = { }
        self.currentGW = networkInfo.get('gateway')
        self.internetMonitorThread = None
        self.searchingSwitch = False
        self.fastSearchingSwitch = False
        self.upnpObserverManager = LPUPnPObserverManager(self.upnpNotifyCome)
        self.upnpObserverManager.start()
        self.fileCache = LPDeviceFileCache(LPUtility.cacheDir)
        self.telemetry = LPDiscoveryTelemetry(self)
        self.onlineRunning = True
        self.removeAllMethod = removeAllMethod
        self.networkSwitchLock = threading.Lock()
        self.deviceNodeMgr = LPDeviceNodeManager.instance()

    
    def deviceList(self):
        retArray = []
        with self.deviceListLock:
            for key in list(self.deviceRecordList):
                item = self.deviceRecordList[key]
                deviceObj = item['device']
                if deviceObj.statusDict is None:
                    continue
                if deviceObj.isWiiMSub:
                    continue
                retArray.append(item['device'])
            None(None, None, None)
        with None:
            if not None:
                pass
        return retArray

    deviceList = property(deviceList)
    
    def mediaServerList(self):
        retArray = []
        with self.deviceListLock:
            for key in list(self.mediaServerRecordList):
                item = self.mediaServerRecordList[key]
                retArray.append(item['device'])
            None(None, None, None)
        with None:
            if not None:
                pass
        return retArray

    mediaServerList = property(mediaServerList)
    
    def deviceForUUID(self, uuid):
        with self.deviceListLock:
            for key in list(self.deviceRecordList):
                item = self.deviceRecordList[key]
                deviceObj = item['device']
                if deviceObj.statusDict is None:
                    continue
                if deviceObj.uuid == uuid:
                    pass
                None(None, None, None)
                return None
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def removeDevice(self, uuid):
        with self.deviceListLock:
            item = self.deviceRecordList.get(uuid, None)
            if item:
                self.deviceRecordList.pop(uuid)
                self.upnpObserverManager.removeObserver(item['ip'])
                if self.rmvMethod:
                    self.rmvMethod(item['device'])
                self.telemetry.onDeviceRemoved(uuid)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def startSearch(self):
        self.onlineCachedDevice()
        self.onlineCachedMediaServer()
        self.searchingSwitch = True
        with self.deviceListLock:
            self.deviceRecordList = OrderedDict()
            self.mediaServerRecordList = OrderedDict()
            None(None, None, None)
        with None:
            if not None:
                pass
        
        def ssdpThreadMethod():
            pass
        # WARNING: Decompyle incomplete

        
        def notifyThreadMethod():
            pass
        # WARNING: Decompyle incomplete

        
        def ssdpCheckThreadMethod():
            if self.searchingSwitch:
                time.sleep(10)
                rmvList = []
                with self.deviceListLock:
                    for key in list(self.deviceRecordList):
                        item = self.deviceRecordList[key]
                        lastUpdate = item['date']
                        seconds = (datetime.now() - lastUpdate).seconds
                    None(None, None, None)
                    continue
                    with None:
                        if not None:
                            pass
                continue

        
        def dealWithSSDPResponse(response = None):
            responseString = response.decode()
            locationKey = 'LOCATION'
            host = re.search('(?<=%s: http://).*?(?=/)' % locationKey, responseString)
            if not host:
                locationKey = 'Location'
                host = re.search('(?<=%s: http://).*?(?=/)' % locationKey, responseString)
                if not host:
                    return None
                hostArr = None.group().split(':')
                ip = hostArr[0]
                port = int(hostArr[1])
                uuid = re.search('(?<=USN: uuid:).*?(?=:)', responseString)
                if not uuid:
                    return None
                uuid = None.group()
                serviceType = None
                ST = re.search('ST:.*?$', responseString, re.S | re.M)
                if not ST:
                    NT = re.search('NT:.*?$', responseString, re.S | re.M)
                    NTS = re.search('NTS:.*?$', responseString, re.S | re.M)
                    if not NT or NTS:
                        return None
                    if None in NTS.group():
                        serviceType = NT.group()
                    else:
                        serviceType = ST.group()
            if serviceType is None:
                return None
            if None in serviceType:
                uuid = uuid[:-len(uuid.split('-')[0])].replace('-', '')
                self.deviceCome(uuid, ip, port)
            elif 'ContentDirectory' in serviceType or 'MediaServer' in serviceType:
                location = re.search('(?<=%s: ).*?$' % locationKey, responseString, re.S | re.M)
                if not location:
                    logger.debug('Invalid media server, ignore: %s' % responseString)
                    return None
                desURL = None.group().strip()
                self.mediaServerCome(uuid, ip, port, desURL)

        
        def sendMSearch():
            if not self.searchingSwitch:
                pass
        # WARNING: Decompyle incomplete

        self.msearchSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.msearchSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # WARNING: Decompyle incomplete

    
    def mediaServerCome(self, uuid, ip, port, desURL, serviceType = ('ssdp',)):
        networkInfo = LPUtility.fetchNetworkInfo()
        if not networkInfo:
            logger.debug('[mediaServerCome] no active physical LAN, ignore media server: %s' % ip)
            return None
        gateway = None.get('gateway')
        netmask = networkInfo.get('netmask')
        isInCurrentNetwork = LPUtility.isIPInGateway(ip, gateway, netmask)
        if not isInCurrentNetwork:
            return None
        serverRecord = None.mediaServerRecordList.get(uuid, None)
        if not serverRecord:
            serverObj = LPMediaServer(ip, port, desURL)
            serverDict = {
                'uuid': uuid,
                'date': datetime.now(),
                'ip': ip,
                'device': serverObj }
            
            def _mediaServerInitFinish(success = None):
                if self.mediaServerAddMethod:
                    if success:
                        if not LPUtility.fetchNetworkInfo():
                            pass
                        currentNetworkInfo = { }
                        self.cacheDevice(currentNetworkInfo.get('gateway'), serverObj, CacheType.MediaServer)
                        self.mediaServerAddMethod(serverObj)
                        logger.info('mediaServerCome from %s: %s' % (serviceType, ip))
                    else:
                        server = self.mediaServerRecordList.get(uuid, None)
                        if server:
                            logger.debug('Invalid media server, ignore: %s' % self.mediaServerRecordList[uuid])
                            with self.deviceListLock:
                                del self.mediaServerRecordList[uuid]
                                None(None, None, None)
                            with None:
                                if not None:
                                    pass
                        else:
                            logger.debug('Invalid media server, ignore uuid: %s' % uuid)

            with self.deviceListLock:
                self.mediaServerRecordList[uuid] = serverDict
                serverObj.start(_mediaServerInitFinish)
                None(None, None, None)
            with None:
                if not None:
                    pass
        else:
            serverRecord['date'] = datetime.now()

    
    def deviceCome(self, uuid, ip, port, serviceType = ('ssdp',)):
        deviceObj = None
        isDeviceNew = False
        isDeviceUpdate = False
        networkInfo = LPUtility.fetchNetworkInfo()
        if not networkInfo:
            logger.debug('[deviceCome] no active physical LAN, ignore device: %s' % ip)
            return None
        gateway = None.get('gateway')
        if serviceType == 'cache':
            netmask = networkInfo.get('netmask')
            isInCurrentNetwork = LPUtility.isIPInGateway(ip, gateway, netmask)
            if not isInCurrentNetwork:
                logger.debug(f'''[deviceCome] gateway {gateway} , Device {ip} not current network, netmask -> {netmask}''')
                return None
            None.telemetry.onDeviceSeen(uuid, serviceType)
            with self.deviceListLock:
                deviceRecord = self.deviceRecordList.get(uuid, None)
                if not deviceRecord:
                    isDeviceNew = True
                    logger.info('deviceCome from %s: %s' % (serviceType, ip))
                else:
                    deviceRecord['date'] = datetime.now()
                    deviceObj = deviceRecord['device']
                    if (deviceObj.ip != ip or deviceObj.upnpPort != port) and serviceType != 'cache':
                        isDeviceUpdate = True
                        logger.info('deviceCome update from %s: %s->%s, %d->%d' % (serviceType, deviceObj.ip, ip, deviceObj.upnpPort, port))
                        self.upnpObserverManager.removeObserver(deviceObj.ip)
                        deviceObj.upnpPort = port
                        deviceObj.ip = ip
                    elif not self.upnpObserverManager.hasObserverForUUID(uuid):
                        logger.info('deviceCome re-subscribe for %s (IP/port unchanged but observer missing, serviceType=%s)', ip, serviceType)
                        self.upnpObserverManager.addObserver(deviceObj.ip, deviceObj.upnpPort, uuid)
                if isDeviceNew:
                    deviceObj = LPDevice(ip, port)
                    deviceDict = {
                        'uuid': uuid,
                        'date': datetime.now(),
                        'ip': ip,
                        'device': deviceObj,
                        'gateway': gateway }
                    self.deviceRecordList[uuid] = deviceDict
                None(None, None, None)
            with None:
                if not None:
                    pass
        if isDeviceNew or isDeviceUpdate:
            result = deviceObj.init()
            if result is False:
                logger.error('Device %s init failed from %s' % (ip, serviceType))
                with self.deviceListLock:
                    self.deviceRecordList.pop(uuid, None)
                    None(None, None, None)
                with None:
                    if not None:
                        pass
                self.telemetry.onDeviceRemoved(uuid)
                return None
            self.upnpObserverManager.addObserver(deviceObj.ip, deviceObj.upnpPort, uuid)
            self.cacheDevice(gateway, deviceObj)
            self.telemetry.onDeviceAdded(uuid)
            if isDeviceNew and callable(self.addMethod):
                self.addMethod(deviceObj)
                self.deviceNodeMgr.deviceOnline(deviceObj)

    
    def upnpNotifyCome(self, uuid, message):
        deviceDict = self.deviceRecordList.get(uuid, None)
        logger.debug(f'''upnpNotifyCome recv -> {repr(message)}''')
        if deviceDict is None:
            return None
        device = None['device']
        info = message.get('info', None)
        slaveAction = message.get('slaveAction', None)
        lpMRM = message.get('lpmrm', None)
    # WARNING: Decompyle incomplete

    
    def update_service(self = None, zc = None, type_ = None, name = {
        'zc': Zeroconf,
        'type_': str,
        'name': str,
        'return': None }):
        info = zc.get_service_info(type_, name)
        if info is None:
            logger.error('update_server info is none: %s' % name)
            return None
        uuid = None.properties.get(b'uuid', None)
        addresses = info.addresses
        port = info.port
        if uuid and addresses or len(addresses) == 0:
            logger.error('update_server Invalid device: %s' % info)
            return None
        uuid = None.decode('utf-8')[5:]
        uuid = uuid[:-len(uuid.split('-')[0])].replace('-', '')
        ip = inet_ntoa(addresses[0])
        if ip or len(ip) == 0:
            logger.error('Invalid device: %s' % info)
            return None
        None.info('mdns device updated: %s, %s:%d, %s' % (name, ip, port, info))
        logger.info('Ignore mdns device update message')

    
    def remove_service(self = None, zc = None, type_ = None, name = {
        'zc': Zeroconf,
        'type_': str,
        'name': str,
        'return': None }):
        logger.info('mdns device removed: %s' % name)
        info = zc.get_service_info(type_, name)
        if not info:
            logger.error('Found no device to remove: %s, %s' % (type_, name))
            return None
        uuid = None.properties.get(b'uuid', None)
        if not uuid:
            logger.error('Found no device to remove: %s' % info)
            return None

    
    def add_service(self = None, zc = None, type_ = None, name = {
        'zc': Zeroconf,
        'type_': str,
        'name': str,
        'return': None }):
        info = zc.get_service_info(type_, name)
        if info is None or info.properties is None:
            logger.error('Invalid device, info nil: %s, %s' % (type_, name))
            return None
        uuid = None.properties.get(b'uuid', None)
        addresses = info.addresses
        port = info.port
        if uuid and addresses or len(addresses) == 0:
            logger.error('Invalid device: %s' % info)
            return None
        uuid = None.decode('utf-8')[5:]
        uuid = uuid[:-len(uuid.split('-')[0])].replace('-', '')
        ip = inet_ntoa(addresses[0])
        if ip or len(ip) == 0:
            logger.error('Invalid device: %s' % info)
            return None
        None.info('mdns device add: %s, %s:%d, %s' % (name, ip, port, info))
        self.deviceCome(uuid, ip, info.port, 'mdns', **('serviceType',))

    
    def monitorInternet(self):
        if not LPUtility.fetchNetworkInfo():
            pass
        networkInfo = { }
        currentGW = networkInfo.get('gateway')
        oldGW = self.currentGW
        signalEmitted = False
        if currentGW and currentGW != oldGW:
            self.currentGW = currentGW
            LPGlobalUI.signalBus.Network_Changed_Signal.emit(oldGW, currentGW)
            logger.debug('send Network_Changed_Signal')
            signalEmitted = True
            self.telemetry.onNetworkChanged(oldGW, currentGW)
        self.telemetry.onGatewayPoll(currentGW, signalEmitted)
        result = LPUtility.pingGoogle()
        if self.internetConnection is None:
            logger.info('Internet status: %s' % LPUtility.pingGoogle())
            logger.info('Network: %s, info: %s, SSID: %s' % (LPUtility.fetchNetworkType(), LPUtility.fetchNetworkInfo(), LPUtility.currentSSID()))
            self.internetConnection = result
            self.telemetry.onInternetPoll(result)
            continue
        if result != self.internetConnection:
            self.internetConnection = result
            logger.info('Internet status change: %s' % result)
            logger.info('Network: %s, info: %s, SSID: %s' % (LPUtility.fetchNetworkType(), LPUtility.fetchNetworkInfo(), LPUtility.currentSSID()))
        self.telemetry.onInternetPoll(result)
        time.sleep(5)
        continue

    
    def onNetworkChanged(self, oldGW, newGW):
        logger.debug('[device manager] onNetworkChanged')
        LPGlobalUI.currentDevice = None
        self.removeAll()
        self.removeAllMethod()
        self.deviceNodeMgr.clearRawDevices(True, **('emitProjection',))
        self.deviceNodeMgr.clearNameGroup()
        t = threading.Thread(self._restartDiscoveryOnNetworkChanged, **('target',))
        t.setDaemon(True)
        t.start()

    
    def _restartDiscoveryOnNetworkChanged(self):
        with self.networkSwitchLock:
            self.stop()
            self.onlineRunning = True
            self.upnpObserverManager.start()
            self.startSearch()
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def removeAll(self):
        self.deviceRecordList.clear()
        self.mediaServerRecordList.clear()
        self.telemetry.onAllDevicesRemoved()

    
    def closeSocket(self, sock):
        pass
    # WARNING: Decompyle incomplete

    
    def onlineCachedDevice(self):
        
        def _target():
