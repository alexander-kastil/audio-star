# Source Generated with Decompyle++
# File: LPQobuzLibraryCacheManager.pyc (Python 3.9)

'''
@Time ： 2025/8/18 17:24
@Auth ： Chris
@File ：LPQobuzLibraryCacheManager.py
@Desc:
'''
import enum
import threading
import time
from functools import partial
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzAccount, LPQobuzLibPageState
from LPClientFramework.LPUtility import logger

class LPQobuzLibCache(enum.Enum):
    FavAlbum = 'favAlbumCache.pkl'
    MyPlaylist = 'myPlaylistCache.pkl'
    FavTrack = 'favTrackCache.pkl'
    FavArtist = 'favArtistCache.pkl'
    PurAlbum = 'purAlbumCache.pkl'
    PurTrack = 'purTrackCache.pkl'


class LPQobuzLibraryCacheManager(QObject):
    libCacheChangedSignal = pyqtSignal(object, str)
    cacheNeedUpdateSignal = pyqtSignal(str)
    libPlaylistLoadedSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.qobuz = parent
        self.sectionBinding = {
            'My Playlists': {
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST,
                'dataMethod': self.qobuz.requestMgr.fetchMyPlaylistData,
                'cacheName': LPQobuzLibCache.MyPlaylist,
                'updateTimeKey': 'playlist' },
            'Favorite Artists': {
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ARTIST,
                'dataMethod': self.qobuz.requestMgr.fetchFavoriteData,
                'cacheName': LPQobuzLibCache.FavArtist,
                'updateTimeKey': 'favorite_artist' },
            'Favorite Albums': {
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'dataMethod': self.qobuz.requestMgr.fetchFavoriteData,
                'cacheName': LPQobuzLibCache.FavAlbum,
                'updateTimeKey': 'favorite_album' },
            'Favorite Tracks': {
                'component': 'tableFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION,
                'dataMethod': self.qobuz.requestMgr.fetchFavoriteData,
                'cacheName': LPQobuzLibCache.FavTrack,
                'updateTimeKey': 'favorite_track' },
            'Purchased Albums': {
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'dataMethod': self.qobuz.requestMgr.fetchPurchaseData,
                'cacheName': LPQobuzLibCache.PurAlbum,
                'updateTimeKey': 'purchase' },
            'Purchased Tracks': {
                'component': 'tableFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION,
                'dataMethod': self.qobuz.requestMgr.fetchPurchaseData,
                'cacheName': LPQobuzLibCache.PurTrack,
                'updateTimeKey': 'purchase' } }
        self.checkLock = threading.Lock()

    
    def initLibCache(self = None, account = None):
        
        def _target():
