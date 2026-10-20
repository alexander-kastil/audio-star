# Source Generated with Decompyle++
# File: LPQobuzPlaylistFrameSection.pyc (Python 3.9)

'''
@Time ： 2025/7/14 9:45
@Auth ： Chris
@File ：LPQobuzPlaylistFrameSection.py
@Desc:
'''
from functools import partial
from string import Template
from PyQt6.QtCore import QModelIndex, QEvent, Qt, pyqtSignal, QCoreApplication
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QButtonGroup, QAbstractItemView, QWidget
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistListModel, LPQobuzPlaylistDelegate
from HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController import LPQobuzAlbumDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController import LPQobuzPlaylistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.SeeAll.LPQobuzAlbumSeeAllViewController import LPQobuzAlbumSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.LPQobuzPlaylistSeeAllViewController import LPQobuzPlaylistSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.UI.LPQobuzAlbumSeeAllViewController_ui import Ui_qobuzAlbumSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.UI.LPQobuzPlaylistSeeAllViewController_ui import Ui_qobuzPlaylistSeeAllWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPListViewSkeleton import LPListViewSkeletonListModel, LPListViewSkeletonDelegateWithSize

class LPQobuzPlaylistFrameSection(LPQobuzBaseViewController):
    updatePlaylistCategoryUISignal = pyqtSignal(object)
    
    def __init__(self = None, section = None, playList = None):
        super().__init__()
        self.section = section
        self.playList = playList
        self.category = ''
        self.qobuz.categoryListReadySignal.connect(self._updateCategory)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.sectionTitleLabel.setText(self.section)
        self.skeletonDelegate = LPListViewSkeletonDelegateWithSize(self.listView, 190, 265)
        if not self.playList:
            self.showSkeleton()
        self.listView.wheelEvent = self.listViewWheelEvent
        self.listView.setFlow(self.listViewDefaultFlow)
        self.listView.setSpacing(self.listViewDefaultSpacing)
        self.listView.clicked.connect(self.onItemClicked)
        self.listView.wheelEvent = self.listViewWheelEvent
        self.listView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.bar = self.listView.horizontalScrollBar()
        self.bar.rangeChanged.connect(self.updateListViewNavButtons)
        self.bar.valueChanged.connect(self.updateListViewNavButtons)
        self.moreButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.moreButton.setStyleSheet('border-radius: 12px;')
        self.moreButton.clicked.connect(self.onSeeAllButtonClicked)
        self.moreButton.setText(self.seeAllText)
        self.leftButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.leftButton.setStyleSheet('border-radius: 12px;')
        self.leftButton.clicked.connect(self.onLeftButtonClicked)
        self.rightButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rightButton.setStyleSheet('border-radius: 12px;')
        self.rightButton.clicked.connect(self.onRightButtonClicked)
        self.categoryButtonGroup = QButtonGroup()
        self.categoryButtonGroup.setExclusive(True)
        self.All_CategoryButton.setCheckable(True)
        self.All_CategoryButton.tag = None
        self.categoryButtonGroup.addButton(self.All_CategoryButton)
        self.All_CategoryButton.setChecked(True)
        self.categoryButtonGroup.buttonClicked.connect(self.onCategoryButtonClicked)
        self.categoryButtonGroup.buttonToggled.connect(self.onToggled)
        self._categoryContainer = QWidget()
        self._categoryContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._categoryContainer.setMinimumHeight(self.PlaylistCategoryFrame.maximumHeight())
        self._categoryContainer.setMaximumHeight(self.PlaylistCategoryFrame.maximumHeight())
        self._categoryContainer.installEventFilter(self)
        self.buttonFrame.setMinimumWidth(0)
        self.buttonFrame.setMaximumWidth(16777215)
        self.buttonFrame.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.buttonFrame.setMinimumHeight(self.PlaylistCategoryFrame.maximumHeight())
        self.buttonFrame.setMaximumHeight(self.PlaylistCategoryFrame.maximumHeight())
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
        stylesheetTemplate = Template('\n                QLabel#sectionTitleLabel {\n                    font-size: ${sectionTitleFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${sectionTitleFontSize}pt;\n                    background-color: transparent;\n                    border: none;\n                }\n                QPushButton#leftButton, #rightButton, #moreButton {\n                    background-color: rgb(31, 31, 31); \n                }\n                QPushButton:checked {\n                    text-decoration: underline;\n                    color: $checkedFontColor;\n    \n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('fontColor', 'sectionTitleFontSize', 'checkedFontColor')))
        self.qobuz.getPlaylistCategory()

    
    def onToggled(self, button, checked):
        if checked:
            self.category = button.tag.trackSlug if button.tag else ''
            logger.debug(f'''self.category == {self.category}''')

    
    def showSkeleton(self):
        model = LPListViewSkeletonListModel(6, self.listView)
        self.listView.setModel(model)
        self.skeletonDelegate.startAnimation()
        delegate = LPListViewSkeletonDelegateWithSize(self.listView, 190, 265)
        self.listView.setItemDelegate(delegate)

    
    def endSkeleton(self):
        self.skeletonDelegate.stopAnimation()

    
    def showContent(self, section, playlist):
        self.endSkeleton()
        self.playList = playlist
        if playlist and playlist.list:
            self.displayButtons(True)
            self.stackedWidget.setCurrentIndex(0)
            model = LPQobuzPlaylistListModel(self.playList, self.listView)
            self.listView.setModel(model)
            delegate = LPQobuzPlaylistDelegate(self.listView)
            self.listView.setItemDelegate(delegate)
        else:
            self.emptyLabel.setText(QCoreApplication.translate('qobuz playlist frame', QobuzSectionTip.NO_Show_Results.value))
            self.displayButtons(False)
            self.stackedWidget.setCurrentIndex(1)

    
    def displayButtons(self, display = (True,)):
        self.leftButton.setVisible(display)
        self.rightButton.setVisible(display)
        self.moreButton.setVisible(display)

    
    def _updateCategory(self):
        logger.debug('_updateCategory====')
        tagsPlayList = self.qobuz.categoryList
        if not tagsPlayList or tagsPlayList.list:
            return None
        for tagItem in None.list:
            objectName = tagItem.trackName + 'CategoryButton'
            btn = self.buttonFrame.findChild(QPushButton, objectName)
            if btn is not None:
                continue
            btn = QPushButton(tagItem.trackName.replace('&', '&&'))
            btn.setCheckable(True)
            btn.setObjectName(objectName)
            btn.tag = tagItem
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.categoryButtonGroup.addButton(btn)
            self.buttonFrame.layout().addWidget(btn)
        self.buttonFrame.adjustSize()
        self._updateCategoryNavButtons()

    
    def _updateCategoryNavButtons(self):
        '''按内容宽度与容器宽度更新左右翻页箭头可见性,并校正偏移'''
        LPQobuzUtil.updateCategoryNavButtons(self._categoryContainer, self.buttonFrame)

    
    def eventFilter(self = None, obj = None, event = None):
        '''分类容器尺寸变化(窗口宽度/箭头显隐引起)时校正偏移并更新箭头'''
        if obj is self._categoryContainer and event.type() == QEvent.Type.Resize:
            self._updateCategoryNavButtons()
        return super().eventFilter(obj, event)

    
    def onCategoryButtonClicked(self = None, categoryButton = None):
        logger.debug(f'''{categoryButton.objectName()} clicked!''')
        
        def callback(result = None):
            self.showContent('', result.data)

        category = categoryButton.tag.trackSlug if categoryButton.tag else ''
        genres = self.disGenreManager.getSelectedGenreStr()
        reqFunc = self.qobuz.requestMgr.fetchFeaturedData
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_PLAYLIST, 'last-created', genres, category)

    
    def onSeeAllButtonClicked(self):
        headType = self.playList.header.headType
        if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistSeeAllViewControllerUI, Ui_qobuzPlaylistSeeAllWidget, LPQobuzPlaylistSeeAllViewController, self.category), 'qobuzdetail')

    
    def onItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        if None.playList and self.playList.list:
            headType = self.playList.header.headType
            if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistDetailViewControllerUI, Ui_qobuzPlaylistDetailViewWidget, LPQobuzPlaylistDetailViewController, playItem), 'qobuzdetail')

    
    def updateListViewNavButtons(self):
        LPQobuzUtil.updateListViewNavButtons(self.bar, self.leftButton, self.rightButton)

    
    def onLeftButtonClicked(self):
        LPQobuzUtil.scrollByItems(-1, self.listView)

    
    def onRightButtonClicked(self):
        LPQobuzUtil.scrollByItems(1, self.listView)

    __classcell__ = None

