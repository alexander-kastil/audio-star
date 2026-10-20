# Source Generated with Decompyle++
# File: LPQobuzNetworkDataParser.pyc (Python 3.9)

'''
@Time ： 2025/7/4 15:18
@Auth ： Chris
@File ：LPQobuzNetworkDataParser.py
@Desc:
'''
import copy
import enum
import json
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType, LPPlayListSource
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayHeader, LPQobuzPlayList, LPQobuzPlayItem

class LPQobuzContentType(enum.Enum):
    Albums = 'albums'
    Artists = 'artists'
    Playlists = 'playlists'
    Tracks = 'tracks'
    Detail_Artist = 'detail_artist'
    Detail_Playlist = 'tracks_p'
    Search_Summary = 'search_summary'


class LPQobuzUrl(enum.Enum):
    BaseUrl = 'https://www.qobuz.com/api.json/0.2/'
    ArtistDetail_EndPoint = 'artist/page?artist_id='


class LPQobuzNetworkDataParser:
    
    def __init__(self):
        self.searchUrl = None

    
    def parse(self, response):
        pass
    # WARNING: Decompyle incomplete

    
    def parseForContent(cls, contentType):
        if contentType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            return LPQobuzAlbumsParser()
        if None == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            return LPQobuzPlaylistParser()
        if None == LPHeaderType.LP_HEADER_TYPE_ARTIST:
            return LPQobuzArtistsParser()
        if None == LPHeaderType.LP_HEADER_TYPE_COLLECTION:
            return LPQobuzTracksParser()
        if None == LPQobuzContentType.Detail_Artist:
            return LPQobuzArtistDetailParser()
        if None == LPQobuzContentType.Search_Summary:
            return LPQobuzSearchDetailParser()
        return None

    parseForContent = classmethod(parseForContent)
    
    def deepGetByPath(self = None, data = None, path = None, default = (None,)):
        keys = path.split('.')
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
                continue
            return default
        if isinstance(data, list) and isinstance(default, str):
            if data:
                return data[0]
            return None



class LPQobuzAlbumsParser(LPQobuzNetworkDataParser):
    
    def __init__(self = None):
        super().__init__()
        self.field = 'albums'
        self.retDict = { }

    
    def parse(self = None, response = None):
        data = super().parse(response)
        header = LPQobuzPlayHeader()
        header.headType = LPHeaderType.LP_HEADER_TYPE_ALBUM
        header.offset = self.deepGetByPath(data, self.field + '.offset', 0)
        header.limit = self.deepGetByPath(data, self.field + '.limit', 0)
        header.total = self.deepGetByPath(data, self.field + '.total', 0)
        if not self.deepGetByPath(data, 'media_count', None):
            pass
        header.mediaCount = self.deepGetByPath(data, self.field + '.media_count', None)
        playList = LPQobuzPlayList()
        itemData = self.deepGetByPath(data, self.field + '.items', [])
        itemList = self.parseItem(itemData)
        playList.header = header
        playList.list = itemList
        return playList

    
    def parseGenre(self, genreItemData):
        genreObjArr = []
        playItem = LPQobuzPlayItem()
        playItem.trackId = genreItemData.get('id', None)
        playItem.trackName = genreItemData.get('name', None)
        playItem.genrePath = genreItemData.get('path', [])
        genreObjArr.append(playItem)
        return genreObjArr

    
    def parseItem(self, itemData):
        if not itemData:
            return None
        itemList = None
        for item in itemData:
            playItem = LPQobuzPlayItem()
            playItem.isAlbum = True
            playItem.trackId = item.get('id', '')
            playItem.parentalWarning = item.get('parental_warning', False)
            playItem.trackDuration = item.get('duration', 0) * 1000
            playItem.hires = item.get('hires', False)
            playItem.trackName = item.get('title', '')
            playItem.trackVersion = item.get('version', None)
            playItem.trackArtist = self.deepGetByPath(item, 'artist.name', None)
            playItem.artistId = self.deepGetByPath(item, 'artist.id', None)
            if not self.deepGetByPath(item, 'image.small', None) and self.deepGetByPath(item, 'image.large', None):
                pass
            playItem.trackImage = self.deepGetByPath(item, 'image.thumbnail', None)
            if not item.get('release_date_stream', '') and item.get('release_date_original', ''):
                pass
            playItem.date = item.get('release_date_download', '')
            playItem.streamable = item.get('streamable', False)
            playItem.genreObjArr = self.parseGenre(item.get('genre', { }))
            playItem.dateAdd = item.get('favorited_at', None)
            playItem.label = self.deepGetByPath(item, 'label.name', None)
            playItem.tracksCount = item.get('tracks_count', None)
            playItem.trackNumber = item.get('track_number', None)
            playItem.mediaNumber = item.get('media_number', None)
            itemList.append(playItem)
        return itemList

    __classcell__ = None


class LPQobuzArtistsParser(LPQobuzNetworkDataParser):
    
    def __init__(self):
        self.field = 'artists'
        self.retDict = { }

    
    def parse(self = None, response = None):
        data = super().parse(response)
        header = LPQobuzPlayHeader()
        header.headType = LPHeaderType.LP_HEADER_TYPE_ARTIST
        header.offset = self.deepGetByPath(data, self.field + '.offset', 0)
        header.limit = self.deepGetByPath(data, self.field + '.limit', 0)
        header.total = self.deepGetByPath(data, self.field + '.total', 0)
        playList = LPQobuzPlayList()
        itemData = self.deepGetByPath(data, self.field + '.items', [])
        itemList = self.parseItem(itemData)
        playList.header = header
        playList.list = itemList
        return playList

    
    def parseItem(self, itemData):
        itemList = []
        for item in itemData:
            playItem = LPQobuzPlayItem()
            playItem.isArtist = True
            playItem.trackId = item.get('id', '')
            playItem.trackName = item.get('name', '')
            if not self.deepGetByPath(item, 'image.medium', None) and self.deepGetByPath(item, 'image.small', None):
                pass
            playItem.trackImage = self.deepGetByPath(item, 'image.large', None)
            playItem.dateAdd = item.get('favorited_at', False)
            itemList.append(playItem)
        return itemList

    __classcell__ = None


class LPQobuzTracksParser(LPQobuzNetworkDataParser):
    
    def __init__(self = None):
        super().__init__()
        self.field = 'tracks'
        self.retDict = { }
        self.header = LPQobuzPlayHeader()

    
    def parse(self = None, response = None):
        data = super().parse(response)
        self.header.mediaSource = LPPlayListSource.Qobuz.value
        self.header.headType = LPHeaderType.LP_HEADER_TYPE_COLLECTION
        if not data.get('title', ''):
            pass
        self.header.headTitle = data.get('name', '')
        self.header.offset = self.deepGetByPath(data, self.field + '.offset', 0)
        self.header.limit = self.deepGetByPath(data, self.field + '.limit', 0)
        self.header.total = self.deepGetByPath(data, self.field + '.total', 0)
        self.header.duration = data.get('duration', 0) * 1000
        if not self.deepGetByPath(data, 'images.small', '') and self.deepGetByPath(data, 'images.large', '') and self.deepGetByPath(data, 'image.small', '') and self.deepGetByPath(data, 'image.large', ''):
            pass
        self.header.imageUrl = self.deepGetByPath(data, 'image_rectangle', '')
        self.header.totalTracks = data.get('track_count', None)
        self.header.hires = data.get('hires', False)
        self.header.qualityStr = data.get('maximum_technical_specifications', '')
        self.header.weeklyQBaseline = data.get('baseline', '')
        self.header.descText = data.get('description', '')
        if not self.deepGetByPath(data, 'media_count', None):
            pass
        self.header.mediaCount = self.deepGetByPath(data, self.field + '.media_count', None)
        self.header.trackArtist = self.deepGetByPath(data, 'artist.name', None)
        if not data.get('release_date_stream', '') and data.get('release_date_original', ''):
            pass
        self.header.date = data.get('release_date_download', '')
        self.header.parentalWarning = data.get('parental_warning', False)
        self.header.label = self.deepGetByPath(data, 'label.name', None)
        self.header.trackOwner = self.deepGetByPath(data, 'owner.name', None)
        self.header.isPublic = data.get('is_public', False)
        self.header.graphics = data.get('graphics', { })
        if not self.header.searchUrl:
            self.header.searchUrl = self.searchUrl
        playList = LPQobuzPlayList()
        itemData = self.deepGetByPath(data, self.field + '.items', [])
        itemList = self.parseItem(itemData)
        playList.header = self.header
        playList.list = itemList
        return playList

    
    def parseGenre(self, genreItemData):
        genreObjArr = []
        playItem = LPQobuzPlayItem()
        playItem.trackId = genreItemData.get('id', None)
        playItem.trackName = genreItemData.get('name', None)
        playItem.genrePath = genreItemData.get('path', [])
        genreObjArr.append(playItem)
        return genreObjArr

    
    def parseItem(self, itemData):
        itemList = []
        for index, item in enumerate(itemData):
            playItem = LPQobuzPlayItem()
            playItem.isTrack = True
            playItem.trackId = item.get('id', '')
            playItem.trackName = item.get('title', '')
            playItem.trackVersion = item.get('version', None)
            playItem.trackArtist = self.deepGetByPath(item, 'performer.name', None)
            playItem.artistId = self.deepGetByPath(item, 'performer.id', None)
            if not self.deepGetByPath(item, 'album.image.small', None) and self.deepGetByPath(item, 'album.image.large', None) and self.deepGetByPath(item, 'album.image.thumbnail', None):
                pass
            playItem.trackImage = self.header.imageUrl
            playItem.albumName = self.deepGetByPath(item, 'album.title', None)
            playItem.albumId = self.deepGetByPath(item, 'album.id', None)
            playItem.streamable = item.get('streamable', False)
            playItem.parentalWarning = item.get('parental_warning', False)
            playItem.trackDuration = item.get('duration', 0) * 1000
            playItem.hires = item.get('hires', False)
            if not item.get('release_date_stream', '') and item.get('release_date_original', ''):
                pass
            playItem.date = item.get('release_date_download', '')
            playItem.dateAdd = item.get('favorited_at', False)
            playItem.genreObjArr = self.parseGenre(self.deepGetByPath(item, 'album.genre', { }))
            playItem.trackNumber = item.get('track_number', None)
            playItem.mediaNumber = item.get('media_number', None)
            playItem.playlistTrackId = item.get('playlist_track_id', None)
            playItem.searchUrl = self.searchUrl
            playItem.startIndex = index + 1
            itemList.append(playItem)
        return itemList

    __classcell__ = None


class LPQobuzPlaylistParser(LPQobuzNetworkDataParser):
    
    def __init__(self):
        self.field = 'playlists'
        self.retDict = { }

    
    def parse(self = None, response = None):
        data = super().parse(response)
        header = LPQobuzPlayHeader()
        header.headType = LPHeaderType.LP_HEADER_TYPE_PLAYLIST
        header.offset = self.deepGetByPath(data, self.field + '.offset', 0)
        header.limit = self.deepGetByPath(data, self.field + '.limit', 0)
        header.total = self.deepGetByPath(data, self.field + '.total', 0)
        playList = LPQobuzPlayList()
        itemData = self.deepGetByPath(data, self.field + '.items', [])
        itemList = []
        if itemData:
            itemList = self.parseItem(itemData)
        playList.header = header
        playList.list = itemList
        return playList

    
    def parseGenre(self, genreItemsData):
        genreObjArr = []
        for genreItem in genreItemsData:
            playItem = LPQobuzPlayItem()
            playItem.trackId = genreItem.get('id', None)
            playItem.trackName = genreItem.get('name', None)
            playItem.genrePath = genreItem.get('path', [])
            genreObjArr.append(playItem)
        return genreObjArr

    
    def parseItem(self, itemData):
        itemList = []
        for item in itemData:
            playItem = LPQobuzPlayItem()
            playItem.isPlaylist = True
            playItem.trackId = item.get('id', '')
            playItem.parentalWarning = item.get('parental_warning', False)
            playItem.trackDuration = item.get('duration', 0) * 1000
            playItem.hires = item.get('hires', False)
            playItem.isPublic = item.get('is_public', True)
            playItem.trackName = item.get('name', '')
            if item.get('image_rectangle', []):
                pass
            elif not None:
                pass
            playItem.trackImage = None
            playItem.trackOwner = self.deepGetByPath(item, 'owner.name', None)
            playItem.ownerId = self.deepGetByPath(item, 'owner.id', None)
            playItem.tracksCount = item.get('tracks_count', None)
            if not item.get('images150', None) and item.get('images300', None):
                pass
            playItem.playlistImageList = item.get('images50', None)
            playItem.genreObjArr = self.parseGenre(item.get('genres', []))
            playItem.lastUpdate = item.get('updated_at', None)
            playItem.dateAdd = item.get('subscribed_at', None)
            itemList.append(playItem)
        return itemList

    __classcell__ = None


class LPQobuzArtistDetailParser(LPQobuzNetworkDataParser):
    
    def __init__(self = None):
        super().__init__()
        self.data = None
        self.imageBase = 'https://static.qobuz.com/images/artists/covers/large/'
        self.header = LPQobuzPlayHeader()
        self.retDict = { }
        self.itemFields = [
            {
                'field': 'similar_artists',
                'headType': LPHeaderType.LP_HEADER_TYPE_ARTIST },
            {
                'field': 'top_tracks',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION },
            {
                'field': 'last_release',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM },
            {
                'field': 'tracks_appears_on',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION },
            {
                'field': 'playlists',
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST }]
        self.releaseFields = [
            'album',
            'live',
            'compilation',
            'epSingle',
            'download',
            'other']
        self.keyMap = [
            ('top_tracks', 'Most popular'),
            ('last_release', 'Latest release'),
            ('album', 'Albums'),
            ('epSingle', 'EPs & Singles'),
            ('live', 'Live'),
            ('playlists', 'Playlists'),
            ('compilation', 'Compilations'),
            ('similar_artists', 'Similar artists'),
            ('download', 'Purchase only'),
            ('other', 'Other'),
            ('tracks_appears_on', 'Appears on')]

    
    def parse(self = None, response = None):
