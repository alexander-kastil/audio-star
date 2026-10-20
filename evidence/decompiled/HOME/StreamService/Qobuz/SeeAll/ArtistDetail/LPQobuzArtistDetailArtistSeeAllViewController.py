# Source Generated with Decompyle++
# File: LPQobuzArtistDetailArtistSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/17 13:30
@Auth ： Chris
@File ：LPQobuzArtistDetailArtistSeeAllViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QModelIndex
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzArtistDelegate
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title

class LPQobuzArtistDetailArtistSeeAllViewController(LPQobuzSeeAllBaseViewController):
    
    def __init__(self = None, section = None, artistId = None):
        super().__init__()
        self.loading = False
        self.offset = 0
        self.limit = 50
        self.total = 0
        self.itemId = artistId
        self.section = section

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setSpacing(5)
        self.listView.clicked.connect(self.onItemClicked)
        self.scrollBar = self.listView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onScroll)
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
        LPQobuzArtistDetailViewController = LPQobuzArtistDetailViewController
        import HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController
        Ui_qobuzArtistDetailViewWidget = Ui_qobuzArtistDetailViewWidget
        import HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui
        if playItem.isArtist:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, playItem), 'qobuzdetail')

    
    def onScroll(self, value):
        if value + self.scrollBar.pageStep() >= self.scrollBar.maximum() - 10:
            self.loadMore()

    
    def loadMore(self, isFirst = (False,)):
        if self.loading:
            return None
        if None and self.offset >= self.total:
            return None
        self.loading = None
        self.loadDataBySection(self.offset, self.limit)

    
    def loadDataBySection(self, offset, limit = (0, 25)):
        artistId = self.itemId
        reqFunc = self.qobuz.requestMgr.fetchSimilarArtistData
        self.qobuz.requestMgr.fetch(reqFunc, self.onDataLoadCallback, artistId, offset, limit)

    
    def onDataLoadCallback(self, result):
        playList = result.data
        self.total = playList.header.total
        if self.offset == 0:
            self.playList = playList
            model = LPQobuzListModel(self.playList, self.listView)
            self.listView.setModel(model)
            delegate = LPQobuzArtistDelegate(self.listView)
            self.listView.setItemDelegate(delegate)
        else:
            self.listView.model().addItemList(playList)
        self.offset += self.limit
        self.loading = False
        print(f'''offset: {self.offset}''')

    __classcell__ = None

