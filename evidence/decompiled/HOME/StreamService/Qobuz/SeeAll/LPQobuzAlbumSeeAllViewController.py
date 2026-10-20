# Source Generated with Decompyle++
# File: LPQobuzAlbumSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/18 11:14
@Auth ： Chris
@File ：LPQobuzAlbumSeeAllViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import pyqtSlot
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType

class LPQobuzAlbumSeeAllViewController(LPQobuzSeeAllBaseViewController):
    
    def __init__(self = None, section = None, *args):
        super().__init__()
        self.section = section
        self.loading = False
        self.genres = None
        self.disGenreManager.genresChangedSignal.connect(self.refreshContent)
        if args:
            self.similarAlbumsGenreStr = args[0]

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setSpacing(self.listViewDefaultSpacing)
        self.listView.clicked.connect(self.onListViewItemClicked)
        self.scrollBar = self.listView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onScroll)
        self.dataBinding = [
            {
                'id': 'New Releases',
                'contentType': 'new-releases' },
            {
                'id': 'Qobuz Essential Discography',
                'contentType': 'ideal-discography' },
            {
                'id': 'Top Albums',
                'contentType': 'most-streamed' },
            {
                'id': 'Qobuzissime',
                'contentType': 'qobuzissims' },
            {
                'id': 'Press Accolades',
                'contentType': 'press-awards' },
            {
                'id': 'Similar albums',
                'contentType': None }]
        for binding in self.dataBinding:
            if self.section == binding['id']:
                self.titleLabel.setText(self.section)
            
            stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton#genresSelectButton {\n                    font-size: ${subTitleFontSize}pt;\n                    color: $fontColor;\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;                 \n                }\n        ')
            self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))
            if self.section == 'Similar albums':
                self.genreSelectorFrame.hide()
            else:
                self.genresSelectButton.clicked.connect(self._showGenresSelector)
                self.genresSelectButton.setText(self.disGenreManager.getSelectorText())
                self.disGenreManager.selectorTextChangedSignal.connect(self.genresSelectButton.setText)

    
    def _showGenresSelector(self):
        self.selector = LPGlobalUI.loadUI(LPUIPath.QobuzGenresSelectorUI, Ui_qobuzGenres_Form, LPQobuzGenresSelector, self, self.disGenreManager)
        if self.selector.isVisible():
            self.selector.hide()
        else:
            self.selector.showGenre()

    _showGenresSelector = pyqtSlot()(_showGenresSelector)
    
    def viewWillAppear(self):
        self.updateUI()

    
    def viewWillDisappear(self):
        self.genreSnapshot = self.disGenreManager.getSelectedGenreStr()

    
    def updateUI(self):
        if not self.needRefresh():
            logger.debug('[qobuz album updateUI] not need refresh')
            return None
        None.refreshContent()

    
    def loadDataBySection(self, genres, offset, limit = (None, 0, 25)):
