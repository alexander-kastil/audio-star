# Source Generated with Decompyle++
# File: LPQobuzRequester.pyc (Python 3.9)

'''
@Time ： 2025/7/11 12:06
@Auth ： Chris
@File ：LPQobuzRequester.py
@Desc:
'''
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPNetworkClient
from LPClientFramework.LPNetworkClient.LPQobuz.LPQobuzNetworkClient import LPQobuzNetworkClient
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzRequester:
    
    def __init__(self, client):
        self.client = client
        self.redirectUrl = 'https://www.qobuz.com/signin/oauth2?client_id=155398957&redirect_uri=https://auth.wiimhome.com/qobuz/wiimhome&response_type=code'
        self.baseUrl = 'https://www.qobuz.com/api.json/0.2/'
        self.CheckFavorite = 'favorite/status?type={}&item_id={}'
        self.Favorite_Ids = 'favorite/getUserFavoriteIds'
        self.User_LastUpdate = 'user/lastUpdate'
        self.Favorite_ToggleStatus = 'favorite/toggle'
        self.Favorite_Delete = 'favorite/delete'
        self.Favorite_Create = 'favorite/create'
        self.Favorite_PLAYLIST_Delete = 'playlist/unsubscribe'
        self.Favorite_PLAYLIST_Create = 'playlist/subscribe'
        self.Discover_NREndPoint = 'album/getFeatured?type=new-releases'
        self.Discover_RecommendEndPoint = 'dynamic-tracks/get?type=weekly'
        self.Discover_PlaylistEndPoint = 'playlist/getFeatured?&type=last-created'
        self.Discover_EssentialDiscographyEndPoint = 'album/getFeatured?type=ideal-discography'
        self.Discover_TopAlbumsEndPoint = 'album/getFeatured?type=most-streamed'
        self.Discover_QobuzissimeEndPoint = 'album/getFeatured?type=qobuzissims'
        self.Discover_PressAccoladesEndPoint = 'album/getFeatured?type=press-awards'
        self.Discover_PlaylistTagsEndPoint = 'playlist/getTags'
        self.Library_MyPlaylistEndPoint = 'playlist/getUserPlaylists'
        self.Library_FavoriteEndPoint = 'favorite/getUserFavorites?type='
        self.Library_PurchasedEndPoint = 'purchase/getUserPurchases?type='
        self.Detail_AlbumEndPoint = 'album/get?album_id='
        self.Detail_PlaylistEndPoint = 'playlist/get?extra=tracks,subscribers&playlist_id={}&offset={}&limit={}'
        self.Detail_SimilarAlbumsEndPoint = 'album/getFeatured?&type=best-sellers'
        self.Detail_ArtistEndPoint = 'artist/page?artist_id='
        self.Detail_ArtistSeeAllEndPoint = 'artist/getReleasesGrid?artist_id='
        self.Genres_SelectorEndPoint = 'genre/list'
        self.Search_EndPoint = 'catalog/search?query='
        self.SearchArtist_EndPoint = 'artist/search?query='
        self.SearchAlbum_EndPoint = 'album/search?query='
        self.SearchTrack_EndPoint = 'track/search?query='
        self.SearchPlaylist_EndPoint = 'playlist/search?query='
        self.qobuzHeadTypeMapping = {
            LPHeaderType.LP_HEADER_TYPE_ARTIST: 'artist',
            LPHeaderType.LP_HEADER_TYPE_COLLECTION: 'track',
            LPHeaderType.LP_HEADER_TYPE_PLAYLIST: 'playlist',
            LPHeaderType.LP_HEADER_TYPE_ALBUM: 'album' }

    
    def fetchFeaturedData(self, headType, contentType = None, genres = None, tag = None, offset = ('', '', 0, 25), limit = {
        'headType': LPHeaderType,
        'genres': str,
        'tag': str }):
        url = f'''{self.baseUrl}{self.qobuzHeadTypeMapping[headType]}/getFeatured?type={contentType}&offset={offset}&limit={limit}'''
        if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST and tag:
            url = url + f'''&tags={tag}'''
        if genres:
            url = url + f'''&genre_ids={genres}'''
        logger.debug(f'''[Qobuz] fetchFeaturedData url == {url}''')
        return self.client.get(url)

    
    def fetchRecommendData(self):
        url = f'''{self.baseUrl}dynamic-tracks/get?type=weekly'''
        logger.debug(f'''[Qobuz] fetchRecommendData url == {url}''')
        return self.client.get(url)

    
    def fetchMyPlaylistData(self, offset, limit, useCache = (0, 25, True)):
        url = f'''{self.baseUrl}playlist/getUserPlaylists?offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchMyPlaylistData url == {url}''')
        return self.client.get(url, useCache)

    
    def fetchFavoriteData(self, headType = None, genres = None, offset = None, limit = ('', 0, 25, True), useCache = {
        'headType': LPHeaderType,
        'genres': str }):
        url = f'''{self.baseUrl}favorite/getUserFavorites?type={self.qobuzHeadTypeMapping[headType]}s&offset={offset}&limit={limit}'''
        if genres:
            url = url + f'''&genre_ids={genres}'''
        logger.debug(f'''[Qobuz] fetchFavoriteData url == {url}''')
        return self.client.get(url, useCache)

    
    def fetchPurchaseData(self = None, headType = None, offset = None, limit = (0, 25, True), useCache = {
        'headType': LPHeaderType }):
        url = f'''{self.baseUrl}purchase/getUserPurchases?type={self.qobuzHeadTypeMapping[headType]}s&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchPurchaseData url == {url}''')
        return self.client.get(url, useCache)

    
    def fetchAlbumDetailData(self, albumID, offset, limit = (0, 25)):
        url = f'''{self.baseUrl}album/get?album_id={albumID}&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchAlbumDetailData url == {url}''')
        return self.client.get(url)

    
    def fetchPlaylistDetailData(self, playlistID, offset, limit, useCache = (0, 25, True)):
        url = f'''{self.baseUrl}playlist/get?extra=tracks,subscribers&playlist_id={playlistID}&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchPlaylistDetailData url == {url}''')
        return self.client.get(url, useCache)

    
    def fetchArtistDetailData(self, artistID):
        url = f'''{self.baseUrl}artist/page?artist_id={artistID}'''
        logger.debug(f'''[Qobuz] fetchArtistDetailData url == {url}''')
        return self.client.get(url)

    
    def fetchArtistReleases(self, artistID, contentType, sort, offset, limit = (0, 25)):
        url = f'''{self.baseUrl}artist/getReleasesGrid?artist_id={artistID}&release_type={contentType}&sort={sort}&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchArtistReleases url == {url}''')
        return self.client.get(url)

    
    def fetchSimilarAlbumData(self = None, genres = None, offset = None, limit = (0, 25)):
        url = f'''{self.baseUrl}album/getFeatured?&type=best-sellers&offset={offset}&limit={limit}&genre_ids={genres}'''
        logger.debug(f'''[Qobuz] fetchSimilarAlbumData url == {url}''')
        return self.client.get(url)

    
    def fetchSimilarArtistData(self, artistID, offset, limit = (0, 25)):
        url = f'''{self.baseUrl}artist/getSimilarArtists?artist_id={artistID}&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchSimilarArtistData url == {url}''')
        return self.client.get(url)

    
    def fetchSearchData(self = None, queryText = None, headType = None, offset = (None, 0, 25), limit = {
        'headType': LPHeaderType }):
        if not headType:
            url = f'''{self.baseUrl}catalog/search?query={queryText}&offset={offset}&limit={limit}'''
        else:
            url = f'''{self.baseUrl}{self.qobuzHeadTypeMapping[headType]}/search?query={queryText}&offset={offset}&limit={limit}'''
        logger.debug(f'''[Qobuz] fetchSearchData url == {url}''')
        return self.client.get(url)

    
    def fetchTagsData(self):
        url = f'''{self.baseUrl}playlist/getTags'''
        logger.debug(f'''[Qobuz] fetchTagsData url == {url}''')
        return self.client.get(url)

    
    def fetchFavoriteIds(self):
        url = f'''{self.baseUrl}favorite/getUserFavoriteIds'''
        logger.debug(f'''[Qobuz] fetchFavoriteIds url == {url}''')
        return self.client.post(url)

    
    def fetchGenresData(self):
        url = f'''{self.baseUrl}genre/list'''
        logger.debug(f'''[Qobuz] fetchGenresData url == {url}''')
        return self.client.get(url)

    
    def fetchLastUpdate(self):
        url = f'''{self.baseUrl}user/lastUpdate'''
        logger.debug(f'''[Qobuz] fetchLastUpdate url == {url}''')
        return self.client.post(url)

    
    def changeFavoriteStatus(self = None, headType = None, itemId = None, changeType = {
        'headType': LPHeaderType }):
        url = f'''{self.baseUrl}'''
        if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            if changeType == 'add':
                url += 'playlist/subscribe'
            else:
                url += 'playlist/unsubscribe'
        elif changeType == 'add':
            url += 'favorite/create'
        else:
            url += 'favorite/delete'
        if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            key = 'album_ids'
        elif headType == LPHeaderType.LP_HEADER_TYPE_SONG:
            key = 'track_ids'
        elif headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            key = 'playlist_id'
        elif headType == LPHeaderType.LP_HEADER_TYPE_ARTIST:
            key = 'artist_ids'
        else:
            return None
        data = {
            None: itemId }
        logger.debug(f'''[Qobuz] changeFavoriteStatus url == {url} type:{headType.value} item_id:{itemId}''')
        return self.client.post(url, data, **('data',))

    
    def fetchAddTracksData(self, playlistId, tracksIds):
        url = f'''{self.baseUrl}playlist/addTracks?playlist_id={playlistId}&track_ids={tracksIds}'''
        logger.debug(f'''[Qobuz] fetchAddTracksData url == {url}''')
        return self.client.post(url)

    
    def fetchPlaylistCreateData(self = None, data = None):
        url = f'''{self.baseUrl}playlist/create'''
        logger.debug(f'''[Qobuz] fetchPlaylistCreateData url == {url} , data == {data}''')
        return self.client.post(url, data, **('data',))

    
    def fetchDeletePlaylistData(self, playlistId):
        url = f'''{self.baseUrl}playlist/delete'''
        data = {
            'playlist_id': playlistId }
        logger.debug(f'''[Qobuz] fetchPlaylistCreateData url == {url} , data == {data}''')
        return self.client.post(url, data, **('data',))

    
    def fetchRemoveFromPlaylistData(self, playlistId, trackId):
        url = f'''{self.baseUrl}playlist/deleteTracks'''
        data = {
            'playlist_id': playlistId,
            'playlist_track_ids': trackId }
        logger.debug(f'''[Qobuz] fetchRemoveFromPlaylistData url == {url} , data == {data}''')
        return self.client.post(url, data, **('data',))

    
    def checkDiscoverCached(self):
        '''
        用 new release url 判断
        '''
        url = f'''{self.baseUrl}album/getFeatured?type=new-releases&offset=0&limit=25'''
        return self.client.cachedSession.cache.has_url(url)

    
    def checkArtistCached(self, artistID):
        url = f'''{self.baseUrl}artist/page?artist_id={artistID}'''
        return self.client.cachedSession.cache.has_url(url)


