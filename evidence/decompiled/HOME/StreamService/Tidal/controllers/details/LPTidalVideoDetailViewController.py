# Source Generated with Decompyle++
# File: LPTidalVideoDetailViewController.pyc (Python 3.9)

'''
TIDAL 视频详情页控制器。
'''
from typing import Optional
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalVideoDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 视频详情页，负责加载视频信息和推荐视频。'''
    
    def __init__(self = None, itemId = None, parent = None):
        '''
        初始化视频详情页。

        :param itemId: 视频 ID。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        store = LPTidalStore.instance()
        super().__init__(itemId, 'video', store.acquireVideoDetailState(itemId), LPUIPath.TidalVideoDetailQML, 'pages/TidalVideoDetail.qml', 'tidalVideoDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取视频详情数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadVideoDetail(self._item_id)

    __classcell__ = None

