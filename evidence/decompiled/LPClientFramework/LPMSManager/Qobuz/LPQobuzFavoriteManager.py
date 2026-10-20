# Source Generated with Decompyle++
# File: LPQobuzFavoriteManager.pyc (Python 3.9)

'''
@Time ： 2025/8/19 17:45
@Auth ： Chris
@File ：LPQobuzFavoriteManager.py
@Desc:
'''
import time
from PyQt6.QtCore import QObject, pyqtSignal
import LPGlobalUI
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType, LPPlayListSource
from LPClientFramework.LPUtility import logger

class LPQobuzFavoriteManager(QObject):
    favLoadSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.qobuz = parent
        self.qobuz.libCacheMgr.libPlaylistLoadedSignal.connect(self.onPlaylistLoad)
        self.favIds = None
        self.playlistIds = None
        self.favLoadSignal.connect(self.onFavLoaded)
        self._registerCacheProjection()

    
    def _registerCacheProjection(self):
        '''注册 Qobuz 收藏缓存投影回调，缓存变化时同步 favIds/playlistIds。'''
        LPFavoriteCacheManager = LPFavoriteCacheManager
        import LPClientFramework.LPFavoriteCacheManager
        LPFavoriteCacheManager.instance().setProjectionCallback('Qobuz', self._onCacheChanged)

    
    def _onCacheChanged(self, source, userId, ids):
        '''缓存变化回调：与当前账号一致时刷新投影并通知页面。'''
        if source != 'Qobuz':
            return None
        account = None.qobuz.currentAccount
        if not getattr(account, 'userId', ''):
            pass
        currentUserId = str('').strip()
        if currentUserId:
            if not userId:
                pass
            if currentUserId != str('').strip():
                return None
            if not ids:
                pass
        self.favIds = (lambda 