# Source Generated with Decompyle++
# File: LPMediaInfo.pyc (Python 3.9)

from enum import IntEnum
from urllib.parse import urlparse
import time
from LPClientFramework import LPUtility, LPPublicDefine

class LPLoopMode(IntEnum):
    listrepeat = (0,)
    singlerepeat = (1,)
    shuffle = (3,)
    repeatshuffle = (2,)
    default = (4,)
    singlerepeatshuffle = 5


class LPMediaInfo(object):
    '''维护设备当前媒体信息和播放能力状态。'''
    
    def __init__(self, ip):
        '''初始化媒体信息对象。

        :param ip: 当前设备 IP。
        :returns: None。
        '''
        self.reInit()
        self.ip = ip

    
    def _update(self, newInfo):
        '''增量更新设备媒体信息。

        :param newInfo: 本次设备通知携带的媒体字段。
        :returns: None。
        '''
        originalArtworkUri = self.artworkUri
        originalLocalArtworkUri = self.localArtworkUri
        if 'volume' in newInfo:
            self.volumeInitialized = True
        for key, value in newInfo.items():
            if hasattr(self, key):
                setattr(self, key, value)
            if key == 'ratingURI' and value and value != 'unknown':
                self.mediaType = LPPublicDefine.MEDIATYPE_STATION
                continue
                if self.playState == 'STOPPED':
                    self.duration = self.progress = '00:00:00'
        if not 'trackName' in newInfo:
            pass
        hasTrackMeta = 'artworkUri' in newInfo
        artworkUri = self._resolvedArtworkUri()
        if (originalArtworkUri != self.artworkUri and originalLocalArtworkUri != self.localArtworkUri or self.mediaType == 'AIRPLAY') and hasTrackMeta:
            if self._is_artwork_uri(artworkUri):
                self._loadArtwork(artworkUri)
            else:
                self.artworkImage = None
                self._clearArtworkRetry()
        self._maybeRetryArtwork(artworkUri)
        message = newInfo.get('message', None)
        self.lastMessage = message

    
    def _is_artwork_uri(artworkUri):
        '''判断封面地址是否是可直接请求的网络地址（http/https/smb）。

        :param artworkUri: 封面资源地址。
        :returns: 命中 http、https 或 smb:// 时返回 True。
        '''
        if not artworkUri:
            pass
        uri = str('').strip()
        if not uri.startswith('http://') and uri.startswith('https://'):
            pass
        return uri.startswith('smb://')

    _is_artwork_uri = staticmethod(_is_artwork_uri)
    
    def _resolvedArtworkUri(self):
        '''解析本次实际使用的封面地址，与 iOS MediaInfo 的选择顺序保持一致。

        优先用固件回带的 ``upnp:localAlbumArtURI``（设备自身 U 盘场景下指向设备 IP，可直接访问）；
        缺失时回退到 ``upnp:albumArtURI``，并修正指向本机的 127.0.0.1 地址。

        :param: 无。
        :returns: 可直接请求的封面地址；均无有效值时返回空字符串。
        '''
        if not self.localArtworkUri:
            pass
        localArtworkUri = str('').strip()
        if localArtworkUri.startswith('http'):
            return localArtworkUri
        if not self.artworkUri:
            pass
        return None._fixArtworkUriHost(str('').strip())

    
    def _fixArtworkUriHost(self, artworkUri):
        '''把指向 127.0.0.1 的封面地址换回设备 IP。

        设备播自身 U 盘时，固件回带的封面 host 是 127.0.0.1（设备视角的自身地址），
        PC 直接请求会打到本机而失败（对齐 iOS MediaInfo.m 的同样处理）。

        :param artworkUri: 原始封面地址。
        :returns: 修正后的封面地址；无需修正时原样返回。
        '''
        if not artworkUri:
            return artworkUri
        parsed = None(artworkUri)
        if not parsed.hostname != '127.0.0.1' or self.ip:
            return artworkUri
        netloc = None.ip
        if parsed.port:
            netloc = '%s:%d' % (self.ip, parsed.port)
        fixedUri = parsed._replace(netloc, **('netloc',)).geturl()
        logger = getattr(LPUtility, 'logger', None)
        if logger is not None:
            logger.debug('[MediaInfo] fix artwork host: %s -> %s' % (artworkUri, fixedUri))
        return fixedUri

    
    def _loadArtwork(self, artworkUri):
        '''按 trackSource 分支尝试加载封面，成功后更新封面并清除补拉状态，失败后记录补拉状态。

        :param artworkUri: 封面资源地址。
        :returns: None。
        '''
        domain = urlparse(artworkUri).netloc
        if self.trackSource == 'WiiMRadio':
            pixmap = LPUtility.getCachedPixmapWithUrl(artworkUri)
            if pixmap is None or pixmap.isNull():
                pixmap = LPUtility.getCachedPixmapWithUrl(artworkUri, 155)
            respDict = {
                'image': pixmap } if not pixmap is not None and pixmap.isNull() else { }
        elif self.trackSource == 'Plex':
            respDict = LPUtility.fetchUrlQPixmap(artworkUri, True, True, **('forceFetch',))
        else:
            respDict = LPUtility.fetchUrlQPixmap(artworkUri, domain == self.ip, True, **('privateDevice', 'forceFetch'))
        pixmap = respDict.get('image', None)
        if not pixmap is not None and pixmap.isNull():
            self.artworkImage = pixmap
            self._clearArtworkRetry()
        else:
            self.artworkImage = None
            response = respDict.get('response', None)
            if response is not None and response.status_code in (403, 404):
                self._clearArtworkRetry()
            else:
                self._recordArtworkRetry(artworkUri)

    
    def _recordArtworkRetry(self, artworkUri):
        '''记录封面加载失败状态，供后续通知自动补拉。

        :param artworkUri: 失败的封面资源地址。
        :returns: None。
        '''
        if self._artworkRetryUri != artworkUri:
            self._artworkRetryCount = 0
        self._artworkRetryUri = artworkUri
        self._artworkRetryFailedTime = time.time()

    
    def _clearArtworkRetry(self):
        '''清除封面补拉状态。

        :param: 无。
        :returns: None。
        '''
        self._artworkRetryUri = None
        self._artworkRetryFailedTime = 0
        self._artworkRetryCount = 0

    
    def _maybeRetryArtwork(self, artworkUri):
        '''封面加载失败达到重试间隔后自动补拉一次，最多自动补拉 2 次。

        :param artworkUri: 当前封面资源地址。
        :returns: None。
        '''
        if self._artworkRetryUri is None:
            return None
        if not None._is_artwork_uri(artworkUri):
            self._clearArtworkRetry()
            return None
        if None._artworkRetryUri != artworkUri:
            return None
        if None.time() - self._artworkRetryFailedTime < 5 or self._artworkRetryCount >= 2:
            return None
        None._artworkRetryCount += 1
        self._artworkRetryFailedTime = time.time()
        self._loadArtwork(artworkUri)

    
    def reInit(self):
        '''重置媒体信息到默认值。

        :param: 无。
        :returns: None。
        '''
        self.volume = 0
        self.volumeInitialized = False
        self.mute = False
        self.playState = None
        self.loopMode = None
        self.customUUID = None
        self.trackName = None
        self.trackId = None
        self.playUri = None
        self.artist = None
        self.artistId = None
        self.albumId = None
        self.album = None
        self.artworkUri = None
        self.localArtworkUri = None
        self.artworkImage = None
        self.mediaType = None
        self.trackSource = None
        self.duration = None
        self.progress = None
        self.quality = -1
        self.actualQuality = None
        self.trackRateHz = 0
        self.trackFormat = 0
        self.trackBitrate = 0
        self.lastMessage = None
        self.guiBehavior = None
        self.itemId = None
        self.itemName = None
        self.playOrigin = None
        self.playOriginTrackId = None
        self.playSection = None
        self._artworkRetryUri = None
        self._artworkRetryFailedTime = 0
        self._artworkRetryCount = 0

    
    def set(self, info):
        '''用新的媒体信息覆盖当前状态。

        :param info: 媒体信息字典。
        :returns: None。
        '''
        self.reInit()
        self._update(info)


