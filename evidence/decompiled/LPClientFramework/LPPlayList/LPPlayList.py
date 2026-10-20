# Source Generated with Decompyle++
# File: LPPlayList.pyc (Python 3.9)

from enum import Enum
from pathlib import Path
from xml.sax.saxutils import escape
from LPClientFramework import LPUtility
from LPClientFramework.LPUtility import logger

class LPPlayListSource(Enum):
    UPnPServer = 'UPnPServer'
    LocalMusic = 'PC_RemoteLocal'
    RadioParadise2 = 'RadioParadise2'
    WiiMRadio = 'WiiMRadio'
    TuneIn = 'newTuneIn'
    Qobuz = 'Qobuz'
    Tidal = 'Tidal'
    Soundtrack = 'Soundtrack'


class LPHeaderType(Enum):
    LP_HEADER_TYPE_COLLECTION = (0,)
    LP_HEADER_TYPE_PLAYLIST = (1,)
    LP_HEADER_TYPE_ALBUM = (2,)
    LP_HEADER_TYPE_ARTIST = (3,)
    LP_HEADER_TYPE_STATION = (4,)
    LP_HEADER_TYPE_SONG = (5,)
    LP_HEADER_TYPE_PODCAST = (6,)
    LP_HEADER_TYPE_SHOW = (7,)
    LP_HEADER_TYPE_EPISODE = 8


def _normalizeHeaderTypeScalarValue(headType):
    '''
    把 LPHeaderType 或其落盘后的值归一成基础值。

    Args:
        headType: 枚举、tuple、数字或其他基础值。

    Returns:
        便于存储和比较的基础值。
    '''
    if hasattr(headType, 'value'):
        headType = headType.value
    if isinstance(headType, tuple) and len(headType) == 1:
        return headType[0]

LP_HEADER_TYPE_VALUE_MAP = (lambda .0: pass# WARNING: Decompyle incomplete
)(LPHeaderType)
LP_HEADER_TYPE_ENUM_MAP = (lambda .0: pass# WARNING: Decompyle incomplete
)(LP_HEADER_TYPE_VALUE_MAP.items())

def headerTypeValue(headType):
    '''
    获取 LPHeaderType 对应的基础值。

    Args:
        headType: LPHeaderType 枚举或其序列化后的值。

    Returns:
        可落盘、可比较的基础值。
    '''
    return _normalizeHeaderTypeScalarValue(headType)


def headerTypeEnum(headType):
    '''
    把基础值还原成 LPHeaderType 枚举。

    Args:
        headType: LPHeaderType 枚举、tuple、数字或字符串值。

    Returns:
        能识别时返回 LPHeaderType，否则原样返回。
    '''
    normalizedValue = _normalizeHeaderTypeScalarValue(headType)
    return LP_HEADER_TYPE_ENUM_MAP.get(normalizedValue, headType)


class LPPlayMusicList(object):
    
    def __init__(self):
        self.account = None
        self.header = None
        self.list = []
        self.index = 0

    
    def generateXML(self, musicArray, startPlayIndex = (None,)):
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(self.header.headTitle if self.header.headTitle else '')
        xmlStr += '<ListInfo>'
        xmlStr += '<Radio>%s</Radio>' % '0'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<TrackNumber>%d</TrackNumber>' % len(musicArray)
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape(self.header.searchUrl if self.header.searchUrl else '')
        xmlStr += '<Quality>0</Quality>'
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(self.header.imageUrl if self.header.imageUrl else '')
        xmlStr += '<StartPlayIndex>%s</StartPlayIndex>' % escape(startPlayIndex if startPlayIndex else '')
        xmlStr += '</ListInfo>'
        xmlStr += '<Tracks>'
        for index in range(len(musicArray)):
            trackItem = musicArray[index]
            xmlStr += '<Track%d>' % (index + 1)
            xmlStr += '<URL>%s</URL>' % escape(trackItem.trackUrl if trackItem.trackUrl else '')
            xmlStr += '<Source>%s</Source>' % self.header.mediaSource
            xmlStr += '<Id>%s</Id>' % escape(trackItem.trackId if trackItem.trackId else '')
            xmlStr += '<Metadata>'
            metaData = '<?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.linkplay.com/song/" xmlns:custom="www.linkplay.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item>'
            if self.header.mediaSource == LPPlayListSource.LocalMusic.value:
                metaData += '<custom:uuid>%s</custom:uuid>' % LPUtility.pcUUID()
            metaData += '<song:id>%s</song:id>' % trackItem.trackId
            metaData += '<song:albumid>%s</song:albumid>' % trackItem.albumId
            metaData += '<song:singerid>%s</song:singerid>' % trackItem.artistId
            metaData += '<dc:title>%s</dc:title>' % escape(trackItem.trackName if trackItem.trackName else '')
            metaData += '<upnp:artist>%s</upnp:artist>' % escape(trackItem.trackArtist if trackItem.trackArtist else '')
            metaData += '<upnp:album>%s</upnp:album>' % escape(trackItem.albumName if trackItem.albumName else '')
            metaData += '<res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="%d">%s</res>' % (trackItem.trackDuration, escape(trackItem.trackUrl if trackItem.trackUrl else ''))
            metaData += '<upnp:albumArtURI>%s</upnp:albumArtURI>' % escape(trackItem.trackImage if trackItem.trackImage else '')
            metaData += '</item></DIDL-Lite>'
            xmlStr += escape(metaData)
            xmlStr += '</Metadata></Track%d>' % (index + 1)
        xmlStr += '</Tracks></PlayList>'
        return xmlStr

    
    def getPicUrl(self):
        if self.header.imageUrl:
            return self.header.imageUrl
        if None.list and self.list[0].trackImage:
            return self.list[0].trackImage



class LPAccount(object):
    
    def __init__(self):
        self.source = None
        self.userId = None
        self.userName = None
        self.userPassword = None
        self.token = None
        self.refreshToken = None
        self.expressIn = None
        self.update = None
        self.showName = None

    
    def getCacheDir(self):
        pass
    # WARNING: Decompyle incomplete



class LPPlayHeader(object):
    
    def __init__(self):
        self.headTitle = None
        self.headId = None
        self.playOrigin = None
        self.mediaType = None
        self.headType = 0
        self.mediaSource = None
        self.searchUrl = None
        self.loopMode = None
        self.creator = None
        self.quality = None
        self.imageUrl = None
        self.totalTracks = None
        self.describe = None
        self.totalPage = None
        self.currentPage = None
        self.perPage = None



class LPPlayItem(object):
    
    def __init__(self):
        self.trackSource = None
        self.trackName = None
        self.trackId = None
        self.trackUrl = None
        self.trackImage = None
        self.trackArtist = None
        self.artistId = None
        self.trackSize = None
        self.trackDuration = 0
        self.playCount = None
        self.albumName = None
        self.albumId = None
        self.createTime = None


