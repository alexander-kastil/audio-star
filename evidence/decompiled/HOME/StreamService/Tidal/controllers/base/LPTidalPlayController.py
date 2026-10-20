# Source Generated with Decompyle++
# File: LPTidalPlayController.pyc (Python 3.9)

'''
TIDAL 播放推送控制器。
'''
import random
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import LPGlobalUI
from PyQt6.QtCore import QCoreApplication, pyqtSlot
from HOME.StreamService.Tidal.config.LPTidalImageConfig import LPTidalImageSize, buildTidalImageUrl
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.models.LPTidalListModel import LPTidalListModel
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalSeeAllDescriptor, LPTidalStore
from LPClientFramework import LPUtility
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPMusicLibrary.LPRecentlyManager import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType, LPPlayListSource, headerTypeValue
from LPClientFramework.LPPlayList.LPTidalPlayList import LPTidalAccount, LPTidalPlayHeader, LPTidalPlayItem, LPTidalPlayList, TIDAL_FAVORITE_TRACKS_ID, TIDAL_FAVORITE_TRACKS_TITLE, tidalPlayingContextForPlaylist, tidalRecentlyNavigationType
from LPClientFramework.LPShuffleManager import LPShuffleManager
from LPClientFramework.LPUtility import logger

def seeAllPlaybackIdentity(descriptor = None):
    '''
    解析 See All 描述对应的队列 ID、StreamType 与封面。

    普通 See All 用 sectionKey 作队列 ID、collection 作类型；artist Top Tracks 这类
    带真实 itemId 的 track See All 用真实 ID 与详情页同款 StreamType 和封面，保证
    写入 Recently 的快照与详情页播放一致，避免 Recently 恢复时用伪 sectionKey 误
    导航到空详情页，封面也不会回退成首曲封面。

    :param descriptor: LPTidalSeeAllDescriptor 或兼容对象。
    :return: `(listId, streamType, imageUrl)`；缺省时分别为 sectionKey、"collection" 与空串。
    '''
    if descriptor is None:
        return ('', 'collection', '')
    if not getattr(descriptor, 'itemId', ''):
        pass
    list_id = None('').strip()
    if not list_id:
        if not getattr(descriptor, 'sectionKey', ''):
            pass
        list_id = str('').strip()
        if list_id == 'favoriteTracks':
            list_id = TIDAL_FAVORITE_TRACKS_ID
    if not getattr(descriptor, 'streamType', ''):
        pass
    stream_type = str('').strip()
    if not stream_type:
        stream_type = 'collection'
    if not getattr(descriptor, 'imageUrl', ''):
        pass
    image_url = str('').strip()
    return (list_id, stream_type, image_url)


class LPTidalPlayController:
    '''TIDAL 播放逻辑 Mixin，统一处理设备队列推送与播放态同步。'''
    _source: str = LPPlayListSource.Tidal.value
    _tidal_api_base_url: str = 'https://api.tidal.com'
    _upnp_model: Optional[LPUpnpAsyncDataModel] = None
    
    def guardTidalSupported(self = None):
        '''
        校验当前设备是否支持 TIDAL。

        :param: 无。
        :return: 支持返回 True，否则返回 False。
        '''
        if self.isCurrentDeviceSupportTidal():
            return True
        None.debug("[TIDAL][Play] current device doesn't support TIDAL")
        self._showToast(QCoreApplication.translate('Tidal', 'Current Device Does Not Support TIDAL. Please Upgrade the Firmware to get support.'))
        return False

    
    def isCurrentDeviceSupportTidal(self = None):
        '''
        判断当前设备 capability 是否声明支持 TIDAL。

        :param: 无。
        :return: 支持返回 True，否则返回 False。
        '''
        device = getattr(LPGlobalUI, 'currentDevice', None)
        manager = getattr(device, 'deviceStreamServiceManager', None)
        capability = getattr(manager, 'streamServiceCapability', None) if manager is not None else None
        if isinstance(capability, dict):
            pass
        return self._source in capability.keys()

    
    def guardTidalLoggedIn(self = None):
        '''
        校验 TIDAL 是否已登录。

        :param: 无。
        :return: 已登录返回 True，否则返回 False。
        '''
        device = getattr(LPGlobalUI, 'currentDevice', None)
    # WARNING: Decompyle incomplete

    
    def playTidalHomeTrack(self = None, sectionKey = None, itemId = None):
        '''
        播放首页区块中的曲目。

        :param sectionKey: 首页区块标识。
        :param itemId: 曲目 ID。
        :return: 成功发起播放返回 True。
        '''
        self._tidal_play_source = 'home'
        state = getattr(self, '_state', None)
        (section_key, section, model) = self._homeSectionForTrack(state, sectionKey, itemId)
        if model is None:
            logger.debug('[TIDAL][Play] home track not found itemId=%s section=%s', itemId, sectionKey)
            return False
        search_url = None._searchUrlForHomeSection(section_key)
        title = str('TIDAL') if isinstance(section, dict) else 'TIDAL'
        return self.playTidalTrackFromModel(model, itemId, search_url, title, section_key, 'collection', **('search_url', 'listTitle', 'listId', 'streamType'))

    
    def playTidalSearchTrack(self = None, itemId = None):
        '''
        播放搜索结果中的曲目。

        :param itemId: 曲目 ID。
        :return: 成功发起播放返回 True。
        '''
        self._tidal_play_source = 'search'
        state = getattr(self, '_state', None)
        track_model = getattr(state, 'trackResults', None)
        top_model = getattr(state, 'topResults', None)
        if not getattr(state, 'searchFilter', ''):
            pass
        search_filter = str('').strip().lower()
        if search_filter == 'top':
            model = top_model
            fallback_model = track_model
            list_title = 'Top'
            list_id = 'TIDAL SEARCH Top'
        else:
            model = track_model
            fallback_model = top_model
            list_title = 'TIDAL SEARCH'
            list_id = 'TIDAL SEARCH Tracks'
        if self._modelContainsItem(model, itemId) and self._modelContainsItem(fallback_model, itemId):
            model = fallback_model
            if model is top_model:
                list_title = 'Top'
                list_id = 'TIDAL SEARCH Top'
            else:
                list_title = 'TIDAL SEARCH'
                list_id = 'TIDAL SEARCH Tracks'
        item = self._itemFromModelById(model, itemId)
        if not isinstance(item, dict):
            return False
        queue_search_url = None._queueSearchUrlForItem(item, '')
        if not queue_search_url:
            return False
        return None.playTidalTrackFromModel([
            item], itemId, queue_search_url, list_title, list_id, 'song', 1, True, **('search_url', 'listTitle', 'listId', 'streamType', 'startPlayIndex', 'allowInlineTracks'))

    
    def playTidalCollectionTrack(self = None, sectionKey = None, itemId = None):
