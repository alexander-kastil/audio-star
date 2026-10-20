# Source Generated with Decompyle++
# File: LPRadioParadise2StreamService.pyc (Python 3.9)

'''
@Time ： 2025/1/2 16:31
@Auth ： Chris
@File ：LPRadioParadise2StreamService.py
@Desc:
'''
import json
import threading
from datetime import datetime
from typing import Type
import LPGlobalUI
from HOME.MyMusic.LPMyMusicAlbumDetailViewController import LPMyMusicAlbumDetailViewController
from HOME.MyMusic.LPMyMusicAlbumDetailViewController_ui import Ui_mymusicAlbumDetailViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController import LPMyMusicArtistDetailViewController
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from LPClientFramework import LPUtility, LPBeetsWrapper, LPPublicDefine
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPMusicLibrary import LPRecentlyManager, LPRecentlyPlayListCodec
from LPClientFramework.LPPlayList.LPPlayList import LPPlayHeader, LPPlayItem, LPPlayListSource, LPHeaderType
from LPClientFramework.LPPlayList.LPRadioParadise2PlayList import LPRadioParadise2PlayItem, LPRadioParadise2Account, LPRadioParadise2PlayList, LPRadioParadise2PlayHeader
from LPClientFramework.LPStreamServiceManager import LPStreamService
from LPClientFramework.LPUtility import logger

class LPRadioParadise2StreamService(LPStreamService):
    
    def LPTrackMoreViewControllerCanViewArtist(self = None, playHeader = None, playItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem] }):
        if callback:
            callback(False, None)
        return False

    
    def LPTrackMoreViewControllerCanViewAlbum(self, playHeader = None, playItem = None, artistItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        if callback:
            callback(False, None)
        return False

    
    def LPTrackMoreViewControllerViewArtist(self, playHeader = None, playItem = None, artistItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        pass

    
    def LPTrackMoreViewControllerViewAlbum(self, playHeader = None, playItem = None, albumItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'albumItem': Type[LPPlayItem] }):
        pass

    
    def registerAccount(self, userinfo):
        account = LPRadioParadise2Account()
        account.anonUserId = userinfo.get('anonUserId', None)
        account.userName = userinfo.get('userName', None)
        account.userId = userinfo.get('userId', None)
        account.expressIn = userinfo.get('expressIn', None)
        account.token = userinfo.get('token', None)
        account.showName = userinfo.get('showName', None)
        account.cUserId = account.userId if account.userId else account.anonUserId
        self.account = account
        if account.showName:
            logger.debug('[LPRadioParadise2StreamService] registerAccount: %s' % account.showName)
        return account

    
    def getAccount(self):
        return self.account

    
    def logoutAccount(self):
        self.account = None
        inParams = {
            'AccountSource': 'RadioParadise2' }
        response = LPGlobalUI.currentDevice.upnpPost('UserLogout', inParams)

    
    def loginAccount(self, username, password, finishedMethod):
        
        def _login(inParams = None, finishedMethod = None):
            response = LPGlobalUI.currentDevice.upnpPost('UserLogin', inParams)
            userinfo = None
        # WARNING: Decompyle incomplete

        inParams = {
            'AccountSource': 'RadioParadise2',
            'UserName': username,
            'PassWord': password }
        t = threading.Thread(_login, (inParams, finishedMethod), **('target', 'args'))
        t.start()

    
    def streamGuiBehavior(self, device):
        behaviorStr = device.mediaInfo.guiBehavior
        if behaviorStr:
            behavior = json.loads(behaviorStr)
            sp = {
                'loop': {
                    'enabled': False },
                'shuffle': {
                    'enabled': False },
                'seek': {
                    'enabled': False } }
            behavior.update(sp)
            return behavior

    
    def guiCan(self, device, key):
        behavior = self.streamGuiBehavior(device)
        if not behavior and key in behavior.keys() and behavior[key]['enabled']:
            return False

    
    def isCurrentPlayChannel(self, device, channelItem):
        if device.mediaInfo.itemId:
            return channelItem['chan'] == device.mediaInfo.itemId

    
    def accountChanged(self, device, notify):
        self._handleAccountChangedNotify(device, notify)

    
    def _handleAccountChangedNotify(self, device, notify):
        eventType = notify.get('eventType', None)
        payload = json.loads(notify.get('payload', None)) if notify.get('payload', None) else None
        source = notify.get('source', None)
        if eventType == 'accountChange' and source == self.source:
            userId = payload.get('userId', None)
            if userId == self.account.userId:
                logger.debug('[Service] [RadioParadise2] _handleAccountChangedNotify already login [ignore] this notify')
                return None
            if None:
                self.registerAccount(payload)
                logger.debug('[Service] [RadioParadise2] _handleAccountChangedNotify loginAccount because [other app]')
                LPUtility.postNotification('accountChangedForSource', {
                    'device': device,
                    'notify': notify })
                logger.debug('[Service] [RadioParadise2] accountChanged post notification')
        if eventType == 'logout' and source == self.source:
            if self.account or self.account.anonUserId:
                logger.debug('[Service] [RadioParadise2] _handleAccountChangedNotify already logout [ignore] this notify')
                return None
            None.logoutAccount()
            logger.debug('[Service] [RadioParadise2] _handleAccountChangedNotify logoutAccount because [other app]')
            LPUtility.postNotification('accountChangedForSource', {
                'device': device,
                'notify': notify })
            logger.debug('[Service] [RadioParadise2] accountChanged post notification')

    
    def updateMediaInfoWithItem(self, device, item, header = (None,)):
        '''用频道信息乐观更新设备媒体状态。

        :param device: 当前播放设备对象。
        :param item: RadioParadise2 频道字典。
        :param header: 可选播放列表头，本音源当前不使用。
        :return: None。
        '''
        channelId = item.get('chan', None)
        mediaInfo = {
            'trackId': channelId,
            'itemId': channelId,
            'mediaType': LPPublicDefine.MEDIATYPE_STATION,
            'playState': 'TRANSITIONING',
            'artworkUri': item.get('image', None),
            'trackName': item.get('title', None),
            'artist': '',
            'guiBehavior': '{"prev": {"enabled": false},"loop": {"enabled": false}, "shuffle": {"enabled": false}, "seek": {"enabled": false}}',
            'duration': '00:00:00',
            'progress': '00:00:00',
            'trackSource': self.source,
            'volume': device.mediaInfo.volume }
        device.setMediaInfo(mediaInfo)

    
    def LPTrackMoreCanPreset(self, device = (None,)):
        '''判断 Radio Paradise minibar 菜单是否展示 preset。

        :param device: 当前播放设备。
        :returns: 始终返回 ``True``。
        '''
        _ = device
        return True

    
    def recentlyCanPreset(self = None, detailDict = None):
        '''
        判断 Radio Paradise Recently 卡片条目是否支持保存为 preset。

        Args:
            detailDict: recently 记录中的 detail 字典。

        Returns:
            设备支持预设且快照�