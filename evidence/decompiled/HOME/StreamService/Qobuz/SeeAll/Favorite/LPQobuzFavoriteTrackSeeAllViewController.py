# Source Generated with Decompyle++
# File: LPQobuzFavoriteTrackSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/27 17:29
@Auth ： Chris
@File ：LPQobuzFavoriteTrackSeeAllViewController.py
@Desc:
'''
import copy
import time
from functools import partial
from string import Template
from PyQt6.QtCore import QModelIndex, pyqtSignal, pyqtSlot, Qt, QCoreApplication
from PyQt6.QtGui import QAction, QIcon, QCursor
from PyQt6.QtWidgets import QLineEdit, QHeaderView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzPlayMode
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteSeeAllBaseViewController import LPQobuzFavoriteSeeAllBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from PyQt6.QtCore import QSortFilterProxyModel
import re
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayList, LPQobuzPlayHeader, LPQobuzPlayItem, HeadTitle_Favorite_Tracks, HeadTitle_Purchased_Tracks
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPTableViewSkeleton import LPTableViewSkeletonTableModel, LPTableViewSkeletonDelegate

class LPTrackFilterProxyModel(QSortFilterProxyModel):
    
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

    
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        playItem = model.data(index, Qt.ItemDataRole.UserRole)
        textFilterOk = True
    # WARNING: Decompyle incomplete

    __classcell__ = None


class LPQobuzFavoriteTrackSeeAllViewController(LPQobuzFavoriteSeeAllBaseViewController):
    addTableDataSignal = pyqtSignal()
    
    def __init__(self = None, section = None):
        super().__init__()
        self.section = section
        self.proxy = None
        self.genreIds = None
        self.text = None
        self.libGenreManager.genresChangedSignal.connect(self.filterContent)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tableView.doubleClicked.connect(self.onTableViewItemDoubleClick)
        self.tableView.clicked.connect(self.onTableViewItemClick)
        self.tableView.setupUI()
        self.addTableDataSignal.connect(self._initView)
        self.titleLabel.setText(self.section)
        stylesheetTemplate = Template('\n                LPLineEdit {\n                    background-color: rgb(31, 31, 31); \n                    color: white; \n                    padding: 5px; \n                    border-radius: 5px; \n                    qproperty-placeholderColor: rgba(255, 255, 255, 89);\n                }\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#weeklyQDescriptionLabel, #weeklyQNameLabel, #baselineLabel {\n                    background-color: $weeklyQTitleFrameBg;     \n\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton#genresSelectButton {\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;\n                    color: $fontColor;                 \n                }\n        ')
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

    
    def _initView(self):
        model = LPQobuzTracksTableWithCoverModel(self.playList, self.tableView)
        self.proxy = LPTrackFilterProxyModel()
        self.proxy.setSourceModel(model)
        self.tableView.setModel(self.proxy)
        delegate = LPQobuzTrackTableWithCoverDelegate(self.tableView)
        if self.section.startswith('Fav'):
            delegate.favClicked.connect(self.onFFavClicked)
        else:
            delegate.favClicked.connect(self.onPFavClicked)
        delegate.optClicked.connect(self.onOptClicked)
        self.tableView.setItemDelegate(delegate)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableView.setColumnWidth(2, 200)
        self.tableView.setColumnWidth(3, 150)
        self.tableView.setColumnWidth(4, 50)
        self.tableView.setColumnWidth(5, 50)
        self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if self.libGenreManager.selectedGenres():
            self.filterContent(self.libGenreManager.selectedGenres())

    
    def onTableViewItemClick(self, index):
        if self.tableView.lastCursorActionIndex:
            data = index.data()
            if data is None:
                return None
            itemType = None[2]
            if itemType == 'artist':
                artistPlayItem = LPQobuzPlayItem()
                artistPlayItem.trackId = data[3]
                artistPlayItem.trackName = data[0]
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistPlayItem), 'qobuzdetail')

    
    def loadDataFromCache(self, cacheData):
        self.playList = cacheData
        header = self.playList.header
        if self.section == 'Favorite Tracks':
            header.headTitle = HeadTitle_Favorite_Tracks
            self.checkPlayListAllFavorite(self.playList)
        else:
            header.headTitle = HeadTitle_Purchased_Tracks
            self.checkPlayListFavorite(self.playList)
        self.addTableDataSignal.emit()

    
    def refreshFavoriteStatus(self = None):
        '''收藏缓存变化时刷新 Purchased Tracks 曲目行，Favorite Tracks 保持整表已收藏。'''
        if self.section == 'Favorite Tracks':
            return None
        None().refreshFavoriteStatus()

    
    def searchFieldChanged(self, text):
        logger.debug(f'''[LPQobuzFavoriteTrackSeeAllViewController] searchFieldChanged text={text}''')
        self.searchFieldClearAction.setVisible(len(text) > 0)
        self.text = text
        self.updateProxy()

    
    def onTableViewItemDoubleClick(self = None, index = None):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        playList = None.tableView.model().sourceModel().playList
        if self.libGenreManager.isSelected() or self.text:
            sourceIndex = self.proxy.mapToSource(index)
            playItem = playList.list[sourceIndex.row()]
            playListCopy = copy.deepcopy(playList)
            playListCopy.list = [
                playItem]
            playList.header.searchUrl = playItem.searchUrl
            xml = playListCopy.generateTrackPlayXML(playListCopy.list, '1')
            recentlyPlayList = playListCopy
            recentlyPlayIndex = 0
            playMode = LPQobuzPlayMode.SingleTrack
        else:
            playItem = playList.list[index.row()]
            startIndex = str(playItem.startIndex)
            playList.header.searchUrl = playItem.searchUrl
            xml = playList.generateXML(startIndex)
            recentlyPlayList = playList
            recentlyPlayIndex = index.row()
            playMode = LPQobuzPlayMode.Normal
        streamable = playItem.streamable
        if not streamable:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz lib', 'This track is not available'), LPGlobalUI.mainWindow)
            logger.debug('qobuz track %s not streamable' % playItem.trackName)
            return None
        None.playQobuzPlayList(recentlyPlayList, playItem, xml, recentlyPlayIndex, playMode, 'qobuz favorite track', **('playIndex', 'playMode', 'logPrefix'))

    
    def filterContent(self, selectedGenres):
        if selectedGenres:
            self.genreIds = set((lambda .0: [ genre.trackId for genre in .0 ])(selectedGenres))
        else:
            self.genreIds = None
        logger.debug(f'''fav albums filterContent selectedGenreIds == {self.genreIds}''')
        self.updateProxy()

    
    def updateProxy(self):
        self.proxy.setFilterPattern(self.text)
        self.proxy.setSelectedGenres(self.genreIds)
        if self.proxy.rowCount() == 0:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

    
    def onOptClicked(self, index):
        data = self.tableView.model().sourceModel()._data
        playItem = data[index.row()]
        parentPlayItem = self.playList.header
        trackMoreMenu = LPQobuzTrackMoreMenu(playItem, parentPlayItem, self.tableView)
        trackMoreMenu.setupUI()
        trackMoreMenu.showMenu(QCursor.pos())

    
    def onFFavClicked(self, index):
        data = self.tableView.model().sourceModel()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'delete'
        LPQobuzUtil.deleteRow(self.tableView, index)
        
        def unfavoriteCallback(result = None):
            status = result.data
            if status == 'success':
                LPGlobalUI.toast.showToast(QCoreApplication.translate('Qobuz Favorite', 'Removed From Favorites'), LPGlobalUI.mainWindow)
                logger.debug(f'''[qobuz favorite track see all unfavorite] ret = {status} trackName={playItem.trackName} trackId={playItem.trackId}''')
                self._loadSkeleton()
                self.qobuz.libCacheMgr.checkUpdate([
                    self.section])

        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, unfavoriteCallback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    
    def _loadSkeleton(self):
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.setModel(LPTableViewSkeletonTableModel(10, 6, self.tableView))
        self.tableView.setItemDelegate(LPTableViewSkeletonDelegate(self.tableView))
        self.tableView.setColumnWidth(0, 20)

    
    def onPFavClicked(self, index):
        data = self.tableView.model().sourceModel()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'add' if playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, LPHeaderType.LP_HEADER_TYPE_SONG, itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    __classcell__ = None

