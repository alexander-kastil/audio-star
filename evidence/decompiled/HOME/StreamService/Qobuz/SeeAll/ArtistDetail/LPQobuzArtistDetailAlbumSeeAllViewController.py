# Source Generated with Decompyle++
# File: LPQobuzArtistDetailAlbumSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/17 11:53
@Auth ： Chris
@File ：LPQobuzArtistDetailAlbumSeeAllViewController.py
@Desc:
'''
import enum
from string import Template
from PyQt6.QtCore import QModelIndex, QCoreApplication
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailListView import LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class ArtistAlbumSortType(enum.Enum):
    Popularity = 'relevant'
    Release_Date = 'release_date'


class LPQobuzArtistDetailAlbumSeeAllViewController(LPQobuzSeeAllBaseViewController):
    
    def __init__(self = None, section = None, artistId = None):
        super().__init__()
        self.loading = False
        self.offset = 0
        self.limit = 50
        self.itemId = artistId
        self.section = section
        self.hasMore = True
        self.filterArray = [
            {
                'sortType': ArtistAlbumSortType.Release_Date,
                'title': QCoreApplication.translate('Qobuz Artist Albums', 'Release Date') },
            {
                'sortType': ArtistAlbumSortType.Popularity,
                'title': QCoreApplication.translate('Qobuz Artist Albums', 'Popularity') }]
        self.sortBy = ArtistAlbumSortType.Release_Date
        self.sectionBinding = {
            'Albums': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'album' },
            'EPs & Singles': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'epSingle' },
            'Live': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'live' },
            'Compilations': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'compilation' },
            'Purchase only': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'download' },
            'Other': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'other' } }

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setSpacing(5)
        self.listView.clicked.connect(self.onItemClicked)
        self.scrollBar = self.listView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onScroll)
        self.filterBox.setupUI()
        itemsArray = []
        for item in self.filterArray:
            itemsArray.append(item['title'])
        self.filterBox.addItems(itemsArray)
        self.filterBox.currentIndexChanged.connect(self.filterIndexChanged)
        self.titleLabel.setText(self.section)
        stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#weeklyQDescriptionLabel, #weeklyQNameLabel, #baselineLabel {\n                    background-color: $weeklyQTitleFrameBg;     \n\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))

    
    def viewWillAppear(self):
        self.updateUI()

    
    def viewWillDisappear(self):
        pass

    
    def updateUI(self):
        self.loadMore(True)

    
    def onItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        if None.isAlbum:
            streamable = playItem.streamable
            if not streamable:
                LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz fav album see all', 'This album is not available'), LPGlobalUI.mainWindow)
                logger.debug('qobuz artist->album %s not streamable' % playItem.trackName)
                return None
            LPQobuzAlbumDetailViewController = LPQobuzAlbumDetailViewController
            import HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController
            Ui_qobuzAlbumDetailViewWidget = Ui_qobuzAlbumDetailViewWidget
            import HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, playItem), 'qobuzdetail')

    
    def filterIndexChanged(self, index):
        sortType = self.filterArray[index]['sortType']
        logger.debug(f'''[LPQobuzFavoriteAlbumSeeAllViewController] filterIndexChanged sortType={sortType.value}''')
        self.sortBy = sortType
        self.resetAndRelod()

    
    def resetAndRelod(self):
        self.offset = 0
        self.hasMore = True
        self.loading = False
        self.loadMore()

    
    def onScroll(self, value):
        if value + self.scrollBar.pageStep() >= self.scrollBar.maximum() - 10:
            self.loadMore()

    
    def loadMore(self, isFirst = (False,)):
        if self.loading:
            return None
        if None.hasMore:
            self.loading = True
            self.loadDataBySection(self.offset, self.limit)

    
    def loadDataBySection(self, offset, limit = (0, 25)):
        binding = self.sectionBinding.get(self.section)
        if not binding:
            return None
        contentType = None['contentType']
        artistId = self.itemId
        sort = self.sortBy.value
        reqFunc = self.qobuz.requestMgr.fetchArtistReleases
        self.qobuz.requestMgr.fetch(reqFunc, self.onDataLoadCallback, artistId, contentType, sort, offset, limit)

    
    def onDataLoadCallback(self, result):
        playList = result.data
        self.hasMore = playList.header.hasMore
        if self.offset == 0:
            self.playList = playList
            model = LPQobuzListModel(self.playList, self.listView)
            self.listView.setModel(model)
            delegate = LPQobuzAlbumDelegate(self.listView)
            self.listView.setItemDelegate(delegate)
        else:
            self.listView.model().addItemList(playList)
        self.offset += self.limit
        self.loading = False
        print(f'''offset: {self.offset}''')

    __classcell__ = None

