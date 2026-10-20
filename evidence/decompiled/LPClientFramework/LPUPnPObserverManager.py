# Source Generated with Decompyle++
# File: LPUPnPObserverManager.pyc (Python 3.9)

import json
from http.server import BaseHTTPRequestHandler
from functools import partial
import threading
import platform
import requests
import datetime
import time
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
from time import mktime
from bs4 import BeautifulSoup
from LPClientFramework import LPUtility
from LPClientFramework.LPUtility import logger, LPThreadHTTPServer
SOAP_PARSER = 'xml'

class LPBasicUPnPServiceParser(object):
    
    def parse(self, xml):
        lastChange = BeautifulSoup(xml, SOAP_PARSER)
        retDict = { }
        for key, value in self.observeAttributes.items():
            item = lastChange.find(key, None)
            if item is None:
                continue
            valType = value.get('type', str)
            temp = item.get('val', '')
            if (valType == int and valType == float or valType == bool) and temp == '':
                temp = '0'
            if valType == bool:
                temp = int(temp)
            retDict[value['name']] = valType(temp)
            logger.debug(f'''retDict recv -> {value['name']}: {valType(temp)}''')
        retDict['message'] = xml
        return retDict

    
    def parserForService(cls, serviceName):
        if serviceName == 'rendercontrol1':
            return LPRenderControlParser()
        if None == 'rendertransport1':
            return LPRenderTransportParser()
        if None == 'PlayQueue1':
            return LPPlayQueueParser()

    parserForService = classmethod(parserForService)


class LPRenderControlParser(LPBasicUPnPServiceParser):
    
    def __init__(self):
        self.observeAttributes = {
            'Volume': {
                'name': 'volume',
                'type': float },
            'Mute': {
                'name': 'mute',
                'type': bool },
            'FixVolume': {
                'name': 'fixedVolume',
                'type': bool },
            'DeviceName': {
                'name': 'deviceName' } }
        self.multiRoomMessageKey = 'Slave'
        self.commonEventMessageKey = 'commonevent'

    
    def parse(self = None, xml = None):
        retDict = super().parse(xml)
        lastChange = BeautifulSoup(xml, SOAP_PARSER)
        mrmItem = lastChange.find(self.multiRoomMessageKey, None)
        if mrmItem:
            action = mrmItem.get('action', None)
            slave = mrmItem.get('val', None)
            if action and slave:
                retDict['slaveAction'] = {
                    'action': action,
                    'slaveId': slave }
        commonEventItem = lastChange.find(self.commonEventMessageKey, None)
    # WARNING: Decompyle incomplete

    __classcell__ = None


class LPRenderTransportParser(LPBasicUPnPServiceParser):
    
    def __init__(self):
        self.observeAttributes = {
            'TransportState': {
                'name': 'playState' },
            'CurrentTrackMetaData': {
                'name': 'metaData' },
            'CurrentTrackURI': {
                'name': 'playUri' },
            'CurrentTrack': {
                'name': 'lastPlayIndex',
                'type': int },
            'TrackSource': {
                'name': 'trackSource' },
            'PlaybackStorageMedium': {
                'name': 'mediaType' },
            'CurrentTrackDuration': {
                'name': 'duration' },
            'A_ARG_TYPE_SeekTarget': {
                'name': 'progress' } }
        self.metaAttributes = {
            'song:guibehavior': {
                'name': 'guiBehavior' },
            'song:id': {
                'name': 'trackId' },
            'custom:uuid': {
                'name': 'customUUID' },
            'dc:title': {
                'name': 'trackName' },
            'song:singerid': {
                'name': 'artistId' },
            'upnp:artist': {
                'name': 'artist' },
            'song:albumid': {
                'name': 'albumId' },
            'upnp:album': {
                'name': 'album' },
            'upnp:albumArtURI': {
                'name': 'artworkUri' },
            'upnp:localAlbumArtURI': {
                'name': 'localArtworkUri' },
            'song:quality': {
                'name': 'quality',
                'type': int },
            'song:actualQuality': {
                'name': 'actualQuality' },
            'song:rate_hz': {
                'name': 'trackRateHz',
                'type': float },
            'song:format_s': {
                'name': 'trackFormat',
                'type': float },
            'song:bitrate': {
                'name': 'trackBitrate',
                'type': float },
            'upnp:ratingURI': {
                'name': 'ratingURI' } }

    
    def parse(self = None, xml = None):
        retDict = super().parse(xml)
        metaData = retDict.get('metaData', None)
        if not metaData:
            return retDict
        metaDataObj = None(metaData, SOAP_PARSER)
        item = metaDataObj.find('item', None)
        if not item:
            return retDict
        for key, value in None.metaAttributes.items():
            valType = value.get('type', str)
            temp = item.find(key, None)
            if not temp:
                continue
            temp = temp.text
            if (valType == int and valType == float or valType == bool) and temp == '':
                temp = '0'
            if valType == bool:
                temp = int(temp)
            retDict[value['name']] = valType(temp)
        resArray = metaDataObj.findAll('res')
        for resItem in resArray:
            duration = resItem.get('duration', None)
            if duration is not None or duration.isdigit():
                duration = int(duration)
                duration = datetime.timedelta(duration / 1000, **('seconds',))
                minutes = duration.seconds // 60
                seconds = duration.seconds - minutes * 60
                if seconds == seconds or seconds == 0:
                    pass
                else:
                    minutes
            else:
                retDict['duration'] = '00:00:00'
        duration = '00:%02d:%02d' % (minutes, seconds)
        continue
        retDict['duration'] = duration.split('.')[0]
        continue
        retDict['progress'] = '00:00:00'
        itemId = item.get('id', None)
        retDict['itemId'] = itemId if itemId else ''
        itemName = item.get('name', None)
        if itemName:
            retDict['itemName'] = itemName
        return retDict

    __classcell__ = None


class LPPlayQueueParser(LPBasicUPnPServiceParser):
    
    def __init__(self):
        self.observeAttributes = {
            'LoopMode': {
                'name': 'loopMode',
                'type': int },
            'LoopMpde': {
                'name': 'loopMode',
                'type': int },
            'CurretPlayListName': {
                'name': 'queueName' },
            'info': {
                'name': 'info' } }

    
    def parse(self = None, xml = None):
        return super().parse(xml)

    __classcell__ = None


class LPSimpleUPnPObserverHandler(BaseHTTPRequestHandler):
    '''接收设备 NOTIFY，并把 SID、SEQ 和 LastChange 交给订阅管理器。'''
    
    def __init__(self = None, messageMethod = None, *args, **kwargs):
        '''保存通知回调并初始化 HTTP handler；参数为回调及 HTTP 参数，返回无。'''
        self.messageMethod = messageMethod
    # WARNING: Decompyle incomplete

    
    def do_NOTIFY(self):
        '''解析并分发设备通知；无参数，返回无。'''
        if urlparse(self.path).path != '/Event':
            self.send404()
            return None
        bodyData = None.rfile.read(int(self.headers.get('content-length', 0)))
        parsedData = BeautifulSoup(bodyData.decode('utf-8'), SOAP_PARSER)
        lastChange = parsedData.find('LastChange')
        if not lastChange:
            self.send404()
            return None
        sid = None.headers.get('SID', None)
        seq = self.headers.get('SEQ', None)
        self.messageMethod(sid, lastChange.text, seq)
        stamp = mktime(datetime.datetime.now().timetuple())
        stamp = format_date_time(stamp)
    # WARNING: Decompyle incomplete

    
    def send404(self):
        '''返回不支持的通知响应；无参数，返回无。'''
        self.send_response(404)
        stamp = mktime(datetime.datetime.now().timetuple())
        stamp = format_date_time(stamp)
        self.send_header('Date', stamp)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"error": "404"}')

    __classcell__ = None


class LPUPnPObserverManager(object):
    '''维护设备各服务的事件订阅、续期和通知分发。'''
    SERVICES = ('rendercontrol1', 'PlayQueue1', 'rendertransport1')
    RENEW_RATIO = 0.8
    RETRY_INTERVAL = 10
    FIRST_NOTIFY_TIMEOUT = 10
    EARLY_NOTIFY_TTL = 10
    MAX_EARLY_NOTIFICATIONS = 20
    
    def __init__(self, notifyComeMethod):
        '''初始化订阅状态；参数为业务通知回调，返回无。'''
        self.httpServer = None
        self.port = 22334
        self.observerDictLock = threading.RLock()
        self.notifyLock = threading.RLock()
        self.lifecycleLock = threading.RLock()
        self.observerDict = { }
        self.serviceRecords = { }
        self.earlyNotifications = []
        self.notifyComeMethod = notifyComeMethod
        self.serverThread = None
        self.timeoutThread = None
        self.serverSwitch = False
        self._generation = 0
        self._stopEvent = threading.Event()

    
    def start(self):
        '''同步绑定监听端口并启动通知及租约线程；无参数，返回是否成功。'''
        pass
    # WARNING: Decompyle incomplete

    
    def stop(self):
        '''停止监听并使所有旧代次异步结果失效；无参数，返回无。'''
        logger.info('Stop UPnP server')
    # WARNING: Decompyle incomplete

    
    def addObserver(self, ip, port, uuid):
        '''确保设备三个服务各自存在订阅；参数为地址、端口和 UUID，返回无。'''
        records = []
        with self.observerDictLock:
            if not self.serverSwitch:
                pass
            None(None, None, None)
            return None
            for service in self.SERVICES:
                key = (uuid, service)
                record = self.serviceRecords.get(key)
                if record is not None and (record['ip'], record['port']) != (ip, port):
                    self._removeRecord(record)
                    record = None
                if record is None:
                    record = self._newRecord(ip, port, service, uuid)
                    self.serviceRecords[key] = record
                if not record['sid'] is None and record['inFlight']:
                    records.append(record)
                None(None, None, None)
            with None:
                if not None:
                    pass
        for record in records:
            self._launchSubscription(record, False, **('renew',))

    
    def removeObserver(self, ip):
        '''删除指定 IP 的全部服务订阅；参数为 IP，返回无。'''
        with self.observerDictLock:
            for key, record in list(self.serviceRecords.items()):
                if record['ip'] == ip:
                    del self.serviceRecords[key]
                    self._removeRecord(record)
                None(None, None, None)
            with None:
                if not None:
                    pass

    
    def _newRecord(self, ip, port, service, uuid):
        '''创建服务订阅记录；参数为地址、端口、服务和 UUID，返回字典。'''
        return {
            'uuid': uuid,
            'service': service,
            'ip': ip,
            'port': port,
            'sid': None,
            'timeout': 1800,
            'renewAt': 0,
            'expireAt': 0,
            'retryAt': 0,
            'inFlight': False,
            'receivedNotify': False,
            'firstNotifyDeadline': 0,
            'firstNotifyRetries': 0,
            'lastSeq': None,
            'generation': self._generation }

    
    def _removeRecord(self, record):
        '''删除记录的 SID 路由；参数为订阅记录，返回无。'''
        sid = record.get('sid')
        if sid and self.observerDict.get(sid) is record:
            del self.observerDict[sid]

    
    def _isCurrent(self, record, generation):
        '''判断异步结果是否仍属于当前运行代次；参数为记录和代次，返回布尔值。'''
        key = (record['uuid'], record['service'])
        if self.serverSwitch and generation == self._generation and record['generation'] == generation:
            pass
        return self.serviceRecords.get(key) is record

    
    def _launchSubscription(self, record, renew):
        '''以 single-flight 方式启动创建或续期；参数为记录及续期标记，返回无。'''
        with self.observerDictLock:
            generation = self._generation
            if self._isCurrent(record, generation) or record['inFlight']:
                pass
            None(None, None, None)
            return None
            record['inFlight'] = True
            None(None, None, None)
        with None:
            if not None:
                pass
        if not record['uuid']:
            pass
        deviceName = str('unknown')[:8]
        thread = threading.Thread(self._performSubscription, (record, generation, renew), 'UPnPSubscribe-%s-%s' % (deviceName, record['service']), True, **('target', 'args', 'name', 'daemon'))
        thread.start()

    
    def _performSubscription(self, record, generation, renew):
        '''执行一次创建或续期并提交结果；参数为记录、代次及续期标记，返回无。'''
        with self.observerDictLock:
            if not self._isCurrent(record, generation):
                pass
            None(None, None, None)
            return None
            oldSid = record['sid'] if renew else None
            None(None, None, None)
        with None:
            if not None:
                pass
        headers = {
            'TIMEOUT': 'Second-1800',
            'User-Agent': '%s/%s UPnP/1.1 %s/%s' % (platform.system(), platform.release(), 'LPUnittest', LPUtility.appVersion) }
        if oldSid:
            headers['SID'] = oldSid
        else:
            headers['NT'] = 'upnp:event'
            headers['CALLBACK'] = '<http://%s:%d/Event>' % (LPUtility.fetchLocalIP(), self.port)
        status = None
        returnedSid = None
    # WARNING: Decompyle incomplete

    
    def _parseTimeout(self, rawTimeout):
        '''解析设备返回的 TIMEOUT；参数为原始头，返回正整数秒数。'''
        if not rawTimeout:
            pass
        value = ''.strip()
        if value.lower() == 'second-infinite':
            return 1800
        if None.lower().startswith('second-'):
            timeout = int(value[7:])
            if timeout > 0:
                return timeout
            raise None('invalid TIMEOUT')

    
    def _timeoutLoop(self, stopEvent, generation):
        '''定期检查租约和首通知；参数为停止事件及代次，返回无。'''
        if not stopEvent.wait(5):
            self._maintainSubscriptions(generation)
            continue

    
    def _maintainSubscriptions(self, generation):
        '''调度到期续期、失败重试和一次首通知重订阅；参数为代次，返回无。'''
        actions = []
        now = time.monotonic()
        with self.observerDictLock:
            if not generation != self._generation or self.serverSwitch:
                pass
            None(None, None, None)
            return None
            for record in list(self.serviceRecords.values()):
                if record['inFlight'] or now < record['retryAt']:
                    continue
                sid = record['sid']
                if sid and record['receivedNotify'] and record['firstNotifyDeadline'] and now >= record['firstNotifyDeadline']:
                    if record['firstNotifyRetries'] == 0:
                        logger.warning('[subscription] first_notify_missing uuid=%s service=%s sid=%s', record['uuid'], record['service'], sid)
                        self._removeRecord(record)
                        record['sid'] = None
                        record['firstNotifyRetries'] = 1
                        actions.append((record, False))
                        continue
                    record['firstNotifyDeadline'] = 0
                    logger.error('[subscription] first_notify_still_missing uuid=%s service=%s sid=%s', record['uuid'], record['service'], sid)
                    continue
                if sid and record['expireAt'] <= now:
                    self._removeRecord(record)
                    record['sid'] = None
                    record['firstNotifyRetries'] = 0
                    actions.append((record, False))
                    continue
                if sid and now >= record['renewAt']:
                    actions.append((record, True))
                    continue
                if sid is None:
                    actions.append((record, False))
                None(None, None, None)
            with None:
                if not None:
                    pass
        for record, renew in actions:
            self._launchSubscription(record, renew)

    
    def unsubscribe(self, remoteIP, remotePort, service, sid):
        '''尽力注销远端 SID；参数为地址、端口、服务和 SID，返回无。'''
        headerFields = {
            'SID': sid }
    # WARNING: Decompyle incomplete

    
    def messageDistributeMethod(self, sid, message, seq = (None,)):
        '''按 SID 串行解析通知并记录 SEQ 诊断；参数为 SID、XML 和 SEQ，返回无。'''
        with self.observerDictLock:
            record = self.observerDict.get(sid)
            if record is None:
                now = time.monotonic()
                self.earlyNotifications = (lambda .0 = None: [ item for item in .0 if now - item[0] <= self.EARLY_NOTIFY_TTL ])(self.earlyNotifications)
                waiting = any((lambda .0: for item in .0:
if item['inFlight']:
passitem['sid'] is None)(self.serviceRecords.values()))
                if sid and waiting and len(self.earlyNotifications) < self.MAX_EARLY_NOTIFICATIONS:
                    self.earlyNotifications.append((now, sid, message, seq))
                    logger.debug('[subscription] early_notify_cached sid=%s seq=%s', sid, seq)
                else:
                    logger.error('[subscription] unknown_sid sid=%s', sid)
                None(None, None, None)
                return None
            None(None, None, None)
        with None:
            if not None:
                pass
        with self.notifyLock:
            with self.observerDictLock:
                if self.observerDict.get(sid) is not record:
                    pass
                None(None, None, None)
                None(None, None, None)
                return None
                generation = record['generation']
                record['receivedNotify'] = True
                record['firstNotifyDeadline'] = 0
                self._logSequence(record, seq)
                None(None, None, None)
            with None:
                if not None:
                    pass
            parser = LPBasicUPnPServiceParser.parserForService(record['service'])
            messageDict = parser.parse(message) if parser else None
            if messageDict is None:
                pass
            None(None, None, None)
            return None
            with self.observerDictLock:
                if self._isCurrent(record, generation) or self.observerDict.get(sid) is not record:
                    pass
                None(None, None, None)
                None(None, None, None)
                return None
                None(None, None, None)
            with None:
                if not None:
                    pass
            if self.notifyComeMethod:
                self.notifyComeMethod(record['uuid'], messageDict)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _takeEarlyNotifications(self, sid, now):
        '''取出指定 SID 的未过期提前通知；参数为 SID 和当前时间，返回通知列表。'''
        matched = []
        remaining = []
        for item in self.earlyNotifications:
            if now - item[0] > self.EARLY_NOTIFY_TTL:
                continue
            if item[1] == sid:
                matched.append(item)
                continue
            remaining.append(item)
        self.earlyNotifications = remaining
        return matched

    
    def _logSequence(self, record, seq):
        '''记录每个 SID 的 SEQ 异常但不阻断通知；参数为记录和 SEQ，返回无。'''
        pass
    # WARNING: Decompyle incomplete

    
    def hasObserverForUUID(self, uuid):
        '''检查设备三个服务是否都有未过期 SID；参数为 UUID，返回布尔值。'''
        with self.observerDictLock:
            now = time.monotonic()
            None(None, None, None)
            return None((lambda .0 = None: for service in .0:
if record = self.serviceRecords.get((uuid, service)) is not None and record['sid'] is not None:
passrecord['expireAt'] > nowself.serviceRecords.get((uuid, service)))(self.SERVICES))
            with None:
                if not None:
                    pass


if __name__ == '__main__':
    run_server()
