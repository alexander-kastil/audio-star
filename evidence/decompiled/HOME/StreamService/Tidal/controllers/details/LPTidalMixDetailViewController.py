# Source Generated with Decompyle++
# File: LPTidalMixDetailViewController.pyc (Python 3.9)

'''
TIDAL Mix 详情页控制器。
'''
from typing import Any, Optional
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPConfig import LPUIPath

class LPTidalMixDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL Mix 详情页，负责加载 Mix 曲目和播放控制。'''
    
    def __init__(self = None, itemId = None, itemTitle = None, itemSubtitle = None, itemImageUrl = None, parent = None):
        store = LPTidalStore.instance()
        state = store.acquireMixDetailState(itemId)
        super().__init__(itemId, 'mix', state, LPUIPath.TidalMixDetailQML, 'pages/TidalMixDetail.qml', 'tidalMixDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))
        if itemTitle or itemImageUrl:
            self._pending_mix_meta = {
                'title': itemTitle,
                'subtitle': itemSubtitle,
                'imageUrl': itemImageUrl }
        else:
            self._pending_mix_meta = None

    
    def _fetchDetailData(self):
        return self._provider.loadMixDetail(self._item_id)

    
    def _handleDetailResult(self = None, result = None):
        super()._handleDetailResult(result)
        if self._pending_mix_meta:
            info = dict(self._state.detailInfo)
            info.update((lambda .0: pass# WARNING: Decompyle incomplete
)(self._pending_mix_meta.items()))
            self._state._ensureDetailThumbnail(info)
            self._state._detailInfo = info
            self._state.detailInfoChanged.emit()
            self._pending_mix_meta = None

    __classcell__ = None

