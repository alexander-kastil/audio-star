# Source Generated with Decompyle++
# File: LPQueueManager.pyc (Python 3.9)

import time
from enum import Enum
from operator import index
from threading import Thread
from cherrypy import response
import LPGlobalUI
from LPClientFramework import LPUtility, LPPublicDefine
from LPClientFramework.LPPlayList.LPLocalMusicPlayList import LPLocalMusicPlayList, LPLocalMusicPlayHeader
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayListSource
from LPClientFramework.LPUtility import logger
from LPGlobalUI import currentDevice
queueSpecialMediaType = [
    LPPublicDefine.MEDIATYPE_RADIO,
    LPPublicDefine.MEDIATYPE_STATION,
    LPPublicDefine.MEDIATYPE_SPOTIFY,
    LPPublicDefine.MEDIATYPE_TIDAL_CONNECT,
    LPPublicDefine.MEDIATYPE_ROON,
    LPPublicDefine.MEDIATYPE_CHROME_CAST]

def isQueueSupportedMediaType(mediaType):
    '''
    判断当前媒体类型是否支持队列。
    '''
    return mediaType not in queueSpecialMediaType


class LPQueueState(Enum):
    queueReady = 0
    queueNotReady = 1
    sourceNotSupportQueue = 2
    queueEmpty = 3


class LPAppendToQueueAllowEnum(Enum):
    LP_AppendToQueue_allow = 0
    LP_AppendToQueue_forbidden_exceed = 1
    LP_AppendToQueue_forbidden_queue = 2


class LPQueueManager(object):
    
    def __init__(self, device):
        self.device = device
        self.playList = None
        self.version = None
        self.checkSum = ''
        self.lastMediaType = getattr(device.mediaInfo, 'mediaType', None)
        self.lastTrackSource = getattr(device.mediaInfo, 'trackSource', None)
        self.needsQueueRefresh = False

    
    def status(self):
        mediaType = self.device.mediaInfo.mediaType
        source = self.device.mediaInfo.trackSource
        if not mediaType or source:
            return LPQueueState.queueEmpty
        if not None(mediaType):
            return LPQueueState.sourceNotSupportQueue
        if None.playList is None:
            return LPQueueState.queueNotReady
        return None.queueReady

    status = property(status)
    
    def _update(self, mediaInfo):
        if 'mediaType' in mediaInfo or 'trackSource' in mediaInfo:
            mediaType = mediaInfo.get('mediaType', self.device.mediaInfo.mediaType)
            trackSource = mediaInfo.get('trackSource', self.device.mediaInfo.trackSource)
            if not mediaType != self.lastMediaType:
                pass
            mediaChanged = trackSource != self.lastTrackSource
            if mediaChanged:
                self.playList = None
                self.version = None
                self.checkSum = ''
                if mediaType and trackSource:
                    pass
                self.needsQueueRefresh = bool(isQueueSupportedMediaType(mediaType))
                self.lastMediaType = mediaType
                self.lastTrackSource = trackSource
        lastPlayIndex = mediaInfo.get('lastPlayIndex', None)
        if lastPlayIndex is not None and self.playList is not None:
            self.playList.index = lastPlayIndex - 1
            LPUtility.triggerDeviceInfoUpdate(self.device, 'queue')

    
    def requestQueue(self):
        self.needsQueueRefresh = False
        
        def callback(response = None):
            if response is None:
                LPUtility.triggerDeviceInfoUpdate(self.device, 'queue')
                return None
            self.playList = None.get('musicList', None)
            self.version = response.get('version', None)
            LPUtility.triggerDeviceInfoUpdate(self.device, 'queue')
            logger.debug('%s queue changed' % self.device.name)

        self.device.asyncUpnpPost('BrowseQueue', {
            'QueueName': 'CurrentQueue' }, callback)
        return self.playList

    
    def add_to_next(self, play_item, finished_method):
        '''
        添加一首到队列，为下一首
        :param play_item:
        :param finished_method:
        :return:
        '''
        
        def _async_add(play_item = None, finished_method = None):
            response = None
            if not self.isPlayingSpecialSource() or self.isPlayingWiFiContent():
                play_list = LPLocalMusicPlayList()
                header = LPLocalMusicPlayHeader()
                header.headTitle = 'MyMusic Track'
                play_list.header = header
                play_list.list.append(play_item)
                xml = play_list.generateXML([
                    play_item], '1')
                response = self.device.upnpPost('CreateQueue', {
                    'QueueContext': xml })
            else:
                last_play_index = self.playList.index
                if last_play_index is not None:
                    xml = self.playList.generateXML([
                        play_item])
                    response = self.device.upnpPost('AppendTracksInQueueEx', {
                        'QueueContext': xml,
                        'Direction': '1',
                        'StartIndex': str(last_play_index + 1) })
            if response.get('error'):
                if finished_method:
                    finished_method(False)
                return None

        t = Thread(_async_add, (play_item, finished_method), **('target', 'args'))
        t.start()

    
    def add_to_last(self, play_item, finished_method):
        '''
        添加到队列，当前播放的后面
        :param play_item:
        :param finished_method:
        :return:
        '''
        
        def _async_add(play_item = None, finished_method = None):
            response = None
            if not self.isPlayingSpecialSource() or self.isPlayingWiFiContent():
                play_list = LPLocalMusicPlayList()
                header = LPLocalMusicPlayHeader()
                header.headTitle = 'MyMusic Track'
                play_list.header = header
                play_list.list.append(play_item)
                xml = play_list.generateXML([
                    play_item], '1')
                response = self.device.upnpPost('CreateQueue', {
                    'QueueContext': xml })
            else:
                last_item_index = len(self.playList.list) - 1
                if last_item_index is not None:
                    xml = self.playList.generateXML([
                        play_item])
                    response = self.device.upnpPost('AppendTracksInQueueEx', {
                        'QueueContext': xml,
                        'Direction': '1',
                        'StartIndex': str(last_item_index + 1) })
            if response.get('error'):
                if finished_method:
                    finished_method(False)
                return None

        t = Thread(_async_add, (play_item, finished_method), **('target', 'args'))
        t.start()

    
    def isPlayingWiFiContent(self):
        media_info = LPGlobalUI.currentDevice.mediaInfo
        if media_info.trackName or media_info.artist:
            return True
        if None.playState and media_info.playState != 'STOPPED' and media_info.playState != 'NO_MEDIA_PRESENT':
            return True

    
    def isPlayingSpecialSource(self):
        return LPGlobalUI.currentDevice.mediaInfo.mediaType in (LPPublicDefine.MEDIATYPE_LINEIN, LPPublicDefine.MEDIATYPE_BLUETOOTH, LPPublicDefine.MEDIATYPE_EXTERNAL_USB, 'USB_DAC', LPPublicDefine.MEDIATYPE_EXTERNAL_TF, LPPublicDefine.MEDIATYPE_OPTICAL, LPPublicDefine.MEDIATYPE_OPTICAL2, LPPublicDefine.MEDIATYPE_AIRPLAY, LPPublicDefine.MEDIATYPE_CO_AXIAL, LPPublicDefine.MEDIATYPE_CO_AXIAL2, LPPublicDefine.MEDIATYPE_HDMI, 'TV', LPPublicDefine.MEDIATYPE_PHONO)

    
    def canAppendToQueue(self, source):
        media_info = LPGlobalUI.currentDevice.mediaInfo
        if self.isPlayingWiFiContent() or self.isPlayingSpecialSource():
            return LPAppendToQueueAllowEnum.LP_AppendToQueue_allow
        if None not in media_info.mediaType:
            return LPAppendToQueueAllowEnum.LP_AppendToQueue_forbidden_queue
        if None and media_info.trackSource != source:
            return LPAppendToQueueAllowEnum.LP_AppendToQueue_forbidden_queue
        return None.LP_AppendToQueue_allow

    
    def delete_from_queue(self, index, action_key, finished_method):
        
        def _asyncOperate(index, action_key, finished_method):
            if not LPGlobalUI.currentDevice:
                logger.debug('delete_from_queue no device !')
                return None
            response = None.currentDevice.upnpPost('RemoveTracksInQueue', {
                'QueueName': 'CurrentQueue',
                'RangStart': str(index),
                'RangEnd': str(index) })
            if response.get('status_code') == 200:
                finished_method(action_key, True)

        t = Thread(_asyncOperate, (index, action_key, finished_method), **('target', 'args'))
        t.start()

    
    def deleteFromQueue(self, row, callback = (None,)):
        
        def _asyncOperate(row, callback):
            response = LPGlobalUI.currentDevice.upnpPost('RemoveTracksInQueue', {
                'QueueName': 'CurrentQueue',
                'RangStart': str(row + 1),
                'RangEnd': str(row + 1) })
            result = response.get('status_code') == 200
            if callback:
                callback(result)

        t = Thread(_asyncOperate, (row, callback), **('target', 'args'))
        t.start()

    
    def get_queue_index(self, result_queue):
        
        def _asyncOperate(result_queue):
            if not LPGlobalUI.currentDevice:
                logger.debug('get_queue_index no device !')
                return None
            response = None.currentDevice.upnpPost('GetQueueIndex', {
                'QueueName': 'CurrentQueue' })
            result_queue.put(response)

        t = Thread(_asyncOperate, (result_queue,), **('target', 'args'))
        t.start()


