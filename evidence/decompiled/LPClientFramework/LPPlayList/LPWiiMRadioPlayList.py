# Source Generated with Decompyle++
# File: LPWiiMRadioPlayList.pyc (Python 3.9)

'''
WiiMRadio 播放列表模型与 XML 生成器。
'''
from html import escape
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayItem, LPPlayListSource

class LPWiiMRadioPlayList(LPPlayMusicList):
    '''WiiMRadio 播放列表，生成设备可识别的 XML 指令。'''
    
    def generateXML(self = None):
        '''
        生成 WiiMRadio 单电台播放 XML。

        XML 格式（Track Metadata 内容需 HTML-encode 后嵌入）：
            <?xml version="1.0"?>
            <PlayList>
                <ListName>电台名</ListName>
                <ListInfo>
                    <Radio>1</Radio>
                    <ContentType>radio</ContentType>
                    <SourceName>WiiMRadio</SourceName>
                    <PicUrl>封面地址</PicUrl>
                    <TrackNumber>1</TrackNumber>
                    <SearchUrl></SearchUrl>
                </ListInfo>
                <Tracks>
                    <Track1>
                        <URL>流地址</URL>
                        <Source>WiiMRadio</Source>
                        <Id>电台ID</Id>
                        <Metadata>（encoded DIDL-Lite）</Metadata>
                    </Track1>
                </Tracks>
            </PlayList>

        :return: XML 字符串。
        '''
        header = self.header
        if not self.list:
            pass
        items = []
        track_count = len(items)
        xml = '<?xml version="1.0"?><PlayList>'
        if not header.headTitle:
            pass
        xml += '<ListName>%s</ListName>' % escape('')
        xml += '<ListInfo>'
        xml += '<Radio>1</Radio>'
        xml += '<ContentType>radio</ContentType>'
        xml += '<SourceName>%s</SourceName>' % header.mediaSource
        if not header.headTitle:
            pass
        xml += '<ShowName>%s</ShowName>' % escape('')
        if len(items):
            pass
        elif not '':
            pass
        escape += items[0].trackId % ''('')
        xml += '<StreamType>radio</StreamType>'
        if not header.imageUrl:
            pass
        xml += '<PicUrl>%s</PicUrl>' % escape('')
        xml += '<TrackNumber>%d</TrackNumber>' % track_count
        xml += '<SearchUrl></SearchUrl>'
        xml += '</ListInfo>'
        xml += '<Tracks>'
        for idx, item in enumerate(items, 1, **('start',)):
            metadata = self._build_didl_metadata(item)
            xml += '<Track%d>' % idx
            if not item.trackUrl:
                pass
            xml += '<URL>%s</URL>' % escape('')
            xml += '<Source>%s</Source>' % header.mediaSource
            if not item.trackId:
                pass
            xml += '<Id>%s</Id>' % escape('')
            xml += '<Metadata>%s</Metadata>' % escape(metadata)
            xml += '</Track%d>' % idx
        xml += '</Tracks></PlayList>'
        return xml

    
    def _build_didl_metadata(item = None):
        '''
        构建单个 Track 的 DIDL-Lite Metadata 字符串（未 encode，由调用方 escape）。

        :param item: WiiMRadio 播放条目。
        :return: DIDL-Lite XML 字符串。
        '''
        meta = '<?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.linkplay.com/song/" xmlns:custom="www.linkplay.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class>'
        if not item.trackId:
            pass
        item_id = escape('')
        if not getattr(item, 'itemName', None) and item.trackName:
            pass
        item_name = escape('')
        meta += '<item id="%s" name="%s">' % (item_id, item_name)
        if not item.trackId:
            pass
        meta += '<song:id>%s</song:id>' % escape('')
        meta += '<song:albumid></song:albumid>'
        meta += '<song:singerid></song:singerid>'
        if not item.trackName:
            pass
        meta += '<dc:title>%s</dc:title>' % escape('')
        meta += '<upnp:artist></upnp:artist>'
        meta += '<upnp:album></upnp:album>'
        meta += '<res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="0"></res>'
        if not item.trackImage:
            pass
        meta += '<upnp:albumArtURI>%s</upnp:albumArtURI>' % escape('')
        meta += '</item></DIDL-Lite>'
        return meta

    _build_didl_metadata = None(_build_didl_metadata)


class LPWiiMRadioPlayHeader(LPPlayHeader):
    '''WiiMRadio 播放列表头信息。'''
    
    def __init__(self = None):
        super().__init__()
        self.mediaSource = LPPlayListSource.WiiMRadio.value

    __classcell__ = None


class LPWiiMRadioPlayItem(LPPlayItem):
    '''WiiMRadio 单个电台播放条目。'''
    
    def __init__(self = None):
        super().__init__()
        self.trackSource = LPPlayListSource.WiiMRadio.value
        self.itemName = None

    __classcell__ = None

