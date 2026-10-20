# Source Generated with Decompyle++
# File: LPQobuzArtistDetailTableFrameViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/7 11:19
@Auth ： Chris
@File ：LPQobuzArtistDetailViewController.py
@Desc:
'''
import random
from functools import partial
from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QCoreApplication
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QHeaderView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailTableView import LPQobuzArtistTracksTableWithCoverModel
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.LPQobuzArtistDetailTrackSeeAllViewController import LPQobuzArtistDetailTrackSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.ArtistDetail.UI.LPQobuzArtistDetailTrackSeeAllViewController_ui import Ui_qobuzArtistTrackSeeAllWidget
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPShuffleManager import LPShuffleManager
from LPClientFramework.LPUtility import logger

class LPQobuzArtistDetailTableFrameViewController(LPQobuzBaseViewController):
    updateDeviceInfoSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updateArtistDetailSignal = pyqtSignal()
    
    def __init__(self = None, section = None, playList = None, parent = None):
        super().__init__()
        self.section = section
        self.playList = playList
        self.parent = parent
        self.playItem = parent.playItem

    
    def _updateTableview(self):
        self.tableView.update()

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        if self.section == 'Most popular':
            self.parent.playNowButton.clicked.connect(self._parentPlayNowButtonPressed)
        self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tableView.doubleClicked.connect(self.itemDoubleClick)
        self.tableView.clicked.connect(self.onTableViewItemClick)
        self.tableView.setupUI()
        self.sectionTitleLabel.setText(self.section)
        self.moreButton.setText(self.seeAllText)
        self.moreButton.clicked.connect(self.onSeeAllButtonClicked)
        self.moreButton.setStyleSheet('border-radius: 12px;')
        model = LPQobuzArtistTracksTableWithCoverModel(self.playList, self.tableView)
        self.tableView.setModel(model)
        delegate = LPQobuzTrackTableWithCoverDelegate(self.tableView)
        delegate.favClicked.connect(self.onFavClicked)
        delegate.optClicked.connect(self.onOptClicked)
        self.tableView.setItemDelegate(delegate)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableView.setColumnWidth(2, 200)
        self.tableView.setColumnWidth(3, 150)
        self.tableView.setColumnWidth(4, 50)
        self.tableView.setColumnWidth(5, 50)
        QTimer.singleShot(0, self.adjustHeight)
        stylesheetTemplate = Template('\n                QLabel#sectionTitleLabel {\n                    font-size: ${subTitleFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton#SimilarAlbumsLeftButton, #SimilarAlbumsRightButton, #SimilarAlbumsMoreButton {\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QPushButton#moreButton {\n                    background-color: rgb(31, 31, 31); \n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{MyMusic_Subtitle}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('titeFontSize', 'artistSubTiteFontSize', 'fontColor', 'subTitleFontSize', 'weeklyQTitleFrameBg')))

    
    def adjustHeight(self):
        total = self.tableView.horizontalHeader().height()
        for row in range(self.tableView.model().rowCount()):
            total += self.tableView.rowHeight(row)
        self.tableView.setFixedHeight(total + 50)

    
    def onOptClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        trackMoreMenu = LPQobuzTrackMoreMenu(playItem, self.playItem, self.tableView)
        trackMoreMenu.setupUI()
        trackMoreMenu.showMenu(QCursor.pos())

    
    def onFavClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'add' if playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, LPHeaderType.LP_HEADER_TYPE_SONG, itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    
    def _parentPlayNowButtonPressed(self):
        '''处理 artist 页顶部播放按钮点击。

        :param: 无。
        :returns: None。
        '''
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        if not None.playList:
            logger.warning('error, self.playList not ready')
            return None
        if None.parent.isShuffle:
            row = random.randint(1, len(self.playList.list))
            LPShuffleManager.setShuffle()
        else:
            row = 1
            LPShuffleManager.setNoShuffle()
        playItem = self.playList.list[row - 1]
        startIndex = playItem.startIndex
        playSection = 'top_tracks'
        self.playList.header.searchUrl = playItem.searchUrl
        self.playList.header.playSection = playSection
        xml = self.playList.generateXML(str(startIndex), playSection, **('playSection',))
        self.playQobuzPlayList(self.playList, playItem, xml, row - 1, 'qobuz artist detail section top_tracks', self.playList.header, **('playIndex', 'logPrefix', 'header'))

    
    def onSeeAllButtonClicked(self):
        headType = self.playList.header.headType
        if headType == LPHeaderType.LP_HEADER_TYPE_COLLECTION:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailTrackSeeAllViewControllerUI, Ui_qobuzArtistTrackSeeAllWidget, LPQobuzArtistDetailTrackSeeAllViewController, self.section, self.playList), 'qobuzseeall')

    
    def itemDoubleClick(self, index):
        '''处理 artist 页表格双击播放。

        :param index: 当前双击的表格索引。
        :returns: None。
        '''
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        playList = None.tableView.model().playList
        playItem = playList.list[index.row()]
        streamable = playItem.streamable
        if not streamable:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz playlist detail', 'This track is not available'), LPGlobalUI.mainWindow)
            logger.debug('qobuz track %s not streamable' % playItem.trackName)
            return None
        if None.section == 'Most popular':
            playSection = 'top_tracks'
        else:
            playSection = 'tracks_appears_on'
        startIndex = str(playItem.startIndex)
        playList.header.searchUrl = playItem.searchUrl
        playList.header.playSection = playSection
        xml = playList.generateXML(startIndex, playSection, **('playSection',))
        self.playQobuzPlayList(playList, playItem, xml, index.row(), 'qobuz artist detail', playList.header, **('playIndex', 'logPrefix', 'header'))

    
    def onTableViewItemClick(self, index):
