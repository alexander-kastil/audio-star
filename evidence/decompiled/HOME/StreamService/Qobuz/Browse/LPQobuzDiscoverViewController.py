# Source Generated with Decompyle++
# File: LPQobuzDiscoverViewController.pyc (Python 3.9)

'''
@Time ： 2025/5/29 15:08
@Auth ： Chris
@File ：LPQobuzDiscoverViewController.py
@Desc:
'''
import queue
import time
from functools import partial
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
import LPGlobalUI
from HOME.StreamService.Qobuz.Browse.LPQobuzBrowseBaseViewController import LPQobuzBrowseBaseViewController
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.Section.LPQobuzListFrameSection import LPQobuzListFrameSection
from HOME.StreamService.Qobuz.Component.Section.LPQobuzPlaylistFrameSection import LPQobuzPlaylistFrameSection
from HOME.StreamService.Qobuz.Component.Section.LPQobuzWeeklyQFrameSection import LPQobuzWeeklyQFrameSection
from HOME.StreamService.Qobuz.Component.UI.LPQobuzListFrameSection_ui import Ui_qobuzListFrameWidget
from HOME.StreamService.Qobuz.Component.UI.LPQobuzPlaylistFrameSection_ui import Ui_qobuzPlaylistFrameWidget
from HOME.StreamService.Qobuz.Component.UI.LPQobuzWeeklyQFrameSection_ui import Ui_qobuzRecommendFrameWidget
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult, LPRequestErrorType
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzDiscoverViewController(LPQobuzBrowseBaseViewController):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.disGenreManager.genresChangedSignal.connect(self.refreshContent)
        self.sectionBinding = [
            {
                'id': 'New Releases',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'new-releases',
                'playList': None },
            {
                'id': 'Recommended for you',
                'component': None,
                'headType': None,
                'contentType': 'weekly',
                'playList': None },
            {
                'id': 'Qobuz Playlist',
                'component': 'playlistFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST,
                'contentType': 'last-created',
                'playList': None },
            {
                'id': 'Qobuz Essential Discography',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'ideal-discography',
                'playList': None },
            {
                'id': 'Top Albums',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'most-streamed',
                'playList': None },
            {
                'id': 'Qobuzissime',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'qobuzissims',
                'playList': None },
            {
                'id': 'Press Accolades',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'contentType': 'press-awards',
                'playList': None }]

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#weeklyQTitleFrame, #weeklyQPlayFrame{\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QFrame#NR_SplitFrame, #Playlist_SplitFrame, #R_SplitFrame, #Qobuzissime_SplitFrame, #TopAlbums_SplitFrame, #PressAccolades_SplitFrame, #ED_SplitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#weeklyQDescriptionLabel, #weeklyQNameLabel, #baselineLabel {\n                    background-color: $weeklyQTitleFrameBg;     \n          \n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                \n                QPushButton {\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QPushButton:checked {\n                    text-decoration: underline;\n                    color: $checkedFontColor;\n    \n                }\n                QPushButton#genresSelectButton {\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;                 \n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))
        self.genresSelectButton.setText(self.disGenreManager.getSelectorText())
        self.disGenreManager.selectorTextChangedSignal.connect(self.genresSelectButton.setText)
        self.genresSelectButton.clicked.connect(self._showGenresSelector)
        self._loadSection()

    
    def _showGenresSelector(self):
        self.selector = LPGlobalUI.loadUI(LPUIPath.QobuzGenresSelectorUI, Ui_qobuzGenres_Form, LPQobuzGenresSelector, self, self.disGenreManager)
        if self.selector.isVisible():
            self.selector.hide()
        else:
            self.selector.showGenre()

    _showGenresSelector = pyqtSlot()(_showGenresSelector)
    
    def loadPreData(self):
        if self.hasPreData():
            logger.debug('loadPreData...')
            for binding in self.sectionBinding:
                playList = binding['playList']
                self.updateSectionUISignal.emit(binding, playList)
                logger.debug(f''' section={binding['id']} use preData''')
        elif self.qobuz.requestMgr.checkDiscoverCached():
            return None
        self.loadSkeletonSignal.emit()

    
    def onEnter(self):
        logger.debug('============onEnter')
        self.loadPreData()
        self.loadPage()

    
    def onLeave(self):
        self.endSkeleton()
        logger.debug('============onLeave')

    
    def refreshContent(self):
        genres = self.disGenreManager.getSelectedGenreStr()
        self.loadData(genres)

    
    def loadPage(self):
        self.requestCounter.start(6)
        self.refreshContent()

    
    def _loadSection(self):
        vLayout = self.mainFrame.layout()
        for binding in self.sectionBinding:
            componentType = binding['component']
            section = binding['id']
            if componentType == 'listFrame':
                frameView = LPGlobalUI.loadUI(LPUIPath.QobuzListFrameSectionUI, Ui_qobuzListFrameWidget, LPQobuzListFrameSection, section, None)
            elif componentType == 'playlistFrame':
                frameView = LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistFrameSectionUI, Ui_qobuzPlaylistFrameWidget, LPQobuzPlaylistFrameSection, section, None)
            else:
                frameView = LPGlobalUI.loadUI(LPUIPath.QobuzWeeklyQFrameSectionUI, Ui_qobuzRecommendFrameWidget, LPQobuzWeeklyQFrameSection, section, None)
            self.viewMap[section] = frameView
            vLayout.addWidget(frameView)

    
    def loadData(self, genres = ('',)):
        for binding in self.sectionBinding:
            headType = binding['headType']
            contentType = binding['contentType']
            section = binding['id']
            callback = partial(self.onLoadDataCallback, genres, binding)
            if headType:
                if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
                    playlistVC = self.viewMap['Qobuz Playlist']
                    playlistVC.All_CategoryButton.setChecked(True)
                reqFunc = self.qobuz.requestMgr.fetchFeaturedData
                self.qobuz.requestMgr.fetch(reqFunc, callback, headType, contentType, genres)
                continue
            recommendVC = self.viewMap['Recommended for you']
            if recommendVC.playList:
                continue
            reqFunc = self.qobuz.requestMgr.fetchRecommendData
            self.qobuz.requestMgr.fetch(reqFunc, callback)

    
    def onLoadDataCallback(self = None, genres = None, binding = None, commonResult = {
        'commonResult': LPRequestCommonResult }):
        if genres != self.disGenreManager.getSelectedGenreStr():
            logger.debug(f'''request-genres {genres} != self.disGenreManager.getSelectedGenreStr{self.disGenreManager.getSelectedGenreStr()} --------response data discard!''')
            return None
        section = None['id']
        logger.debug(f'''{section} success = {commonResult.is_success()}''')
        self.requestCounter.requestFinished(commonResult.is_success())
        if commonResult.is_success():
            self.updateSectionUISignal.emit(binding, commonResult.data)
        else:
            logger.debug(f'''status_code={commonResult.status_code}, error={commonResult.error}''')

    __classcell__ = None

