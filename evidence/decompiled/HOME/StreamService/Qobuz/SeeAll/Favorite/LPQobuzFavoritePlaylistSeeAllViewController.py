# Source Generated with Decompyle++
# File: LPQobuzFavoritePlaylistSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/24 11:03
@Auth ： Chris
@File ：LPQobuzFavoriteAlbumSeeAllViewController.py
@Desc:
'''
import enum
import time
from string import Template
from PyQt6.QtCore import QModelIndex, pyqtSignal, pyqtSlot, Qt, QCoreApplication
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QLineEdit
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistDelegate, LPQobuzPlaylistListModel
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteSeeAllBaseViewController import LPQobuzFavoriteSeeAllBaseViewController
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from PyQt6.QtCore import QSortFilterProxyModel
import re
from LPClientFramework.LPUtility import logger

class FPSortType(enum.Enum):
    CUSTOM_ORDER = 'custom_order'
    LAST_UPDATE = 'last_update'
    TITLE = 'title'


class LPAlbumFilterProxyModel(QSortFilterProxyModel):
    
    def __init__(self = None):
        super().__init__()
        self.pattern = ''
        self.sortBy = ''
        self.sortOrder = Qt.SortOrder.AscendingOrder
        self.selectedGenreIds = set()

    
    def setFilterPattern(self, pattern):
        self.pattern = pattern
        self.invalidateFilter()

    
    def setSelectedGenres(self = None, genre_ids = None):
        self.selectedGenreIds = genre_ids
        self.invalidateFilter()

    
    def changeSorting(self = None, key = None, order = None):
        self.sortBy = key
        self.sortOrder = order
        self.invalidate()
        self.sort(0, order)

    
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        playItem = model.data(index, Qt.ItemDataRole.UserRole)
        textFilterOk = True
    # WARNING: Decompyle incomplete

    
    def lessThan(self, left, right):
        model = self.sourceModel()
        left = model.data(left, Qt.ItemDataRole.UserRole)
        right = model.data(right, Qt.ItemDataRole.UserRole)
        if self.sortBy == FPSortType.CUSTOM_ORDER:
            if not left.dateAdd:
                pass
            if not right.dateAdd:
                pass
            return 0 <= 0
        if None.sortBy == FPSortType.LAST_UPDATE:
            if not left.lastUpdate:
                pass
            if not right.lastUpdate:
                pass
            return 0 <= 0
        if None.sortBy == FPSortType.TITLE:
            if not left.trackName:
                pass
            if not right.trackName:
                pass
            return ''.lower() < ''.lower()

    __classcell__ = None


class FPCacheType(enum.Enum):
    PLAYLISTS = 'playlists'


class LPQobuzFavoritePlaylistSeeAllViewController(LPQobuzFavoriteSeeAllBaseViewController):
    
    def __init__(self = None):
        super().__init__()
        self.section = 'My Playlists'
        self.proxy = None
        cacheSortByValue = self.getSortType('playlist')
        self.sortBy = FPSortType(cacheSortByValue) if cacheSortByValue else FPSortType.CUSTOM_ORDER
        self.genreIds = None
        self.text = None
        self.filterArray = [
            {
                'sortType': FPSortType.CUSTOM_ORDER,
                'title': QCoreApplication.translate('Favorite Playlists', 'Custom order') },
            {
                'sortType': FPSortType.LAST_UPDATE,
                'title': QCoreApplication.translate('Favorite Playlists', 'Last update') },
            {
                'sortType': FPSortType.TITLE,
                'title': QCoreApplication.translate('Favorite Playlists', 'Title') }]
        self.libGenreManager.genresChangedSignal.connect(self.filterContent)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setSpacing(5)
        self.listView.clicked.connect(self.onListViewItemClicked)
        self.filterBox.setupUI()
        itemsArray = []
        sortTypes = []
        for item in self.filterArray:
            itemsArray.append(item['title'])
            sortTypes.append(item['sortType'])
        self.filterBox.addItems(itemsArray)
        if self.sortBy and self.sortBy in sortTypes:
            index = sortTypes.index(self.sortBy)
            self.filterBox.setCurrentIndex(index)
        self.filterBox.currentIndexChanged.connect(self.filterIndexChanged)
        self.titleLabel.setText('My Playlists')
        stylesheetTemplate = Template('\n                LPLineEdit {\n                    background-color: rgb(31, 31, 31); \n                    color: white; \n                    padding: 5px; \n                    border-radius: 5px; \n                    qproperty-placeholderColor: rgba(255, 255, 255, 89);\n                }\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton#genresSelectButton {\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;\n                    color: $fontColor;                 \n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))
        self.genresSelectButton.setText(self.libGenreManager.getSelectorText())
        self.libGenreManager.selectorTextChangedSignal.connect(self.genresSelectButton.setText)
        self.genresSelectButton.clicked.connect(self._showGenresSelector)
        self.searchField.textChanged.connect(self.searchFieldChanged)
        self.searchFieldClearAction = QAction('clear', self)
        self.searchFieldClearAction.setIcon(QIcon(LPGlobalUI.imagePath('search_close.png')))
        self.searchField.addAction(self.searchFieldClearAction, QLineEdit.ActionPosition.TrailingPosition)
        None((lambda : self.searchField.clear()))
        self.searchFieldClearAction.setVisible(False)
        self.emptyLabel.setText(QCoreApplication.translate('qobuz see all', QobuzSectionTip.NO_Filter_Results.value))

    
    def _showGenresSelector(self):
        self.selector = LPGlobalUI.loadUI(LPUIPath.QobuzGenresSelectorUI, Ui_qobuzGenres_Form, LPQobuzGenresSelector, self, self.libGenreManager)
        if self.selector.isVisible():
            self.selector.hide()
        else:
            self.selector.showGenre()

    _showGenresSelector = pyqtSlot()(_showGenresSelector)
    
    def viewWillAppear(self):
        self.updateUI()

    
    def viewWillDisappear(self):
        pass

    
    def updateUI(self):
        self.loadData()
        self.qobuz.libCacheMgr.checkUpdate([
            self.section])

    
    def loadDataFromCache(self, cacheData):
        self.playList = cacheData
        model = LPQobuzPlaylistListModel(self.playList, self.listView)
        self.proxy = LPAlbumFilterProxyModel()
        self.proxy.sort(0, Qt.SortOrder.DescendingOrder)
        self.proxy.setSourceModel(model)
        self.listView.setModel(self.proxy)
        delegate = LPQobuzPlaylistDelegate(self.listView)
        self.listView.setItemDelegate(delegate)
        if self.libGenreManager.selectedGenres() and self.sortBy or self.text:
            self.filterContent(self.libGenreManager.selectedGenres())

    
    def searchFieldChanged(self, text):
        logger.debug(f'''[LPQobuzFavoritePlaylistSeeAllViewController] searchFieldChanged text={text}''')
        self.searchFieldClearAction.setVisible(len(text) > 0)
        self.text = text
        self.updateProxy()

    
    def filterIndexChanged(self, index):
        sortType = self.filterArray[index]['sortType']
        logger.debug(f'''[LPQobuzFavoritePlaylistSeeAllViewController] filterIndexChanged sortType={sortType.value}''')
        self.sortBy = sortType
        self.saveSortType('playlist', sortType.value)
        self.updateProxy()

    
    def filterContent(self, selectedGenres):
        if selectedGenres:
            self.genreIds = set((lambda .0: [ genre.trackId for genre in .0 ])(selectedGenres))
        else:
            self.genreIds = None
        logger.debug(f'''my playlists filterContent selectedGenreIds == {self.genreIds}''')
        self.updateProxy()

    
    def updateProxy(self):
        self.proxy.setFilterPattern(self.text)
        self.proxy.setSelectedGenres(self.genreIds)
        if self.sortBy:
            if self.sortBy == FPSortType.CUSTOM_ORDER or self.sortBy == FPSortType.LAST_UPDATE:
                order = Qt.SortOrder.DescendingOrder
            else:
                order = Qt.SortOrder.AscendingOrder
            self.proxy.changeSorting(self.sortBy, order, **('order',))
        if self.proxy.rowCount() == 0:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

    __classcell__ = None

