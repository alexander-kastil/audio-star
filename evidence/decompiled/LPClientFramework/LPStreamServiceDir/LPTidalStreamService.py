# Source Generated with Decompyle++
# File: LPTidalStreamService.pyc (Python 3.9)

'''
TIDAL 音源服务。
'''
import json
import time
from typing import Any, Dict, Optional, Type
from bs4 import BeautifulSoup
import LPGlobalUI
from LPClientFramework import LPPublicDefine, LPUtility
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPMusicLibrary import LPRecentlyManager, LPRecentlyPlayListCodec
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType, LPPlayHeader, LPPlayItem, LPPlayListSource
from LPClientFramework.LPPlayList.LPTidalPlayList import LPTidalAccount, LPTidalPlayHeader, LPTidalPlayItem, LPTidalPlayList, TIDAL_RECENTLY_NAVIGATION_SEE_ALL, tidalPlayingContextForPlaylist, tidalRecentlyNavigationType, tidalRecentlySeeAllSectionKey
from LPClientFramework.LPStreamServiceManager import LPStreamService
from LPClientFramework.LPUtility import logger
from LPClientFramework.util.aes import AESCipher
FAVORITE_RESYNC_PENDING_GRACE_SECONDS = 3

class LPTidalStreamService(LPStreamService):
    '''TIDAL 音源服务，负责设备账号注册、登出和账号变化通知处理。'''
    _prefixedDetailNavigationId = True
    
    def _metadataText(metaDataObj = None, *names):
        '''
        从 metadata XML 中读取第一个非空字段。

        :param metaDataObj: BeautifulSoup 解析后的 metadata XML。
        :param names: 候选字段名，按优先级依次尝试。
        :return: 第一个非空字段文本；没有匹配时返回空字符串。
        '''
        for name in names:
            element = metaDataObj.find(name, None)
            if element and element.text is not None:
                return str(element.text)
            return ''

    _metadataText = None(_metadataText)
    
    def _durationSeconds(value = None):
        '''
        将队列 metadata 中的 duration 转成秒数。

        :param value: 原始 duration，可能是秒数字符串或 HH:MM:SS。
        :return: 秒数；无法解析时返回 0。
        '''
        if not value:
            pass
        raw_value = str('').strip()
        if not raw_value:
            return 0
    # WARNING: Decompyle incomplete

    _durationSeconds = None(_durationSeconds)
    
    def _buildCurrentPlayItem(self = None, device = None, sourcePlayItem = None):
        '''
        构造 minibar More 使用的 TIDAL 当前播放项。

        :param device: 当前播放设备。
        :param sourcePlayItem: 当前队列中匹配到的原始播放项。
        :return: 补齐后的 TIDAL 播放项；没有设备媒体信息时返回 None。
        '''
        media = getattr(device, 'mediaInfo', None) if device is not None else None
        if media is None and sourcePlayItem is None:
            return None
        play_item = None()
        if sourcePlayItem is not None:
            if not getattr(sourcePlayItem, 'trackSource', None):
                pass
            play_item.trackSource = self.source
            play_item.trackName = getattr(sourcePlayItem, 'trackName', None)
            play_item.trackId = getattr(sourcePlayItem, 'trackId', None)
            play_item.trackUrl = getattr(sourcePlayItem, 'trackUrl', None)
            play_item.trackImage = getattr(sourcePlayItem, 'trackImage', None)
            play_item.trackArtist = getattr(sourcePlayItem, 'trackArtist', None)
            play_item.artistId = getattr(sourcePlayItem, 'artistId', None)
            play_item.trackDuration = getattr(sourcePlayItem, 'trackDuration', 0)
            play_item.albumName = getattr(sourcePlayItem, 'albumName', None)
            play_item.albumId = getattr(sourcePlayItem, 'albumId', None)
            play_item.searchUrl = getattr(sourcePlayItem, 'searchUrl', '')
            play_item.startIndex = getattr(sourcePlayItem, 'startIndex', 0)
            play_item.isExplicit = getattr(sourcePlayItem, 'isExplicit', False)
            play_item.allowStreaming = getattr(sourcePlayItem, 'allowStreaming', True)
        if media is not None:
            if not play_