# Source Generated with Decompyle++
# File: LPLocalMusicPlayList.pyc (Python 3.9)

import datetime
from xml.sax.saxutils import escape
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayListSource, LPPlayItem

class LPLocalMusicPlayList(LPPlayMusicList):
    
    def __init__(self):
        LPPlayMusicList.__init__(self)

    
    def generateBackupQueueXML(self, musicArray, listName):
        '''
        <?xml version="1.0"?>
        <PlayList>
            <ListName>2013央视春晚_#~2025-04-09 10:25:48</ListName>
            <ListInfo>
                <TrackNumber>2</TrackNumber>
                <SourceName>UPnPServer</SourceName>
                <Radio>0</Radio>
                <Group_name>WiimuCustomList</Group_name>
                <TotalNumber>2</TotalNumber>
                <SearchUrl></SearchUrl>
            </ListInfo>
            <Tracks>
                <Track1>
                    <URL>http://192.168.188.21:8200/MediaItems/242.mp3</URL>
                    <Source>UPnPServer</Source>
                    <Id>1$7$22$0</Id>
                    <Metadata>&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;&lt;DIDL-Lite
                        xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot;
                        xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot;
                        xmlns:song=&quot;www.linkplay.com/song/&quot;
                        xmlns:custom=&quot;www.linkplay.com/custom/&quot;
                        xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;upnp:class&gt;object.item.audioItem.musicTrack&lt;/upnp:class&gt;&lt;item&gt;&lt;song:id&gt;1$7$22$0&lt;/song:id&gt;&lt;song:albumid&gt;&lt;/song:albumid&gt;&lt;song:singerid&gt;&lt;/song:singerid&gt;&lt;dc:title&gt;风吹麦浪&lt;/dc:title&gt;&lt;upnp:artist&gt;李健&lt;/upnp:artist&gt;&lt;upnp:album&gt;2013央视春晚&lt;/upnp:album&gt;&lt;res protocolInfo=&quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&quot; duration=&quot;0&quot;&gt;http://192.168.188.21:8200/MediaItems/242.mp3&lt;/res&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;
                    </Metadata>
                </Track1>
                <Track2>
                    <URL>http://192.168.188.21:8200/MediaItems/246.dat</URL>
                    <Source>UPnPServer</Source>
                    <Id>1$7$22$1</Id>
                    <Metadata>&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;&lt;DIDL-Lite
                        xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot;
                        xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot;
                        xmlns:song=&quot;www.linkplay.com/song/&quot;
                        xmlns:custom=&quot;www.linkplay.com/custom/&quot;
                        xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;upnp:class&gt;object.item.audioItem.musicTrack&lt;/upnp:class&gt;&lt;item&gt;&lt;song:id&gt;1$7$22$1&lt;/song:id&gt;&lt;song:albumid&gt;&lt;/song:albumid&gt;&lt;song:singerid&gt;&lt;/song:singerid&gt;&lt;dc:title&gt;风吹麦浪&lt;/dc:title&gt;&lt;upnp:artist&gt;李健&lt;/upnp:artist&gt;&lt;upnp:album&gt;2013央视春晚&lt;/upnp:album&gt;&lt;res protocolInfo=&quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&quot; duration=&quot;0&quot;&gt;http://192.168.188.21:8200/MediaItems/246.dat&lt;/res&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;
                    </Metadata>
                </Track2>
            </Tracks>
        </PlayList>
        '''
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(listName)
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<TrackNumber>%d</TrackNumber>' % len(musicArray)
        xmlStr += '<TotalNumber>%d</TotalNumber>' % len(musicArray)
        xmlStr += '<Group_name>WiimuCustomList</Group_name>'
        xmlStr += '<Radio>%s</Radio>' % '0'
        if not self.header.searchUrl:
            pass
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape('')
        xmlStr += '<ContentType>songlist</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
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

    
    def generateSetKeyMappingXML(self, name):
        xmlStr = '<Name>%s</Name>' % escape(name)
        xmlStr += '<Source>%s</Source>' % self.header.mediaSource
        xmlStr += '<ContentType>songlist</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
        xmlStr += '<RoutineId>Empty</RoutineId>'
        xmlStr += '<Loop>1</Loop>'
        xmlStr += '<Shuffle>1</Shuffle>'
        return xmlStr



class LPLocalMusicPlayHeader(LPPlayHeader):
    
    def __init__(self):
        LPPlayHeader.__init__(self)
        self.mediaSource = LPPlayListSource.LocalMusic.value



class LPLocalMusicPlayItem(LPPlayItem):
    
    def __init__(self):
        LPPlayItem.__init__(self)
        self.date = None
        self.localPath = None
        self.trackNumber = 0
        self.trackSource = LPPlayListSource.LocalMusic.value
        self.customUUID = None
        self.bitrate = 0
        self.samplerate = 0
        self.channels = 0
        self.albumartist = None


