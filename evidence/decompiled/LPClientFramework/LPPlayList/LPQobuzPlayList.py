# Source Generated with Decompyle++
# File: LPQobuzPlayList.pyc (Python 3.9)

'''
@Time ： 2025/6/6 13:42
@Auth ： Chris
@File ：LPQobuzPlayList.py
@Desc:
'''
import datetime
import threading
from html import escape
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayListSource, LPPlayItem, LPAccount

class LPQobuzLibPageState:
    
    def __init__(self, limit, updating = (500, False)):
        self.limit = limit
        self.total = 16777215
        self.offset = 0
        self.updating = updating
        self.needRefresh = False

    
    def resetPageState(self, limit = (500,)):
        self.limit = limit
        self.total = 16777215
        self.offset = 0



class LPQobuzAccount(LPAccount):
    
    def __init__(self = None):
        super().__init__()
        self.source = LPPlayListSource.Qobuz.value
        self.email = None
        self.subscription = None
        self.maxStreaming = 2
        self.userStreaming = None
        self.dataBinding = {
            'My Playlists': {
                'playList': None,
                'pageState': LPQobuzLibPageState(),
                'loaded': False,
                'lock': threading.Lock() },
            'Favorite Artists': {
                'playList': None,
                'pageState': LPQobuzLibPageState(),
                'loaded': False,
                'lock': threading.Lock() },
            'Favorite Albums': {
                'playList': None,
                'pageState': LPQobuzLibPageState(),
                'loaded': False,
                'lock': threading.Lock() },
            'Favorite Tracks': {
                'playList': None,
                'pageState': LPQobuzLibPageState(50),
                'loaded': False,
                'lock': threading.Lock() },
            'Purchased Albums': {
                'playList': None,
                'pageState': LPQobuzLibPageState(),
                'loaded': False,
                'lock': threading.Lock() },
            'Purchased Tracks': {
                'playList': None,
                'pageState': LPQobuzLibPageState(50),
                'loaded': False,
                'lock': threading.Lock() } }

    __classcell__ = None


class LPQobuzPlayList(LPPlayMusicList):
    
    def __init__(self = None):
        super().__init__()
        self.qualityMap = {
            1: '5',
            2: '6',
            3: '7',
            4: '27' }

    
    def generateXML(self, startPlayIndex, playSection = (None, None)):
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(self.header.headTitle if self.header.headTitle else '')
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape(self.header.searchUrl if self.header.searchUrl else '')
        xmlStr += '<ContentType>songlist</ContentType>'
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(self.header.imageUrl if self.header.imageUrl else '')
        xmlStr += '<StartPlayIndex>%s</StartPlayIndex>' % escape(startPlayIndex if startPlayIndex else '')
        xmlStr += '<PlaySection>%s</PlaySection>' % escape(playSection if playSection else '')
        xmlStr += '<requestQuality>%s</requestQuality>' % self.getRequestQualityStr()
        xmlStr += '<EnableReplayGain>1</EnableReplayGain>'
        xmlStr += '<ReplayGainType>%s</ReplayGainType>' % self.getReplayGainType()
        xmlStr += '</ListInfo>'
        xmlStr += '</PlayList>'
        return xmlStr

    
    def generateTrackPlayXML(self, musicArray, startPlayIndex = (None,)):
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(self.header.headTitle if self.header.headTitle else 'Qobuz')
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<ContentType>songlist</ContentType>'
        xmlStr += '<TrackNumber>%d</TrackNumber>' % len(musicArray)
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(self.header.imageUrl if self.header.imageUrl else '')
        xmlStr += '<StartPlayIndex>%s</StartPlayIndex>' % escape(startPlayIndex if startPlayIndex else '')
        xmlStr += '<requestQuality>%s</requestQuality>' % self.getRequestQualityStr()
        xmlStr += '<EnableReplayGain>1</EnableReplayGain>'
        xmlStr += '<ReplayGainType>%s</ReplayGainType>' % self.getReplayGainType()
        xmlStr += '</ListInfo>'
        xmlStr += '<Tracks>'
        for index in range(len(musicArray)):
            trackItem = musicArray[index]
            xmlStr += '<Track%d>' % (index + 1)
            xmlStr += '<URL>wiimu_search://%s</URL>' % escape(str(trackItem.trackId) if trackItem.trackId else '')
            xmlStr += '<Source>%s</Source>' % self.header.mediaSource
            xmlStr += '<Id>%s</Id>' % escape(str(trackItem.trackId) if trackItem.trackId else '')
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

    
    def getRequestQualityStr(self):
        settings = LPUtility.settings
        LPQobuzManager = LPQobuzManager
        import LPClientFramework.LPMSManager.Qobuz.LPQobuzManager
        qobuz = LPQobuzManager.instance()
        account = qobuz.loginMgr.account
        if not account:
            return None
        userId = None.userId
        settings.beginGroup(f'''{LPPlayListSource.Qobuz.value}/{userId}''')
        quality = settings.value('quality', None)
        settings.endGroup()
        if not quality:
            quality = 2
        qualityStr = self.qualityMap.get(quality, '')
        return qualityStr

    
    def getReplayGainType(self):
        settings = LPUtility.settings
        LPQobuzManager = LPQobuzManager
        import LPClientFramework.LPMSManager.Qobuz.LPQobuzManager
        qobuz = LPQobuzManager.instance()
        account = qobuz.loginMgr.account
        if not account:
            return None
        userId = None.userId
        settings.beginGroup(f'''{LPPlayListSource.Qobuz.value}/{userId}''')
        replayGain = settings.value('replayGain', None)
        settings.endGroup()
        if replayGain is None:
            replayGain = 1
        return replayGain

    
    def generateBackupQueueXML(self, listName, playSection = (None,)):
        '''
        <?xml version="1.0"?>
        <PlayList>
            <ListName>RP Rock Mix_#~2025-04-01 11:27:20</ListName>
            <ListInfo>
                <SourceName>RadioParadise2</SourceName>
                <SearchUrl>https://api.radioparadise.com/api/gapless?chan=2&amp;bitrate=4&amp;C_user_id=1257664614&amp;player_id=FF98F7F4BBB1646CE0AC7A30</SearchUrl>
                <PicUrl>https://img.radioparadise.com/covers/l/B000002UBB.jpg</PicUrl>
                <Login_username></Login_username>
            </ListInfo>
        </PlayList>
        '''
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(listName)
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        if not self.header.searchUrl:
            pass
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape('')
        xmlStr += '<ContentType>songlist</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
        xmlStr += '<PlaySection>%s</PlaySection>' % escape(playSection if playSection else '')
        xmlStr += '<Login_username></Login_username>'
        xmlStr += '</ListInfo>'
        xmlStr += '</PlayList>'
        return xmlStr

    
    def generateSetKeyMappingXML(self, name):
        xmlStr = '<Name>%s</Name>' % escape(name)
        xmlStr += '<Source>%s</Source>' % self.header.mediaSource
        xmlStr += '<ContentType>songlist</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
        xmlStr += '<RoutineId>Empty</RoutineId>'
        xmlStr += '<Loop>0</Loop>'
        xmlStr += '<Shuffle>0</Shuffle>'
        return xmlStr

    __classcell__ = None

HeadTitle_Weekly_Q = 'My Weekly Q'
HeadTitle_Favorite_Tracks = 'Qobuz Favorite Tracks'
HeadTitle_Purchased_Tracks = 'Qobuz Purchased Tracks'
RECENTLY_FAVORITE_TRACKS_ID = 'qobuzFavoriteTracks'
RECENTLY_PURCHASED_TRACKS_ID = 'qobuzPurchasedTracks'

class LPQobuzPlayHeader(LPPlayHeader):
    
    def __init__(self = None):
        super().__init__()
        self.mediaSource = LPPlayListSource.Qobuz.value
        self.duration = 0
        self.qualityStr = None
        self.hires = False
        self.total = 0
        self.limit = 0
        self.offset = 0
        self.searchQueryText = None
        self.descText = None
        self.weeklyQBaseline = None
        self.mediaCount = None
        self.date = None
        self.trackArtist = None
        self.parentalWarning = False
        self.label = False
        self.trackOwner = None
        self.ownerId = None
        self.isPublic = True
        self.graphics = { }
        self.recentlyNavigateId = None
        self.recentlyPlaylistTrackImage = None
        self.recentlyPlaylistImageList = None
        self.recentlyIsUserPlaylist = False

    __classcell__ = None


class LPQobuzPlayItem(LPPlayItem):
    
    def __init__(self = None):
        super().__init__()
        self.searchUrl = None
        self.startIndex = None
        self.date = None
        self.trackVersion = None
        self.trackNumber = 0
        self.trackSource = LPPlayListSource.Qobuz.value
        self.customUUID = None
        self.bitrate = 0
        self.samplerate = 0
        self.trackOwner = None
        self.ownerId = None
        self.genreObjArr = []
        self.genrePath = []
        self.isPublic = True
        self.isTrack = False
        self.isAlbum = False
        self.isArtist = False
        self.isPlaylist = False
        self.isGenre = False
        self.parentalWarning = False
        self.tracksCount = 0
        self.hires = False
        self.isFavorite = False
        self.dateAdd = None
        self.releaseDate = None
        self.streamable = True
        self.label = None
        self.mediaNumber = None
        self.trackNumber = None
        self.lastUpdate = None
        self.albumImage = None
        self.playlistImageList = None
        self.playlistTrackId = None
        self.artistName = None
        self.artistImage = None

    __classcell__ = None

