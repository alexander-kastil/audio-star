# Source Generated with Decompyle++
# File: LPQobuzLibraryViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/6 14:33
@Auth ： Chris
@File ：LPQobuzLibraryViewController.py
@Desc:
'''
import threading
import time
from functools import partial
from string import Template
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QTimer, QCoreApplication
import LPGlobalUI
from HOME.StreamService.Qobuz.Browse.LPQobuzBrowseBaseViewController import LPQobuzBrowseBaseViewController
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.Section.LPQobuzListFrameSection import LPQobuzListFrameSection
from HOME.StreamService.Qobuz.Component.Section.LPQobuzTableFrameSection import LPQobuzTableFrameSection
from HOME.StreamService.Qobuz.Component.UI.LPQobuzListFrameSection_ui import Ui_qobuzListFrameWidget
from HOME.StreamService.Qobuz.Component.UI.LPQobuzTableFrameSection_ui import Ui_qobuzTableFrameWidget
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LibPageState:
    
    def __init__(self, limit = (500,)):
        self.limit = limit
        self.total = 16777215
        self.offset = 0



class LPQobuzLibraryViewController(LPQobuzBrowseBaseViewController):
    updateTableviewSignal = pyqtSignal()
    updateImageSignal = pyqtSignal(object)
    updateGenreSelectorSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.libGenreManager.genresChangedSignal.connect(self.filterContent)
        self.qobuz.libCacheMgr.libCacheChangedSignal.connect(self.onSectionDataChanged)
        self.sectionBinding = [
            {
                'id': 'My Playlists',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST },
            {
                'id': 'Favorite Artists',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ARTIST },
            {
                'id': 'Favorite Albums',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM },
            {
                'id': 'Favorite Tracks',
                'component': 'tableFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION },
            {
                'id': 'Purchased Albums',
                'component': 'listFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM },
            {
                'id': 'Purchased Tracks',
                'component': 'tableFrame',
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION }]

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                \n                QPushButton {\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: $weeklyQTitleFrameBg;\n                }               \n                QPushButton:checked {\n                    text-decoration: underline;\n                    color: $checkedFontColor;  \n                }\n                QPushButton#genresSelectButton {\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;                 \n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))
        self.genresSelectButton.setText(self.libGenreManager.getSelectorText())
        self.libGenreManager.selectorTextChangedSignal.connect(self.genresSelectButton.setText)
        self.genresSelectButton.clicked.connect(self._showGenresSelector)
        self.emptyLabel.setText(QCoreApplication.translate('qobuz lib', QobuzSectionTip.NO_Show_Results.value))
        self._loadSection()

    
    def onSectionDataChanged(self, account, sectionKey):
