# Source Generated with Decompyle++
# File: LPQobuzGenreManager.pyc (Python 3.9)

'''
@Time ： 2025/7/29 10:43
@Auth ： Chris
@File ：LPQobuzGenreManager.py
@Desc:
'''
import os
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenreBaseManager import LPQobuzGenreBaseManager
from HOME.StreamService.Qobuz.Util.LPQobuzUtil import singleton
from LPClientFramework import LPUtility
from LPClientFramework.LPCache.LPPickleCache import LPPickleCache

class LPQobuzGenreManager(LPQobuzGenreBaseManager):
    cachePath = LPUtility.cacheDir / 'Qobuz' / 'genreCache.pkl'
    pklCache = LPPickleCache()
    
    def setAllGenres(self = None, genres = None):
        self._allGenres = genres.copy()
        self.pklCache.save(self.cachePath, self._allGenres)

    
    def loadAllGenresFromCache(self):
        if not os.path.exists(self.cachePath):
            return None
        data = None.pklCache.tryLoad(self.cachePath, None)
        if data:
            self._allGenres = data


