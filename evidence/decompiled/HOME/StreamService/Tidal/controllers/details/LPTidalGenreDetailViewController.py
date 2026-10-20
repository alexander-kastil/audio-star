# Source Generated with Decompyle++
# File: LPTidalGenreDetailViewController.pyc (Python 3.9)

'''
TIDAL 流派和心情详情页控制器。
'''
from typing import Optional
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.controllers.pages.LPTidalSeeAllViewController import LPTidalSeeAllViewController
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalGenreDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 流派或心情详情页，负责加载分类下的歌单、曲目和专辑。'''
    
    def __init__(self = None, itemId = None, title = None, parent = None, categoryType = None):
        '''
        初始化流派或心情详情页。

        :param itemId: 分类路径、slug 或 ID。
        :param title: 首页分类卡片带入的展示标题。
        :param parent: 父级 QWidget。
        :param categoryType: 分类类型，支持 genre 或 mood。
        :return: None。
        '''
        if not title:
            pass
        self._genre_title = str('').strip()
        if not categoryType:
            pass
        self._category_type = str('genre').strip().lower()
        if self._category_type not in frozenset({'genre', 'mood'}):
            self._category_type = 'genre'
        store = LPTidalStore.instance()
        state = store.acquireMoodDetailState(itemId) if self._category_type == 'mood' else store.acquireGenreDetailState(itemId)
        super().__init__(itemId, self._category_type, state, LPUIPath.TidalGenreDetailQML, 'pages/TidalGenreDetail.qml', 'tidalGenreDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取流派或心情详情数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadGenreDetail(self._item_id, self._genre_title, self._category_type, **('title', 'categoryType'))

    
    def _genreTitle(self = None):
        '''
        返回分类展示标题。

        :return: 分类标题。
        '''
        detail_info = getattr(self._state, 'detailInfo', { })
        if isinstance(detail_info, dict):
            if not detail_info.get('title', ''):
                pass
            title = str('').strip()
            if title:
                return title
            if not None._genre_title:
                pass
        return self._item_id

    
    def _descriptorForGenreSection(self = None, sectionKey = None):
        '''
        根据流派或心情详情 section 创建 See All 描述。

        :param sectionKey: 分类详情 section 标识。
        :return: See All 描述对象或 None。
        '''
        if self._category_type == 'mood':
            return LPTidalSeeAllViewController.descriptorForMoodSection(self._item_id, self._genreTitle(), sectionKey, **('moodId', 'moodTitle', 'sectionKey'))
        return None.descriptorForGenreSection(self._item_id, self._genreTitle(), sectionKey, **('genreId', 'genreTitle', 'sectionKey'))

    __classcell__ = None

