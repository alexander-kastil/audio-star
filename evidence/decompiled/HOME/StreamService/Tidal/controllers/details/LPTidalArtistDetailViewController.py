# Source Generated with Decompyle++
# File: LPTidalArtistDetailViewController.pyc (Python 3.9)

'''
TIDAL 艺人详情页控制器。
'''
from typing import Optional
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalSeeAllDescriptor, LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalArtistDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 艺人详情页，负责加载艺人信息、热门曲目、专辑、视频、简介和关联艺人。'''
    
    def __init__(self = None, itemId = None, parent = None):
        '''
        初始化艺人详情页。

        :param itemId: 艺人 ID。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        store = LPTidalStore.instance()
        super().__init__(itemId, 'artist', store.acquireArtistDetailState(itemId), LPUIPath.TidalArtistDetailQML, 'pages/TidalArtistDetail.qml', 'tidalArtistDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取艺人详情数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadArtistDetail(self._item_id)

    
    def updateDetailSectionVisibleRange(self = None, sectionKey = None, firstIndex = pyqtSlot(str, int, int), lastIndex = {
        'sectionKey': str,
        'firstIndex': int,
        'lastIndex': int,
        'return': None }):
        '''
        更新艺人详情页分区可见范围。

        :param sectionKey: 分区标识。
        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        self._state.updateDetailSectionVisibleRange(sectionKey, firstIndex, lastIndex)

    updateDetailSectionVisibleRange = None(updateDetailSectionVisibleRange)
    
    def clearDetailSectionVisibleRange(self = None, sectionKey = None):
        '''
        清理艺人详情页分区可见范围。

        :param sectionKey: 分区标识。
        :return: None。
        '''
        self._state.clearDetailSectionVisibleRange(sectionKey)

    clearDetailSectionVisibleRange = None(clearDetailSectionVisibleRange)
    
    def _descriptorForGenreSection(self = None, sectionKey = None):
        '''
        返回艺人详情页 SeeAll 描述。

        :param sectionKey: 区块标识。
        :return: SeeAll 描述对象或 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        section_map = {
            'artistTopTracks': ('Top Tracks', 'track', f'''/v1/artists/{self._item_id}/toptracks'''),
            'artistAlbums': ('Albums', 'album', f'''/v1/artists/{self._item_id}/albums'''),
            'artistSingles': ('EP & Singles', 'album', f'''/v1/artists/{self._item_id}/albums'''),
            'artistRelated': ('Related Artists', 'artist', f'''/v1/artists/{self._item_id}/related''') }
        config = section_map.get(section_key)
        if config is None:
            return None
        (title, item_type, endpoint_path) = None
        playback_kwargs = { }
        if section_key == 'artistTopTracks':
            if not getattr(self._state, 'detailInfo', { }):
                pass
            detail_info = { }
            detail_info = detail_info if isinstance(detail_info, dict) else { }
            if not self._item_id:
                pass
            if not detail_info.get('imageUrl', ''):
                pass
            playback_kwargs = {
                'itemId': str('').strip(),
                'streamType': 'artist',
                'imageUrl': str('').strip() }
    # WARNING: Decompyle incomplete

    __classcell__ = None

