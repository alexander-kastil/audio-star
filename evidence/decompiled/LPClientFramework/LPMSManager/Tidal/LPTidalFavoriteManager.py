# Source Generated with Decompyle++
# File: LPTidalFavoriteManager.pyc (Python 3.9)

'''
TIDAL 收藏管理器。
'''
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPFavoriteCacheManager import LPFavoriteCacheManager
from LPClientFramework.LPUtility import logger

class LPTidalFavoriteManager(QObject):
    '''负责同步收藏 ID、拉取收藏列表和执行收藏切换。'''
    
    def __init__(self = None, parent = None):
        '''
        初始化收藏管理器。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPTidalStore.instance()
        self._provider = LPTidalDataProvider()

    
    def requestFavoriteIds(self = None, userId = None, countryCode = None, skipCache = ('', False)):
