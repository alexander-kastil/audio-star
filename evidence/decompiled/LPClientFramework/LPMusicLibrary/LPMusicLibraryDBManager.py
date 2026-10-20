# Source Generated with Decompyle++
# File: LPMusicLibraryDBManager.pyc (Python 3.9)

'''
Music Library 的 SQLite 持久化层。

当前主要服务于 Recently Played：把账号、目录、播放项分别落到 ``LibAccount`` / ``LibMusicList`` / ``LibMusicItem``
三张表，并提供按目录读写、去重裁剪、删除等能力。

约束（与文档一致）：
- Recently 使用的目录标识：``directoryName = "recently"``，``directoryType = "favorite"``
- 整个 Recently 目录最多保留 ``RECENTLY_MAX_COUNT`` 条
- ``checkDuplicate`` 为真时，会先删除同目录、同账号、同 trackId 的旧记录
'''
import json
import threading
from datetime import datetime
from LPClientFramework import LPMusicDatabase
from LPClientFramework.LPUtility import logger
RECENTLY_DIRECTORY_NAME = 'recently'
RECENTLY_DIRECTORY_TYPE = 'favorite'
RECENTLY_MAX_COUNT = 500

class LPMusicLibraryDBManager(object):
    '''Music Library 的单例 DB 管理器，封装 SQLite 读写与线程锁。'''
    _instance = None
    _instanceLock = threading.Lock()
    
    def __init__(self):
        self._dbPath = str(LPMusicDatabase.databasePath())
        self._lock = threading.RLock()
        self._initDb()

    
    def databasePath(self):
        '''返回 Recently 使用的共享主库路径。

        参数:
            无。
        返回:
            str: 共享主库文件路径。
        '''
        return self._dbPath

    
    def instance(cls):
        if cls._instance is None:
            with cls._instanceLock:
                if cls._instance is None:
                    cls._instance = cls()
                None(None, None, None)
            with None:
                if not None:
                    pass
        return cls._instance

    instance = classmethod(instance)
    
    def _connect(self):
        '''创建共享主库连接；PRAGMA 与 busy_timeout 由 LPMusicDatabase 统一设置。

        参数:
            无。
        返回:
            sqlite3.Connection: 主库连接。
        '''
        return LPMusicDatabase.connect(self._dbPath)

    
    def _initDb(self):
        pass
    # WARNING: Decompyle incomplete

    
    def ensureDirectory(self, directoryName, directoryType, accountId, source = (None, None)):
        '''
        确保指定目录存在，返回 directoryId。

        directoryId 用 ``directoryName`` 直接表示，保证同一类目录全局唯一。
        '''
        directoryId = directoryName
    # WARNING: Decompyle incomplete

    
    def upsertAccount(self, accountDict):
        '''写入或更新账号记录，accountDict 至少需要包含 accountId。'''
        if not isinstance(accountDict, dict) or accountDict.get('accountId'):
            return None
    # WARNING: Decompyle incomplete

    
    def _nowTimestamp():
        return int(datetime.now().timestamp())

    _nowTimestamp = staticmethod(_nowTimestamp)
    
    def addRecentlyItem(self, directoryId, directoryName, directoryType, itemDict):
        '''
        写入一条 Recently 记录。

        itemDict 需要包含的字段与 ``LibMusicItem`` 对应，detail 字段会被 JSON 序列化。
        当 ``checkDuplicate`` 为真时，会先删除同目录、同账号、同 trackId 的旧记录。
        写入后会裁剪到 ``RECENTLY_MAX_COUNT`` 条。
        '''
        if not isinstance(itemDict, dict):
            return None
        itemId = None.get('itemId')
        if not itemId:
            if not itemDict.get('accountId'):
                pass
            if not itemDict.get('trackId'):
                pass
            itemId = '%s_%s_%s' % (directoryId, '', '')
        if not itemDict.get('createTime'):
            pass
        createTime = self._nowTimestamp()
        if not itemDict.get('detail'):
            pass
        detailStr = json.dumps({ }, False, **('ensure_ascii',))
    # WARNING: Decompyle incomplete

    
    def getRecentlyItems(self, directoryId, limit = (200,)):
        '''
        按 createTime 倒序读取 Recently 记录。

        Args:
            directoryId: 目录标识，通常是 ``recently``。
            limit: 最多返回的条数；``-1`` 表示返回全部。

        Returns:
            字典列表，每项的字段与 ``LibMusicItem`` 对齐，detail 已反序列化。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def deleteRecentlyItems(self, directoryId, itemIds):
        '''按 itemId 批量删除 Recently 记录。'''
        if not itemIds:
            return None
        itemIdList = (lambda 