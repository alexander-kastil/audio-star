# Source Generated with Decompyle++
# File: LPQobuzGenreBaseManager.pyc (Python 3.9)

'''
@Time ： 2025/7/18 9:42
@Auth ： Chris
@File ：LPQobuzGenreBaseManager.py
@Desc:
'''
from PyQt6.QtCore import pyqtSignal, QObject
from LPClientFramework.CacheLog import logger

class LPQobuzGenreBaseManager(QObject):
    genresChangedSignal = pyqtSignal(object)
    selectorTextChangedSignal = pyqtSignal(str)
    
    def __init__(self = None):
        super().__init__()
        self._selectedGenres = []
        self._allGenres = []

    
    def _getGenreKey(self, genre):
        return genre.trackId

    
    def _getGenresKeyList(self = None, genres = None):
        return (lambda .0: [ g.trackId for g in .0 ])(genres)

    
    def getSelectedKeys(self):
        return (lambda .0 = None: [ self._getGenreKey(g) for g in .0 ])(self._selectedGenres)

    
    def selectedGenres(self = None):
        return self._selectedGenres.copy()

    
    def setGenres(self = None, genres = None, emitSignal = None):
        self._selectedGenres = genres.copy()
        if emitSignal:
            self.genresChangedSignal.emit(self._selectedGenres)

    
    def allGenres(self = None):
        return self._allGenres.copy()

    
    def setAllGenres(self = None, genres = None):
        self._allGenres = genres.copy()

    
    def sortedGenres(self = None):
        return sorted(self._selectedGenres, (lambda g: g.trackId), **('key',))

    
    def clearGenres(self):
        logger.debug('[LPQobuzGenreBaseManager] clearGenres')
        if self._selectedGenres:
            self._selectedGenres.clear()
            self.genresChangedSignal.emit(None)
            self.sendSelectorTextChangedSignal()

    
    def selectAllGenres(self):
        logger.debug('[LPQobuzGenreBaseManager] selectAllGenres')
        if self._allGenres:
            self._selectedGenres = self._allGenres.copy()
            self.genresChangedSignal.emit(None)
            self.sendSelectorTextChangedSignal()

    
    def toggleGenre(self, genre):
        logger.debug(f'''[LPQobuzGenreBaseManager] toggleGenre genre->{genre.trackId}''')
        key = self._getGenreKey(genre)
        keys = self._getGenresKeyList(self._selectedGenres)
        if key in keys:
            self._selectedGenres = (lambda .0 = None: [ g for g in .0 if self._getGenreKey(g) != key ])(self._selectedGenres)
        else:
            self._selectedGenres.append(genre)
        self.sendSelectorTextChangedSignal()

    
    def sendSelectorTextChangedSignal(self):
        text = self.getSelectorText()
        self.selectorTextChangedSignal.emit(text)

    
    def getSelectorText(self = None, maxVisible = None, defaultText = None):
        selected = self._selectedGenres
        total = self._allGenres
        if selected or len(selected) == len(total):
            return defaultText
        names = (lambda 