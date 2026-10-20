# Source Generated with Decompyle++
# File: LPQobuzPlaylistSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/19 10:09
@Auth ： Chris
@File ：LPQobuzPlaylistSeeAllViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QModelIndex, QEvent, pyqtSlot, Qt
from PyQt6.QtWidgets import QButtonGroup, QPushButton, QSizePolicy, QWidget
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.GenresSelector.LPQobuzGenresSelector import LPQobuzGenresSelector
from HOME.StreamService.Qobuz.Component.GenresSelector.UI.LPQobuzGenresSelector_ui import Ui_qobuzGenres_Form
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistListModel, LPQobuzPlaylistDelegate
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzPlaylistSeeAllViewController(LPQobuzSeeAllBaseViewController):
    
    def __init__(self = None, tag = None):
        super().__init__()
        self.loading = False
        self.offset = 0
        self.limit = 50
        self.total = self.defaultTotal
        self.slug = tag
        self.disGenreManager.genresChangedSignal.connect(self.refreshContent)
        self.qobuz.categoryListReadySignal.connect(self._updateCategory)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setSpacing(5)
        self.listView.clicked.connect(self.onListViewItemClicked)
        self.scrollBar = self.listView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onScroll)
        self.categoryButtonGroup = QButtonGroup()
        self.categoryButtonGroup.setExclusive(True)
        self.All_CategoryButton.setCheckable(True)
        self.All_CategoryButton.tag = None
        self.categoryButtonGroup.addButton(self.All_CategoryButton)
        self.categoryButtonGroup.buttonClicked.connect(self.onCategoryButtonClicked)
        if not self.slug:
            self.All_CategoryButton.setChecked(True)
        self.titleLabel.setText('Qobuz Playlist')
        stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton#genresSelectButton {\n                    font-size: ${subTitleFontSize}pt;\n                    color: $fontColor;\n                    background-color: $checkedFontColor;\n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    min-width: 150px;                 \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                    border: none;\n                }\n                QPushButton:checked {\n                    text-decoration: underline;\n                    color: $checkedFontColor;\n    \n                }\n\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor', 'weeklyQTitleFrameBg')))
        self.genresSelectButton.clicked.connect(self._showGenresSelector)
        self.genresSelectButton.setText(self.disGenreManager.getSelectorText())
        self.disGenreManager.selectorTextChangedSignal.connect(self.genresSelectButton.setText)
        self._categoryContainer = QWidget()
        self._categoryContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._categoryContainer.setMinimumHeight(40)
        self._categoryContainer.setMaximumHeight(40)
        self._categoryContainer.installEventFilter(self)
        self.buttonFrame.setMinimumWidth(0)
        self.buttonFrame.setMaximumWidth(16777215)
        self.buttonFrame.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.buttonFrame.setMinimumHeight(40)
        self.buttonFrame.setMaximumHeight(40)
        parentLayout = self.PlaylistCategoryFrame.layout()
        parentLayout.removeWidget(self.buttonFrame)
        self.buttonFrame.setParent(self._categoryContainer)
        self.buttonFrame.move(0, 0)
        self.buttonFrame.adjustSize()
        parentLayout.addWidget(self._categoryContainer)
        self._categoryNavPrevButton = LPQobuzUtil.createCategoryNavButton(self._categoryContainer, self.buttonFrame, -1)
        self._categoryNavNextButton = LPQobuzUtil.createCategoryNavButton(self._categoryContainer, self.buttonFrame, 1)
        self._categoryContainer._qobuzNavPrevButton = self._categoryNavPrevButton
        self._categoryContainer._qobuzNavNextButton = self._categoryNavNextButton
        self._categoryContainer._qobuzNavOffset = 0
        self._updateCategoryNavButtons()
        self.qobuz.getPlaylistCategory()

    
    def _updateCategory(self):
