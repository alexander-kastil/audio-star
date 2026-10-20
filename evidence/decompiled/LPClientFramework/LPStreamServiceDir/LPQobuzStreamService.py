# Source Generated with Decompyle++
# File: LPQobuzStreamService.pyc (Python 3.9)

'''
@Time ： 2025/5/28 17:05
@Auth ： Chris
@File ：LPQobuzStreamService.py
@Desc:
'''
import json
from typing import Type
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QTableView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.Playlist.LPQobuzAddToPlaylistDialog import LPQobuzAddToPlaylistDialog
from HOME.StreamService.Qobuz.Component.UI.LPQobuzAddToPlaylistDialog_ui import Ui_AddToPlaylistDialog
from HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController import LPQobuzAlbumDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController import LPQobuzPlaylistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzWeeklyQDetailViewController import LPQobuzWeeklyQDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzWeeklyQDetailViewController_ui import Ui_qobuzWeeklyQDetailViewWidget
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteTrackSeeAllViewController import LPQobuzFavoriteTrackSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.UI.LPQobuzFavoriteTrackSeeAllViewController_ui import Ui_qobuzFTrackSeeAllWidget
from LPClientFramework import LPUtility, LPPublicDefine
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPMusicLibrary import LPRecentlyManager, LPRecentlyPlayListCodec
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPPlayHeader, LPPlayItem, LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem, LPQobuzAccount, LPQobuzPlayList, LPQobuzPlayHeader, HeadTitle_Weekly_Q, HeadTitle_Favorite_Tracks, HeadTitle_Purchased_Tracks
from LPClientFramework.LPStreamServiceManager import LPStreamService
from LPClientFramework.LPUtility import logger
from LPClientFramework.util.aes import AESCipher
_QOBUZ_FAVORITE_HEAD_TYPE_MAP = {
    'album': LPHeaderType.LP_HEADER_TYPE_ALBUM,
    'artist': LPHeaderType.LP_HEADER_TYPE_ARTIST,
    'track': LPHeaderType.LP_HEADER_TYPE_SONG,
    'playlist': LPHeaderType.LP_HEADER_TYPE_PLAYLIST }

class LPQobuzStreamService(LPStreamService):
    '''Qobuz 流服务实现，负责详情跳转、当前播放解析和设备状态同步。'''
    _prefixedDetailNavigationId = True
    
    def _metadataText(metaDataObj, *names):
        '''从不同命名空间候选字段里取第一个非空文本。

        :param metaDataObj: 解析后的 metadata XML 对象。
        :param names: 候选字段名，按优先级依次尝试。
        :returns: 第一个非空字段文本；都不存在时返回空字符串。
        '''
        for name in names:
            element = metaDataObj.find(name, None)
            if element and element.text is not None:
                return element.text
            return ''

    _metadataText = staticmethod(_metadataText)
    
    def _normalizedGenreObjArr(playItem):
        '''把播放项上的 ``genreObjArr`` 规范成列表。

        :param playItem: 可能带有 ``genreObjArr`` 属性的播放项。
        :returns: 规范后的 genre 对象列表；缺失或类型不匹配时返回空列表。
        '''
        genreObjArr = getattr(playItem, 'genreObjArr', None)
        if isinstance(genreObjArr, (list, tuple)):
            return list(genreObjArr)

    _normalizedGenreObjArr = staticmethod(_normalizedGenreObjArr)
    
    def _buildCurrentPlayItem(self, device, sourcePlayItem = (None,)):
        '''构造当前播放的 Qobuz 播放项。

        :param device: 当前设备对象。
        :param sourcePlayItem: 队列中已命中的原始播放项，优先复用其扩展字段。
        :returns: 补齐后的 ``LPQobuzPlayItem`` 对象。
        '''
        playItem = LPQobuzPlayItem()
        if sourcePlayItem is not None:
            playItem.trackSource = getattr(sourcePlayItem, 'trackSource', playItem.trackSource)
            playItem.trackName = getattr(sourcePlayItem, 'trackName', None)
            playItem.trackId = getattr(sourcePlayItem, 'trackId', None)
            playItem.trackUrl = getattr(sourcePlayItem, 'trackUrl', None)
            playItem.trackImage = getattr(sourcePlayItem, 'trackImage', None)
            playItem.trackArtist = getattr(sourcePlayItem, 'trackArtist', None)
            playItem.artistId = getattr(sourcePlayItem, 'artistId', None)
            playItem.trackDuration = getattr(sourcePlayItem, 'trackDuration', 0)
            playItem.albumName = getattr(sourcePlayItem, 'albumName', None)
            playItem.albumId = getattr(sourcePlayItem, 'albumId', None)
            playItem.customUUID = getattr(sourcePlayItem, 'customUUID', None)
            playItem.genreObjArr = self._normalizedGenreObjArr(sourcePlayItem)
        if device and device.mediaInfo:
            if not playItem.trackName:
                pass
            playItem.trackName = device.mediaInfo.trackName
            if not playItem.trackId:
                pass
            playItem.trackId = device.mediaInfo.trackId
            if not playItem.trackImage:
                pass
            playItem.trackImage = device.mediaInfo.artworkUri
            if not playItem.trackArtist:
                pass
            playItem.trackArtist = device.mediaInfo.artist
            if not playItem.artistId:
                pass
            playItem.artistId = device.mediaInfo.artistId
            if not playItem.albumName:
                pass
            playItem.albumName = device.mediaInfo.album
            if not playItem.albumId:
                pass
            playItem.albumId = device.mediaInfo.albumId
            if not playItem.customUUID:
                pass
            playItem.customUUID = device.mediaInfo.customUUID
        return playItem

    
    def _detailNavigationReady(self, device = (None,)):
        '''判断当前上下文是否具备进入 Qobuz 详情页的条件。

        :param device: 待检查的设备对象；为空时默认使用当前设备。
        :returns: 设备账号、登录账号与 token 都有效时返回 ``True``。
        '''
        if not device:
            pass
        device = LPGlobalUI.currentDevice
        if not device:
            return False
        LPQobuzManager = LPQobuzManager
        import LPClientFramework.LPMSManager.Qobuz.LPQobuzManager
        qobuz = LPQobuzManager.instance()
        currentAccount = qobuz.loginMgr.account
        if not currentAccount or currentAccount.userId:
            return False
        deviceAccount = None.deviceStreamServiceManager.accountForSource(self.source)
        if not deviceAccount or deviceAccount.userId:
            return False
        if None(deviceAccount.userId) != str(currentAccount.userId):
            return False
        return None(qobuz.requestMgr.requester.client.getToken())

    
    def LPTrackMoreViewControllerCanViewArtist(self = None, playHeader = None, playItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem] }):
        '''判断更多菜单中是否允许查看歌手详情。

        :param playHeader: 当前列表头信息，保留现有接口签名。
        :param playItem: 当前曲目对应的播放项。
        :param immediately: 兼容旧接口的预留参数。
        :param callback: 可选回调，参数为 ``(canView, None)``。
        :returns: 是否允许展示或进入歌手详情。
        '''
        return self._canViewDetailArtist(playHeader, playItem, immediately, callback)

    
    def LPTrackMoreViewControllerCanViewAlbum(self, playHeader = None, playItem = None, artistItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        '''判断更多菜单中是否允许查看专辑详情。

        :param playHeader: 当前列表头信息。
        :param playItem: 当前曲目对应的播放项。
        :param artistItem: 兼容旧接口的预留参数，本方法不直接使用。
        :param immediately: 兼容旧接口的预留参数。
        :param callback: 可选回调，参数为 ``(canView, None)``。
        :returns: 是否允许展示或进入专辑详情。
        '''
        return self._canViewDetailAlbum(playHeader, playItem, artistItem, immediately, callback)

    
    def LPTrackMoreViewControllerCanAddToPlaylist(self, playHeader = None, playItem = None, artistItem = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        canView = True
        trackId = playItem.trackId
        if not trackId:
            canView = False
        if callback:
            callback(canView, None)
        return canView

    
    def LPTrackMoreViewControllerCanRemoveFromPlaylist(self, playHeader = None, playItem = None, qobuzAccount = None, immediately = (False, None), callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem] }):
        canView = True
        trackId = playItem.trackId
        if not trackId:
            canView = False
        if not hasattr(playHeader, 'ownerId'):
            canView = False
            return canView
        ownerId = None.ownerId
        userId = qobuzAccount.userId
        if ownerId and userId or str(ownerId) != str(userId):
            canView = False
        if callback:
            callback(canView, None)
        return canView

    
    def LPTrackMoreViewControllerViewArtist(self, playHeader = None, playItem = None, artistItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'artistItem': Type[LPPlayItem] }):
        '''构造并打开歌手详情控制器。

        :param playHeader: 当前列表头信息。
        :param playItem: 当前曲目对应的播放项。
        :param artistItem: 兼容旧接口的预留参数，本方法内部会重建对象。
        :param callback: 用于接收详情控制器的回调。
        :returns: None
        '''
        self._viewDetailArtist(playHeader, playItem, artistItem, callback)

    
    def _openArtistDetail(self, playHeader, playItem, artistId, callback):
        '''Qobuz 构造艺人详情控制器并通过菜单回调打开。'''
        _ = playHeader
        artistItem = LPQobuzPlayItem()
        artistItem.trackId = artistId
        if not playItem.trackArtist:
            pass
        artistItem.trackName = ''
        artistItem.isArtist = True
        callback(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistItem))

    
    def LPTrackMoreViewControllerViewAlbum(self, playHeader = None, playItem = None, albumItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'albumItem': Type[LPPlayItem] }):
        '''构造并打开专辑详情控制器。

        :param playHeader: 当前列表头信息。
        :param playItem: 当前曲目对应的播放项。
        :param albumItem: 兼容旧接口的预留参数，本方法内部会重建对象。
        :param callback: 用于接收详情控制器的回调。
        :returns: None
        '''
        self._viewDetailAlbum(playHeader, playItem, albumItem, callback)

    
    def _openAlbumDetail(self, playHeader, playItem, albumId, callback):
        '''Qobuz 构造专辑详情控制器并通过菜单回调打开。'''
        _ = playHeader
        albumItem = LPQobuzPlayItem()
        albumItem.trackId = albumId
        if not playItem.albumName:
            pass
        albumItem.trackName = ''
        if not playItem.trackArtist:
            pass
        albumItem.trackArtist = ''
        if not playItem.artistId:
            pass
        albumItem.artistId = None
        albumItem.trackImage = getattr(playItem, 'trackImage', None)
        albumItem.genreObjArr = self._normalizedGenreObjArr(playItem)
        albumItem.isAlbum = True
        callback(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, albumItem))

    
    def LPTrackMoreViewControllerAddToPlaylist(self, playHeader = None, playItem = None, albumItem = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'albumItem': Type[LPPlayItem] }):
        trackId = playItem.trackId
        if not trackId:
            return None
        parent = None.getTopWidget()
        callback(LPGlobalUI.loadUI(LPUIPath.QobuzAddToPlaylistDialogUI, Ui_AddToPlaylistDialog, LPQobuzAddToPlaylistDialog, playItem, parent))

    
    def LPTrackMoreViewControllerRemoveFromPlaylist(self, playHeader = None, playItem = None, tableView = None, callback = {
        'playHeader': Type[LPPlayHeader],
        'playItem': Type[LPPlayItem],
        'tableView': QTableView }):
        trackId = playItem.trackId
        if not trackId:
            return None
        None(None)

    
    def registerAccount(self, userinfo):
        '''
        注册设备返回的 Qobuz 账号信息。

        Args:
            userinfo: 设备 GetUserInfo 或账号变化通知返回的用户信息。

        Returns:
            Qobuz 账号对象；无有效 userId 时返回 None 并清空当前账号。
        '''
        if not isinstance(userinfo, dict) or userinfo.get('userId', None):
            self.account = None
            return None
        account = None()
        account.userName = userinfo.get('userName', None)
        account.userId = userinfo.get('userId', None)
        account.expressIn = userinfo.get('expressIn', None)
        accessToken = userinfo.get('accessToken', None)
        if accessToken:
            accessToken = AESCipher.decrypt2(LPGlobalUI.currentDevice.uuid[:16], accessToken)
        account.token = accessToken
        account.showName = userinfo.get('showName', None)
        account.email = userinfo.get('email', None)
        account.subscription = userinfo.get('credential', { }).get('description', None)
        if not userinfo.get('credential', { }).get('parameters'):
            pass
        streaming = { }.get('hires_purchases_streaming', False)
        account.maxStreaming = 4 if streaming else 2
        self.account = account
        if account.showName:
            logger.debug(f'''[LPQobuzStreamService] {LPGlobalUI.currentDevice.uuid} registerAccount: %s''' % account.showName)
        return account

    
    def getAccount(self):
        return self.account

    
    def logoutAccount(self):
        self.account = None
        inParams = {
            'AccountSource': LPPlayListSource.Qobuz.value }
        response = LPGlobalUI.currentDevice.upnpPost('UserLogout', inParams)

    
    def streamGuiBehavior(self, device):
        behaviorStr = device.mediaInfo.guiBehavior
        if behaviorStr:
            behavior = json.loads(behaviorStr)
            return behavior

    
    def guiCan(self, device, key):
        behavior = self.streamGuiBehavior(device)
        if not behavior and key in behavior.keys() and behavior[key]['enabled']:
            return False

    
    def accountChanged(self, device, notify):
        self._handleAccountChangedNotify(device, notify)

    
    def _handleAccountChangedNotify(self, device, notify):
        eventType = notify.get('eventType', None)
        payload = json.loads(notify.get('payload', None)) if notify.get('payload', None) else None
        source = notify.get('source', None)
        if eventType == 'accountChange' and source == self.source:
            userId = payload.get('userId', None)
            if payload:
                self.registerAccount(payload)
                logger.debug(f'''[Service] [Qobuz] _handleAccountChangedNotify device=={device.uuid} loginAccount because [other app]''')
                LPUtility.postNotification('accountChangedForSource', {
                    'device': device,
                    'notify': notify })
                logger.debug('[Service] [qobuz] accountChanged post notification')
        if eventType == 'logout' and source == self.source:
            if not self.account:
                logger.debug(f'''[Service] [Qobuz] _handleAccountChangedNotify device=={device.uuid} already logout [ignore] this notify''')
                return None
            None.logoutAccount()
            logger.debug(f'''[Service] [Qobuz] _handleAccountChangedNotify device=={device.uuid} logoutAccount because [other app]''')
            logger.debug('[Service] [Qobuz] accountChanged post notification')
            LPUtility.postNotification('accountChangedForSource', {
                'device': device,
                'notify': notify })

    
    def updateMediaInfoWithItem(self, device, item, header = (None,)):
        '''用播放项信息刷新设备上的 mediaInfo。

        :param device: 当前设备对象。
        :param item: 需要写入的 Qobuz 播放项。
        :param header: 兼容父类调用的预留参数。
        :returns: None
        '''
        playSection = getattr(header, 'playSection', None) if header else None
        mediaInfo = {
            'trackId': item.trackId if item.trackId else None,
            'mediaType': LPPublicDefine.MEDIATYPE_NETLIST,
            'playState': 'TRANSITIONING',
            'artworkUri': item.trackImage,
            'trackName': item.trackName if item.trackName else None,
            'artist': item.trackArtist if item.trackArtist else None,
            'artistId': item.artistId if item.artistId else None,
            'albumId': item.albumId if item.albumId else None,
            'album': item.albumName if item.albumName else None,
            'guiBehavior': '{"prev": {"enabled": true},"loop": {"enabled": true}, "shuffle": {"enabled": true}, "seek": {"enabled": true}}',
            'duration': '00:00:00',
            'progress': '00:00:00',
            'trackSource': self.source,
            'playOrigin': getattr(header, 'playOrigin', None),
            'playOriginTrackId': item.trackId if getattr(header, 'playOrigin', None) else None,
            'volume': device.mediaInfo.volume,
            'loopMode': device.mediaInfo.loopMode,
            'playSection': playSection }
        device.setMediaInfo(mediaInfo)

    
    def LPTrackMoreCanPreset(self, device = (None,)):
        '''判断 Qobuz minibar 当前播放菜单是否展示 preset。

        :param device: 当前播放设备。
        :returns: 非搜索单曲播放返回 ``True``。
        '''
        return not self._isSearchTrackPlayback(device)

    
    def recentlyCanPreset(self = None, detailDict = None):
        '''
        判断 Qobuz Recently 卡片条目是否支持保存为 preset。

        Args:
            detailDict: recently 记录中的 detail 字典。

        Returns:
            设备支持预设、队列非搜索单曲且快照可还原时返回 True。
        '''
        return self._recentlyCanPresetForDetail(detailDict)

    
    def canFavorite(self = None, itemType = None, itemId = None):
