# Source Generated with Decompyle++
# File: LPPCRemoteLocalStreamService.pyc (Python 3.9)

from datetime import datetime
from typing import Type
from bs4 import BeautifulSoup
import LPGlobalUI
from HOME.MyMusic.LPMyMusicAlbumDetailViewController import LPMyMusicAlbumDetailViewController
from HOME.MyMusic.LPMyMusicAlbumDetailViewController_ui import Ui_mymusicAlbumDetailViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController import LPMyMusicArtistDetailViewController
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from HOME.MyMusic.LPMyMusicGenreDetailViewController import LPMyMusicGenreDetailViewController
from HOME.MyMusic.LPMyMusicGenreDetailViewController_ui import Ui_mymusicGenreDetailViewWidget
from HOME.MyMusic.LPMyMusicTracksViewController import LPMyMusicTracksViewController
from HOME.MyMusic.LPMyMusicTracksViewController_ui import Ui_mymusicTracksViewWidget
from LPClientFramework import LPUtility, LPBeetsWrapper, LPPublicDefine
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPMusicLibrary import LPRecentlyManager, LPRecentlyPlayListCodec
from LPClientFramework.LPPlayList.LPLocalMusicPlayList import LPLocalMusicPlayItem, LPLocalMusicPlayList
from LPClientFramework.LPPlayList.LPPlayList import LPPlayHeader, LPPlayItem, LPHeaderType
from LPClientFramework.LPUtility import logger
from LPClientFramework.LPStreamServiceManager import LPStreamService

class LPPCRemoteLocalStreamService(LPStreamService):
    
    def recentlyDidSelect(self = None, detailDict = None, baseController = None):
        '''
        从 recently detail 的 playList 恢复 MyMusic 内容页。

        Args:
            detailDict: recently 记录中的 detail 字典。
            baseController: 预留参数，当前本地音乐详情恢复不依赖页面控制器。

        Returns:
            是否已成功进入详情页。
        '''
        playList = self._playListFromRecentlyDetail(detailDict)
        if playList is None or playList.header is None:
            logger.debug('[PCRemoteLocal] recentlyDidSelect ignore because playList is invalid')
            return False
        currentItem = None.currentItemFromPlayList(playList)
        navigationType = self._recentlyNavigationType(playList, currentItem)
        if navigationType is None:
            logger.debug('[PCRemoteLocal] recentlyDidSelect ignore because recent item cannot map to a detail page')
            return False
        if not None._isRecentlyResourceAvailable(playList, currentItem, navigationType):
            logger.debug('[PCRemoteLocal] recentlyDidSelect ignore because recent item resource is unavailable')
            return False
        return None._navigateFromRecently(playList, currentItem, navigationType)

    
    def recentlyOpensDetail(self = None, detailDict = None):
        '''
        判断 My Music recently 是否应打开详情页。

        Args:
            detailDict: recently 记录 detail。

        Returns:
            会进入详情页返回 True。
        '''
        return self._canNavigateRecently(detailDict)

    
    def playRecently(self = None, detailDict = None, baseController = None):
        '''
        处理本地音乐 Recently 播放按钮：直接恢复播放，不进入详情页。

        Args:
            detailDict: recently 记录中的 detail 字典。
            baseController: 预留参数，直接播放不依赖页面控制器。

        Returns:
            是否已成功发起播放请求。
        '''
        playList = self._playListFromRecentlyDetail(detailDict)
        if not playList is None and playList.header is None or playList.list:
            logger.debug('[PCRemoteLocal] playRecently ignore because playList is invalid')
            return False
        if not None._filterUnavailableRecentlyItemsForPlayback(playList):
            logger.debug('[PCRemoteLocal] playRecently ignore because local resource is unavailable')
            return False
        currentItem = None.currentItemFromPlayList(playList)
        if currentItem is None:
            logger.debug('[PCRemoteLocal] playRecently ignore because currentItem is empty')
            return False
        device = None.currentDevice
        if device is None:
            logger.debug('[PCRemoteLocal] playRecently ignore because currentDevice is empty')
            return False
        
        def _playFinishMethod(result = None):
            '''
            处理本地音乐恢复播放结果，成功后刷新 Recently 记录。

            :param result: 设备播放是否成功。
            :return: None。
            '''
            logger.debug('[PCRemoteLocal] playRecently result=%s title=%s', result, getattr(currentItem, 'trackName', ''))
        # WARNING: Decompyle incomplete

        device.fastPlay(playList, _playFinishMethod)
        return True

    
    def recentlyResourceUnavailable(self = None, detailDict = None):
        '''
        判断 Recently 本地音乐快照是否已没有任何可访问文件。

        :param detailDict: Recently 条目中的 detail 字典。
        :return: 快照有效但所有本地文件均已删除或移动时返回 True。
        '''
        playList = self._playListFromRecentlyDetail(detailDict)
        if not playList is None or getattr(playList, 'list', None):
            return False
        return not None._playListHasExistingLocalResource(playList)

    
    def LPTrackMoreViewControllerCanViewArtist(self = None, playHeader = None, playItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem] }):
        if playItem.customUUID != LPUtility.pcUUID():
            if callback:
                callback(False, None)
            return False
        if None:
            if callback:
                callback(True, None)
            return True
        if not None.trackArtist:
            if callback:
                callback(False, None)
            return False
        artists = None.queryTrackArtists(playItem.trackArtist, True, **('strict',))
        if len(artists) == 0:
            if callback:
                callback(False, None)
            return False
        artistDict = None[0]
        retItem = LPPlayItem()
        retItem.trackArtist = artistDict['artist']
        if callback:
            callback(True, retItem)
        return True

    
    def LPTrackMoreViewControllerCanViewAlbum(self, playHeader = None, playItem = None, artistItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        if playItem.customUUID != LPUtility.pcUUID():
            if callback:
                callback(False, None)
            return False
        if None:
            if callback:
                callback(True, None)
            return True
        if not None.albumName:
            if callback:
                callback(False, None)
            return False
        albums = None.queryAlbums(playItem.albumName, **('key',))
        if len(albums) == 0:
            if callback:
                callback(False, None)
            return False
        albumDict = None[0]
        retItem = LPPlayItem()
        retItem.albumName = albumDict['album']
        if callback:
            callback(True, retItem)
        return True

    
    def LPTrackMoreViewControllerViewArtist(self, playHeader = None, playItem = None, artistItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        if not callback:
            return None
        artists = None.queryTrackArtists(playItem.trackArtist)
        if len(artists) == 0:
            return None
        None(LPGlobalUI.loadUI(LPUIPath.MyMusicArtistDetailViewControllerUI, Ui_mymusicArtistDetailViewWidget, LPMyMusicArtistDetailViewController, artists[0]))

    
    def LPTrackMoreViewControllerViewAlbum(self, playHeader = None, playItem = None, albumItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'albumItem': Type[LPPlayItem] }):
        if not callback:
            return None
        albums = None.queryAlbums(playItem.albumName, **('key',))
        if len(albums) == 0:
            return None
        albumDict = None[0]
        callback(LPGlobalUI.loadUI(LPUIPath.MyMusicAlbumDetailViewControllerUI, Ui_mymusicAlbumDetailViewWidget, LPMyMusicAlbumDetailViewController, albumDict))

    
    def currentPlayItem(self = None, device = None):
        '''音箱当前播放的playItem对象
        :returns: sub LPPlayItem
        '''
        if device.name.endswith('AAE0'):
            print(1)
        playItem = LPLocalMusicPlayItem()
        playItem.trackName = device.mediaInfo.trackName
        playItem.trackId = device.mediaInfo.trackId
        playItem.trackArtist = device.mediaInfo.artist
        playItem.artistId = device.mediaInfo.artistId
        playItem.albumId = device.mediaInfo.albumId
        playItem.albumName = device.mediaInfo.album
        playItem.customUUID = device.mediaInfo.customUUID
        return playItem

    
    def parseQueuePlayItem(self, trackItemObj):
