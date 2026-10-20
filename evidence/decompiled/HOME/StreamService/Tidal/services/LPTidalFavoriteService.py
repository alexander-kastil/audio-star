# Source Generated with Decompyle++
# File: LPTidalFavoriteService.pyc (Python 3.9)

'''
TIDAL 收藏写操作服务。
'''
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import QCoreApplication, QObject
import LPGlobalUI
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest, LPTidalRequestScheduler
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPFavoriteCacheManager import LPFavoriteCacheManager
from LPClientFramework.LPMSManager.Tidal.LPTidalFavoriteManager import LPTidalFavoriteManager
from LPClientFramework.LPUtility import logger
FAVORITE_PENDING_TIMEOUT_SECONDS = 60

def toastFavoriteResult(result = None):
    '''
    用全局 Toast 展示收藏操作结果。

    供页面已离场（无法再用页面内 Toast）时兜底，保证收藏失败不静默。

    :param result: 收藏结果字典。
    :return: None。
    '''
    if not isinstance(result, dict):
        return None
    success = None(result.get('success'))
    desired_favorite = bool(result.get('desiredFavorite', False))
    if success:
        message = QCoreApplication.translate('Qobuz Favorite', 'Added to Favorites' if desired_favorite else 'Removed From Favorites')
    elif desired_favorite:
        pass
    
    message = 'Qobuz Favorite'('Add Failed', 'Remove Failed')
    toast = getattr(LPGlobalUI, 'toast', None)
    if toast is None:
        return None
    QCoreApplication.translate.showToast(message, getattr(LPGlobalUI, 'mainWindow', None))


class LPTidalFavoriteService(QObject):
    '''TIDAL 收藏写操作唯一编排者，负责乐观更新、常驻调度、提交与失败回滚。

    该服务是进程级单例，调度器不随 TIDAL 页面销毁而关闭：页面只负责发起与展示，
    已确认的收藏结果一定写入通用缓存与 Store，避免页面离场丢弃回调导致状态长期不一致。
    '''
    _instance = None
    
    def instance(cls):
        '''
        返回 TIDAL 收藏写服务的全局单例。

        :return: LPTidalFavoriteService 实例。
        '''
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    instance = classmethod(instance)
    
    def __init__(self = None, parent = None):
        '''
        初始化收藏管理器与常驻异步请求调度器。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._manager = LPTidalFavoriteManager(self)
        self._scheduler = LPTidalRequestScheduler(self)

    
    def setFavorite(self = None, itemType = None, itemId = None, desiredFavorite = (None,), callback = {
        'itemType': str,
        'itemId': str,
        'desiredFavorite': bool,
        'callback': Optional[Callable[([
            Dict[(str, Any)]], None)]],
        'return': None }):
        '''
        异步设置指定条目收藏状态。

        先做乐观更新，再经常驻调度器请求服务端；成功后提交服务端收藏 ID 到通用缓存与
        Store 并广播 Collection 变化，失败时回滚本地状态并回调结果。

        :param itemType: 条目类型。
        :param itemId: 条目 ID。
        :param desiredFavorite: 目标收藏状态。
        :param callback: 可选结果回调（仅用于调用方的页面内 UI 展示，不承担状态提交），
            参数为结果字典，含 success/error/itemType/itemId/desiredFavorite/wasFavorite。
        :return: None。
        '''
        store = LPTidalStore.instance()
        account = store.accountState
        if not account.get('userId', ''):
            pass
        userId = str('').strip()
        if not itemType:
            pass
        normalized_type = str('').strip().lower()
        if not itemId:
            pass
        normalized_id = str('').strip()
        result_prefix = {
            'itemType': normalized_type,
            'itemId': normalized_id,
            'desiredFavorite': bool(desiredFavorite) }
    # WARNING: Decompyle incomp