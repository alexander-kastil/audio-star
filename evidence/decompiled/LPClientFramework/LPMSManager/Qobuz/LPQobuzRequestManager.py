# Source Generated with Decompyle++
# File: LPQobuzRequestManager.pyc (Python 3.9)

'''
@Time ： 2025/7/11 12:06
@Auth ： Chris
@File ：LPQobuzRequestManager.py
@Desc:
'''
import json
from concurrent.futures import ThreadPoolExecutor
import requests
from PyQt6.QtCore import pyqtSignal, QObject
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestError, LPRequestCommonResult, LPRequestErrorType
from LPClientFramework.LPNetworkClient.LPQobuz.LPQobuzNetworkDataParser import LPQobuzNetworkDataParser, LPQobuzTagsParser, LPQobuzGenresParser, LPQobuzSearchDetailParser, LPQobuzArtistDetailParser, LPQobuzArtistSeeAllParser
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzRequestManager(QObject):
    http4xxErrorSignal = pyqtSignal(int)
    
    def __init__(self = None, requester = None):
        super().__init__()
        self.requester = requester
        self.parser = LPQobuzNetworkDataParser()
        self._executor = ThreadPoolExecutor(10, **('max_workers',))

    
    def fetch(self, reqFunc, callback = (None,), *args, **kwargs):
        
        def task():
            result = LPRequestCommonResult()
        # WARNING: Decompyle incomplete

        self._executor.submit(task)

    
    def fetchFeaturedData(self, headType, contentType = None, genres = None, tag = None, offset = ('', '', 0, 25), limit = {
        'headType': LPHeaderType,
        'contentType': str,
        'genres': str,
        'tag': str }):
        response = self.requester.fetchFeaturedData(headType, contentType, genres, tag, offset, limit)
        parser = self.parser.parseForContent(headType)
        return (parser.parse(response), response.status_code)

    
    def fetchRecommendData(self):
        response = self.requester.fetchRecommendData()
        headType = LPHeaderType.LP_HEADER_TYPE_COLLECTION
        parser = self.parser.parseForContent(headType)
        return (parser.parse(response), response.status_code)

    
    def fetchMyPlaylistData(self, offset, limit, useCache = (0, 25, True)):
        response = self.requester.fetchMyPlaylistData(offset, limit, useCache)
        headType = LPHeaderType.LP_HEADER_TYPE_PLAYLIST
        parser = self.parser.parseForContent(headType)
        return (parser.parse(response), response.status_code)

    
    def fetchFavoriteData(self, headType = None, genres = None, offset = None, limit = ('', 0, 25, True), useCache = {
        'headType': LPHeaderType,
        'genres': str }):
        response = self.requester.fetchFavoriteData(headType, genres, offset, limit, useCache)
        parser = self.parser.parseForContent(headType)
        return (parser.parse(response), response.status_code)

    
    def fetchPurchaseData(self = None, headType = None, offset = None, limit = (0, 25, True), useCache = {
        'headType': LPHeaderType }):
        response = self.requester.fetchPurchaseData(headType, offset, limit, useCache)
        parser = self.parser.parseForContent(headType)
        return (parser.parse(response), response.status_code)

    
    def fetchAlbumDetailData(self, albumID, offset, limit = (0, 25)):
        response = self.requester.fetchAlbumDetailData(albumID, offset, limit)
        parser = self.parser.parseForContent(LPHeaderType.LP_HEADER_TYPE_COLLECTION)
        return (parser.parse(response), response.status_code)

    
    def fetchPlaylistDetailData(self, playlistID, offset, limit, useCache = (0, 25, True)):
        response = self.requester.fetchPlaylistDetailData(playlistID, offset, limit, useCache)
        parser = self.parser.parseForContent(LPHeaderType.LP_HEADER_TYPE_COLLECTION)
        return (parser.parse(response), response.status_code)

    
    def fetchArtistDetailData(self, artistID):
        response = self.requester.fetchArtistDetailData(artistID)
        parser = LPQobuzArtistDetailParser()
        return (parser.parse(response), response.status_code)

    
    def fetchArtistReleases(self, artistID, contentType, sort, offset, limit = (0, 25)):
        response = self.requester.fetchArtistReleases(artistID, contentType, sort, offset, limit)
        parser = LPQobuzArtistSeeAllParser()
        return (parser.parse(response), response.status_code)

    
    def fetchSimilarAlbumData(self = None, genres = None, offset = None, limit = (0, 25)):
        response = self.requester.fetchSimilarAlbumData(genres, offset, limit)
        parser = self.parser.parseForContent(LPHeaderType.LP_HEADER_TYPE_ALBUM)
        return (parser.parse(response), response.status_code)

    
    def fetchSimilarArtistData(self, artistID, offset, limit = (0, 25)):
        response = self.requester.fetchSimilarArtistData(artistID, offset, limit)
        parser = self.parser.parseForContent(LPHeaderType.LP_HEADER_TYPE_ARTIST)
        return (parser.parse(response), response.status_code)

    
    def fetchTagsData(self):
        response = self.requester.fetchTagsData()
        parser = LPQobuzTagsParser()
        return (parser.parse(response), response.status_code)

    
    def fetchFavoriteIds(self):
        response = self.requester.fetchFavoriteIds()
        return (json.loads(response.text), response.status_code)

    
    def fetchGenresData(self):
        response = self.requester.fetchGenresData()
        parser = LPQobuzGenresParser()
        return (parser.parse(response), response.status_code)

    
    def fetchLastUpdate(self):
        response = self.requester.fetchLastUpdate()
        data = json.loads(response.text)
        return (data.get('last_update', { }), response.status_code)

    
    def changeFavoriteStatus(self = None, headType = None, itemId = None, changeType = (None,), callback = {
        'headType': LPHeaderType }):
        response = self.requester.changeFavoriteStatus(headType, itemId, changeType)
        ret = json.loads(response.text)
        return (ret.get('status', None), response.status_code)

    
    def fetchSearchData(self = None, queryText = None, headType = None, offset = (None, 0, 25), limit = {
        'headType': LPHeaderType }):
        response = self.requester.fetchSearchData(queryText, headType, offset, limit)
        if headType:
            parser = self.parser.parseForContent(headType)
        else:
            parser = LPQobuzSearchDetailParser()
        return (parser.parse(response), response.status_code)

    
    def fetchAddTracksData(self = None, playlistId = None, tracksIds = None):
        response = self.requester.fetchAddTracksData(playlistId, tracksIds)
        success = response.status_code == 200
        return (success, response.status_code)

    
    def fetchPlaylistCreateData(self, headType, trackId, name = None, desc = None, isPublic = None, isCollaborative = {
        'trackId': str,
        'name': str,
        'desc': str,
        'isPublic': bool,
        'isCollaborative': bool }):
        data = {
            'name': name,
            'description': desc }
        if isCollaborative:
            data.update({
                'is_collaborative': '1' })
        elif isPublic:
            pass
        
        'is_public'({
            '1': '0' })
        if headType == LPHeaderType.LP_HEADER_TYPE_SONG:
            data.update({
                'track_ids': str(trackId) })
        elif headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            data.update({
                'album_id': str(trackId) })
        response = self.requester.fetchPlaylistCreateData(data)
        success = response.status_code == 200
        return (success, response.status_code)

    
    def fetchDeletePlaylistData(self, playlistId, callback = (None,)):
        response = self.requester.fetchDeletePlaylistData(playlistId)
        ret = json.loads(response.text)
        return (ret.get('status', None), response.status_code)

    
    def fetchRemoveFromPlaylistData(self = None, playlistId = None, trackId = None):
        response = self.requester.fetchRemoveFromPlaylistData(playlistId, trackId)
        ret = json.loads(response.text)
        return (ret.get('status', None), response.status_code)

    
    def checkDiscoverCached(self):
        '''
        用 new release url 判断
        '''
        return self.requester.checkDiscoverCached()

    
    def checkArtistCached(self, artistID):
        return self.requester.checkArtistCached(artistID)

    __classcell__ = None

