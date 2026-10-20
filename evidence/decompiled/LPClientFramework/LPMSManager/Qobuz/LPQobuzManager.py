# Source Generated with Decompyle++
# File: LPQobuzManager.pyc (Python 3.9)

'''
@Time ： 2025/8/5 11:15
@Auth ： Chris
@File ：LPQobuzManager.py
@Desc:
'''
import threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework import LPUtility
from LPClientFramework.LPCache.LPFileCache import FileCache
from LPClientFramework.LPCache.LPPickleCache import LPPickleCache
from LPClientFramework.LPMSManager.Qobuz.LPQobuzFavoriteManager import LPQobuzFavoriteManager
from LPClientFramework.LPMSManager.Qobuz.LPQobuzLibraryCacheManager import LPQobuzLibraryCacheManager
from LPClientFramework.LPMSManager.Qobuz.LPQobuzLoginManager import LPQobuzLoginManager
from LPClientFramework.LPMSManager.Qobuz.LPQobuzRequestManager import LPQobuzRequestManager
from LPClientFramework.LPNetworkClient.LPQobuz.LPQobuzNetworkClient import LPQobuzNetworkClient
from LPClientFramework.LPNetworkClient.LPQobuz.LPQobuzRequester import LPQobuzRequester
from LPClientFramework.LPNetworkClient.LPQobuz.LPQobuzTokenProvider import LPQobuzTokenProvider
from LPClientFramework.LPUtility import logger

class LPQobuzManager(QObject):
    _instance = None
    _initialized = False
    favIdsReadySignal = pyqtSignal()
    lastUpdateTimeReadySignal = pyqtSignal(object, object)
    categoryListReadySignal = pyqtSignal()
    
    def instance(cls, parent = (None,)):
        if cls._instance is None:
            cls._instance = cls(parent)
            cls._instance._initialized = True
        return cls._instance

    instance = classmethod(instance)
    
    def __init__(self = None, parent = None):
        if getattr(self, '_initialized', False):
            return None
        None().__init__(parent)
        self._init()
        self._initialized = True

    
    def _init(self):
        tokenProvider = LPQobuzTokenProvider()
        client = LPQobuzNetworkClient(tokenProvider)
        self.requestMgr = LPQobuzRequestManager(LPQobuzRequester(client))
        self.loginMgr = LPQobuzLoginManager()
        self.loginMgr.tokenProvider = tokenProvider
        self.loginMgr.initAccountAboutSignal.connect(self.initAccountAbout)
        self.libCacheMgr = LPQobuzLibraryCacheManager(self)
        self.favMgr = LPQobuzFavoriteManager(self)
        self.pklCache = LPPickleCache()
        self.fileCache = FileCache(LPUtility.cacheDir / 'Qobuz')
        self.favoriteIds = None
        self.favoriteIdsCondition = threading.Condition()
        self.lastUpdateTime = None
        self.lastUpdateTimeCondition = threading.Condition()
        self.categoryList = None
        self.playlistCategoryPath = LPUtility.cacheDir / 'Qobuz' / 'categoryList.pkl'

    
    def getPlaylistCategory(self):
        data = self.pklCache.tryLoad(self.playlistCategoryPath, None)
        if data:
            self.categoryList = data
            self.categoryListReadySignal.emit()
        else:
            
            def callback(result = None):
                self.categoryList = result.data
                self.pklCache.save(self.playlistCategoryPath, self.categoryList)
                self.categoryListReadySignal.emit()

            reqFunc = self.requestMgr.fetchTagsData
            self.requestMgr.fetch(reqFunc, callback)

    
    def getCacheDir(self):
        if not self.loginMgr.account:
            return None
        userId = self.loginMgr.account.userId
        print(f'''userid=={userId}''')
        filePath = LPUtility.cacheDir / 'SS' / 'Qobuz' / str(userId)
        filePath = Path(filePath).resolve()
        filePath.mkdir(True, True, **('parents', 'exist_ok'))
        :
            if not self.loginMgr.account:
                return None
            userId = self.loginMgr.account.userId
            print(f'''userid=={userId}''')
            filePath = LPUtility.cacheDir / 'SS' / 'Qobuz' / str(userId)
            filePath = Path(filePath).resolve()
            filePath.mkdir(True, True, **('parents', 'exist_ok'))
            
            return filePath
        return filePath
    # WARNING: Decompyle incomplete

    
    def initAccountAbout(self):
        logger.debug('qobuz manager initAccountAbout')
        self.requestMgr.requester.client.token = self.currentAccount.token if self.currentAccount.token else None
        self.libCacheMgr.initLibCache(self.currentAccount)
        self.favMgr.initFavIds()

    
    def currentAccount(self):
        '''返回当前登录的Qobuz Account 对象'''
        return self.loginMgr.account

    currentAccount = property(currentAccount)
    __classcell__ = None

