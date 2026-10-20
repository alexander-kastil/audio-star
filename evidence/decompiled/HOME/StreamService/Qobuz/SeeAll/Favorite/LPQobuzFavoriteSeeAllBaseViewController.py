# Source Generated with Decompyle++
# File: LPQobuzFavoriteSeeAllBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/8/5 17:23
@Auth ： Chris
@File ：LPQobuzFavoriteSeeAllBaseViewController.py
@Desc:
'''
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, Qt
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger

class LPQobuzFavoriteSeeAllBaseViewController(LPQobuzSeeAllBaseViewController):
    updateFavoriteSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.offset = 0
        self.total = self.defaultTotal
        self.limit = self.defaultLimit
        self.itemId = None
        self.itemType = None
        self.playItem = None
        self.playList = None
        self.loadDataSignal.connect(self._loadData)
        self.onFavClickedMethod = None
        self.pageName = None
        self.updateFavoriteSignal.connect(self._updateFavorite)
        self.section = None
        self.qobuz.libCacheMgr.libCacheChangedSignal.connect(self.onSectionDataChanged)

    
    def onSectionDataChanged(self, account, sectionKey):
        currentAccount = self.qobuz.currentAccount
        if account is None or currentAccount is None:
            return None
        if None.userId != currentAccount.userId:
            return None
        if None != self.section:
            return None
        None.loadData()

    
    def _updateFavorite(self):
        pass

    _updateFavorite = pyqtSlot()(_updateFavorite)
    
    def _loadData(self, genres, binding):
        pass

    _loadData = pyqtSlot(object, object)(_loadData)
    
    def loadDataFromCache(self, data):
        pass

    
    def loadData(self):
        currentAccount = self.qobuz.currentAccount
        if currentAccount is None:
            return None
        dataBinding = None.dataBinding[self.section]
        self.playList = dataBinding['playList']
        if not self.playList:
            cachedPlayList = self.qobuz.libCacheMgr.loadCache(currentAccount, self.section)
            if cachedPlayList:
                logger.debug('[loadData] fallback to local loadCache')
                dataBinding['playList'] = cachedPlayList
                self.playList = cachedPlayList
        if self.playList:
            logger.debug('[loadData] data from cache')
            self.loadDataFromCache(self.playList)

    
    def saveSortType(self, key, sortType):
        settings = LPUtility.settings
        account = self.qobuz.currentAccount
        if account is None:
            return None
        userId = None.userId
        if not userId:
            return None
        None.beginGroup(f'''{LPPlayListSource.Qobuz.value}/{userId}''')
        settings.setValue(key, sortType)
        settings.endGroup()
        logger.debug(f'''[Qobuz Fav See all] saveSortType key={key} key={sortType}''')

    
    def getSortType(self, key):
        pass
    # WARNING: Decompyle incomplete

    __classcell__ = None

