# Source Generated with Decompyle++
# File: LPQobuzArtistDetailListFrameViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/4 10:29
@Auth ： Chris
@File ：LPQobuzArtistDetailViewController.py
@Desc:
'''
from functools import partial
from string import Template
from PyQt6.QtCore import QModelIndex, Qt, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractItemView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzArtistDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistDelegate, LPQobuzPlaylistListModel
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailListView import LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.LPQobuzArtistDetailAlbumSeeAllViewController import LPQobuzArtistDetailAlbumSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.LPQobuzArtistDetailArtistSeeAllViewController import LPQobuzArtistDetailArtistSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.UI.LPQobuzArtistDetailAlbumSeeAllViewController_ui import Ui_qobuzArtistAlbumSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.UI.LPQobuzArtistDetailArtistSeeAllViewController_ui import Ui_qobuzArtistArtistSeeAllWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzArtistDetailListFrameViewController(LPQobuzBaseViewController):
    
    def __init__(self = None, section = None, playList = None):
        super().__init__()
        self.section = section
        self.playList = playList

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setFlow(self.listViewDefaultFlow)
        self.listView.setSpacing(self.listViewDefaultSpacing)
        self.listView.clicked.connect(self.onListViewItemClicked)
        self.listView.wheelEvent = self.listViewWheelEvent
        self.listView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.bar = self.listView.horizontalScrollBar()
        self.bar.rangeChanged.connect(self.updateListViewNavButtons)
        self.bar.valueChanged.connect(self.updateListViewNavButtons)
        self.leftButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.leftButton.setStyleSheet('border-radius: 12px;')
        self.leftButton.clicked.connect(self.onLeftButtonClicked)
        self.leftButton.setCursor(Qt.CursorShape.ArrowCursor)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('nav_prev.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        self.leftButton.setIcon(QIcon(tintImage))
        self.rightButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rightButton.setStyleSheet('border-radius: 12px;')
        self.rightButton.clicked.connect(self.onRightButtonClicked)
        self.rightButton.setCursor(Qt.CursorShape.ArrowCursor)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('nav_next.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        self.rightButton.setIcon(QIcon(tintImage))
        self.sectionTitleLabel.setText(self.section)
        self.moreButton.setText(self.seeAllText)
        self.moreButton.setStyleSheet('border-radius: 12px;')
        hasMore = self.playList.header.hasMore
        if not hasMore:
            self.moreButton.setVisible(False)
        headType = self.playList.header.headType
        if headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            model = LPQobuzPlaylistListModel(self.playList, self.listView)
        else:
            model = LPQobuzListModel(self.playList, self.listView)
        self.listView.setModel(model)
        if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            delegate = LPQobuzAlbumDelegate(self.listView)
        elif headType == LPHeaderType.LP_HEADER_TYPE_ARTIST:
            delegate = LPQobuzArtistDelegate(self.listView)
        elif headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
            delegate = LPQobuzPlaylistDelegate(self.listView)
        self.listView.setItemDelegate(delegate)
        self.moreButton.clicked.connect(self.onSeeAllButtonClicked)
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${titeFontSize}pt;\n                }\n                QLabel#sectionTitleLabel {\n                    font-size: ${subTitleFontSize}pt;\n                }\n                QButton#artistButton {\n                    font-size: ${artistSubTiteFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#SA_TitleLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton#SimilarAlbumsLeftButton, #SimilarAlbumsRightButton, #SimilarAlbumsMoreButton {\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QPushButton#leftButton, #rightButton, #moreButton {\n                    background-color: rgb(31, 31, 31); \n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{MyMusic_Subtitle}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('titeFontSize', 'artistSubTiteFontSize', 'fontColor', 'subTitleFontSize', 'weeklyQTitleFrameBg')))

    
    def onSeeAllButtonClicked(self):
        artistId = self.playList.header.headId
        if not artistId:
            return None
        headType = None.playList.header.headType
        if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailAlbumSeeAllViewControllerUI, Ui_qobuzArtistAlbumSeeAllWidget, LPQobuzArtistDetailAlbumSeeAllViewController, self.section, artistId), 'qobuzseeall')
        elif headType == LPHeaderType.LP_HEADER_TYPE_ARTIST:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailArtistSeeAllViewControllerUI, Ui_qobuzArtistArtistSeeAllWidget, LPQobuzArtistDetailArtistSeeAllViewController, self.section, artistId), 'qobuzseeall')

    
    def onListViewItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        if None.playList and self.playList.list:
            headType = self.playList.header.headType
            if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
                streamable = playItem.streamable
                if not streamable:
                    LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz fav album see all', 'This album is not available'), LPGlobalUI.mainWindow)
                    logger.debug('qobuz artist->album %s not streamable' % playItem.trackName)
                    return None
                LPQobuzAlbumDetailViewController = LPQobuzAlbumDetailViewController
                import HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, playItem), 'qobuzdetail')
            elif headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
                LPQobuzPlaylistDetailViewController = LPQobuzPlaylistDetailViewController
                import HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistDetailViewControllerUI, Ui_qobuzPlaylistDetailViewWidget, LPQobuzPlaylistDetailViewController, playItem), 'qobuzdetail')
            elif headType == LPHeaderType.LP_HEADER_TYPE_ARTIST:
                LPQobuzArtistDetailViewController = LPQobuzArtistDetailViewController
                import HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, playItem), 'qobuzdetail')

    
    def updateListViewNavButtons(self):
        LPQobuzUtil.updateListViewNavButtons(self.bar, self.leftButton, self.rightButton)

    
    def onLeftButtonClicked(self):
        LPQobuzUtil.scrollByItems(-1, self.listView)

    
    def onRightButtonClicked(self):
        LPQobuzUtil.scrollByItems(1, self.listView)

    __classcell__ = None

