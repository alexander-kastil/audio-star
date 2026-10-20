# Source Generated with Decompyle++
# File: LPRecentlyManager.pyc (Python 3.9)

'''
Recently Played 的对外管理器。

负责把播放成功后的上下文整理成 ``detail`` 快照并落库，同时提供读取、删除、音源推导等能力。
页面层、音源 StreamService、WiiMHome 主窗口都通过 ``LPRecentlyManager.instance()`` 访问 Recently 数据。

主写入路径：``addRecentlyPlayedWithMusicList(playList, showDict)``
- 从 playList 中提取 header / account / 当前播放项
- 通过 LPRecentlyPlayListCodec 序列化成 detail
- 经 LPMusicLibraryDBManager 写入 SQLite，并裁剪到上限
- 写入成功后发送 ``RecentlyPlayedChangedNotify`` 通知页面刷新

trackId 落库规则：队列型上下文（Collection/Playlist/Album/Artist/Station）按所属列表 id 记录，
同一列表内播放不同曲目只保留一条；单曲（Song）按真实曲目 id 记录。
'''
import threading
import uuid
from LPClientFramework.LPMusicLibrary.LPMusicLibraryDBManager import LPMusicLibraryDBManager, RECENTLY_DIRECTORY_NAME, RECENTLY_DIRECTORY_TYPE
from LPClientFramework.LPMusicLibrary.LPRecentlyPlayListCodec import LPRecentlyPlayListCodec
from LPClientFramework.LPPlayList.LPPlayList import LPAccount, LPPlayListSource, headerTypeEnum, headerTypeValue, LPHeaderType
from LPClientFramework.LPPublicDefine import SOURCES_NO_LOGIN
from LPClientFramework.LPUtility import logger, postNotification
RECENTLY_PLAYED_CHANGED_NOTIFY = 'RecentlyPlayedChangedNotify'
RECENTLY_DEFAULT_LIMIT = 200

class LPRecentlyManager(object):
    '''Recently Played 单例管理器。'''
    _instance = None
    _instanceLock = threading.Lock()
    _QUEUE_DEDUP_TYPE_VALUES = frozenset({
        0,
        1,
        2,
        3,
        4})
    
    def __init__(self):
        self._db = LPMusicLibraryDBManager.instance()
        self._directoryId = self._db.ensureDirectory(RECENTLY_DIRECTORY_NAME, RECENTLY_DIRECTORY_TYPE)
        self._writeLock = threading.Lock()

    
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
    
    def _accountIdentifier(self, account):
        '''从 account 对象推导唯一标识，缺失时回退到匿名标识。'''
        if account is None:
            return 'anonymous'
        if not None(account, 'userId', None):
            pass
        accountId = getattr(account, 'anonUserId', None)
        if accountId:
            return str(accountId)
        userName = None(account, 'userName', None)
        if userName:
            return str(userName)

    
    def _accountDict(self, account, source):
        '''把 account 对象整理成可落库的字典。'''
        if account is None:
            account = LPAccount()
        if not getattr(account, 'source', None):
            pass
        return {
            'accountId': self._accountIdentifier(account),
            'source': source,
            'userId': getattr(account, 'userId', None),
            'userName': getattr(account, 'userName', None),
            'token': getattr(account, 'token', None),
            'refreshToken': getattr(account, 'refreshToken', None) }

    
    def _typeValueFromHeader(self, header):
        '''把 header.headType 归一成可落库的整数。'''
        headType = getattr(header, 'headType', LPHeaderType.LP_HEADER_TYPE_COLLECTION)
        enumValue = headerTypeEnum(headType)
    # WARNING: Decompyle incomplete

    
    def addRecentlyPlayedWithAccount(self, header, playItem, showDict, source, account = (None, None, None)):
        '''
        以单条播放项的形式写入 Recently。

        Args:
            header: 播放上下文 header。
            playItem: 当前播放项。
            showDict: UI 行为信息，例如是否允许 openMore / canNavigate。
            source: 音源标识，为空时回退到 header.mediaSource。
            account: 账号对象，为空时使用空账号。

        Returns:
            写入成功返回 itemId，失败返回 None。
        '''
        if header is None or playItem is None:
            return None
        if not getattr(header, 'playOrigin', ''):
            pass
        if None('') == 'search_track':
            logger.debug('[RecentlyManager] addRecentlyPlayedWithAccount ignore because playOrigin is search_track')
            return None
        if not None and getattr(header, 'mediaSource', None):
            pass
        resolvedSource = getattr(playItem, 'trackSource', None)
        accountDict = self._accountDict(account, resolvedSource)
        showDict = dict(showDict) if showDict else { }
        detail = {
            'header': LPRecentlyPlayListCodec._objectToDict(header),
            'item': LPRecentlyPlayListCodec._objectToDict(playItem),
            'show': showDict,
            'account': accountDict }
        return self._writeRecentlyItem(detail, header, playItem, showDict, accountDict, resolvedSource)

    
    def addRecentlyPlayedWithMusicList(self, playList, showDict = (None,)):
        '''
        Recently 的主写入路径：把完整播放列表快照写入。

        会优先使用 ``playList.header`` / ``playList.account`` / ``playList.list[playList.index]``。

        Args:
            playList: 具体音源的播放列表对象。
            showDict: UI 行为信息。

        Returns:
            写入成功返回 itemId，失败返回 None。
        '''
        if playList is None:
            return None
        header = None(playList, 'header', None)
        if header is None:
            logger.debug('[RecentlyManager] addRecentlyPlayedWithMusicList ignore because header is empty')
            return None
        if not getattr(header, 'playOrigin', ''):
            pass
        if None('') == 'search_track':
            logger.debug('[RecentlyManager] addRecentlyPlayedWithMusicList ignore because playOrigin is search_track')
            return None
        if not None(playList, 'list', None):
            pass
        itemList = []
        if not itemList:
            logger.debug('[RecentlyManager] addRecentlyPlayedWithMusicList ignore because list is empty')
            return None
        currentIndex = None.currentItemFromPlayList(playList)
        currentItem = currentIndex if currentIndex is not None else itemList[0]
        if not getattr(header, 'mediaSource', None) and getattr(currentItem, 'trackSource', None):
            pass
        source = getattr(getattr(playList, 'account', None), 'source', None)
        accountDict = self._accountDict(getattr(playList, 'account', None), source)
        showDict = dict(showDict) if showDict else { }
        detail = LPRecentlyPlayListCodec.playListToDetail(playList, showDict)
        return self._writeRecentlyItem(detail, header, currentItem, showDict, accountDict, source)

    
    def _writeRecentlyItem(self, detail, header, currentItem, showDict, accountDict, source):
        '''整理 LibMusicItem 字段并写入 DB；队列型记录按列表 id 去重，成功后发送通知。'''
        typeValue = self._typeValueFromHeader(header)
        headId = getattr(header, 'headId', None)
        if typeValue in self._QUEUE_DEDUP_TYPE_VALUES and headId:
            trackId = str(headId)
        elif not getattr(currentItem, 'trackId', None):
            pass
        trackId = headId
        headerImageUrl = getattr(header, 'imageUrl', None)
        isCollectionContext = typeValue == headerTypeValue(LPHeaderType.LP_HEADER_TYPE_COLLECTION)
        if isCollectionContext:
            pass
        elif not headerImageUrl:
            pass
        recentlyTrackImage = getattr(currentItem, 'trackImage', None)
        if not getattr(header, 'headTitle', None):
            pass
        itemDict = {
            'itemId': '%s_%s_%s' % (self._directoryId, accountDict.get('accountId'), trackId),
            'directoryId': self._directoryId,
            'accountId': accountDict.get('accountId'),
            'source': source,
            'trackName': getattr(currentItem, 'trackName', None),
            'trackId': trackId,
            'trackImage': recentlyTrackImage,
            'trackArtist': getattr(currentItem, 'trackArtist', None),
            'typeValue': typeValue,
            'openMore': bool(showDict.get('openMore', False)),
            'canNavigate': bool(showDict.get('canNavigate', False)),
            'checkDuplicate': bool(showDict.get('checkDuplicate', True)),
            'detail': detail }
        with self._writeLock:
            self._db.upsertAccount(accountDict)
            itemId = self._db.addRecentlyItem(self._directoryId, RECENTLY_DIRECTORY_NAME, RECENTLY_DIRECTORY_TYPE, itemDict)
            headerImageUrl(None, None, None)
        with None:
            if not headerImageUrl:
                pass
        None if not trackId else getattr(currentItem, 'trackId', None)
        if itemId:
            postNotification(RECENTLY_PLAYED_CHANGED_NOTIFY, None)
        return itemId

    
    def getRecentlyRawList(self, limit = (RECENTLY_DEFAULT_LIMIT,)):
        '''
        读取原始 Recently 记录。

        Args:
            limit: 最多返回的条数，默认 ``200``；传入 ``-1`` 返回全部。

        Returns:
            原始字典列表，按 createTime 倒序。
        '''
        return self._db.getRecentlyItems(self._directoryId, limit)

    
    def deleteRecentlyItems(self, itemIds):
        '''
        按 itemId 批量删除 Recently 记录，删除后发送变更通知。

        Args:
            itemIds: 待删除的 itemId 列表。
        '''
        if not itemIds:
            return None
        None._db.deleteRecentlyItems(self._directoryId, itemIds)
        postNotification(RECENTLY_PLAYED_CHANGED_NOTIFY, None)

    
    def sourceFromDetail(self, detailDict):
