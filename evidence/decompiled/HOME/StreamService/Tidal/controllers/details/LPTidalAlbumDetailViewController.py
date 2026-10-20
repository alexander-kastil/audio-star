# Source Generated with Decompyle++
# File: LPTidalAlbumDetailViewController.pyc (Python 3.9)

'''
TIDAL 专辑详情页控制器。
'''
from typing import Optional
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalSeeAllDescriptor, LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalAlbumDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 专辑详情页，负责加载专辑信息、曲目、评论、制作名单和相似专辑。'''
    
    def __init__(self = None, itemId = None, parent = None):
        '''
        初始化专辑详情页。

        :param itemId: 专辑 ID。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        store = LPTidalStore.instance()
        super().__init__(itemId, 'album', store.acquireAlbumDetailState(itemId), LPUIPath.TidalAlbumDetailQML, 'pages/TidalAlbumDetail.qml', 'tidalAlbumDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取专辑详情数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadAlbumDetail(self._item_id)

    
    def updateAlbumTrackVisibleRange(self = None, firstIndex = None, lastIndex = pyqtSlot(int, int)):
        '''
        更新专辑曲目可见范围。

        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        self._state.updateTrackVisibleRange(firstIndex, lastIndex)

    updateAlbumTrackVisibleRange = None(updateAlbumTrackVisibleRange)
    
    def _descriptorForGenreSection(self = None, sectionKey = None):
        '''
        返回专辑详情页动态横向区块的 SeeAll 描述。

        :param sectionKey: 区块标识。
        :return: SeeAll 描述对象或 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not section_key or hasattr(self._state, 'sectionInfo'):
            return None
        section_info = None._state.sectionInfo(section_key)
        if not isinstance(section_info, dict):
            return None
        if not section_info.get('title', ''):
            pass
        title = None('').strip()
        if not section_info.get('itemType', 'album'):
            pass
        item_type = str('album').strip().lower()
        if not section_info.get('endpointPath', ''):
            pass
        endpoint_path = str('').strip()
        if not title and item_type or endpoint_path:
            return None
        return None(section_key, title, item_type, endpoint_path, 'detail', section_info.get('queryParams', { }), section_info.get('excludeItemIds', []), **('sectionKey', 'title', 'itemType', 'endpointPath', 'sourceKind', 'queryParams', 'excludeItemIds'))

    __classcell__ = None

