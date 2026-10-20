# Source Generated with Decompyle++
# File: LPTidalArtistRadioDetailViewController.pyc (Python 3.9)

'''
TIDAL 艺人电台详情页控制器。
'''
from typing import Optional
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalArtistRadioDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 艺人电台详情页，负责加载艺人电台曲目和播放控制。'''
    
    def __init__(self = None, itemId = None, parent = None):
        '''
        初始化艺人电台详情页。

        :param itemId: 艺人 ID。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        store = LPTidalStore.instance()
        super().__init__(itemId, 'artist_radio', store.acquireArtistRadioDetailState(itemId), LPUIPath.TidalArtistRadioDetailQML, 'pages/TidalArtistRadioDetail.qml', 'tidalArtistRadioDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取艺人电台数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadArtistRadio(self._item_id)

    __classcell__ = None

