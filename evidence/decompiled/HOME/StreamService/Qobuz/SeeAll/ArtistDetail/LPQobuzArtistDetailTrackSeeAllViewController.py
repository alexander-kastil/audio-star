# Source Generated with Decompyle++
# File: LPQobuzArtistDetailTrackSeeAllViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/17 9:17
@Auth ： Chris
@File ：LPQobuzArtistDetailTrackSeeAllViewController.py
@Desc:
'''
from functools import partial
from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QHeaderView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.SeeAll.LPQobuzSeeAllBaseViewController import LPQobuzSeeAllBaseViewController
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPClientFramework.LPUtility import logger

class LPQobuzArtistDetailTrackSeeAllViewController(LPQobuzSeeAllBaseViewController):
    updateContentSignal = pyqtSignal()
    
    def __init__(self = None, section = None, playList = None):
        super().__init__()
        self.playList = playList
        self.section = section

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.titleLabel.setText(self.section)
        self.tableView.setupUI()
        self.tableView.doubleClicked.connect(self.itemDoubleClick)
        self.tableView.clicked.connect(self.onItemClick)
        stylesheetTemplate = Template('\n                QWidget {\n                    border:none;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('subTitleFontSize', 'fontColor', 'checkedFontColor')))

    
    def viewWillAppear(self):
        self.updateUI()

    
    def viewWillDisappear(self):
        pass

    
    def updateUI(self):
        self.checkPlayListFavorite(self.playList)
        model = LPQobuzTracksTableWithCoverModel(self.playList, self.tableView)
        delegate = LPQobuzTrackTableWithCoverDelegate(self.tableView)
        delegate.favClicked.connect(self.onFavClicked)
        delegate.optClicked.connect(self.onOptClicked)
        self.tableView.setModel(model)
        self.tableView.setItemDelegate(delegate)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableView.setColumnWidth(2, 200)
        self.tableView.setColumnWidth(3, 150)
        self.tableView.setColumnWidth(4, 50)
        self.tableView.setColumnWidth(5, 50)
        self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    
    def onItemClick(self, index):
        if self.tableView.lastCursorActionIndex:
            data = index.data()
            if data is None:
                return None
            itemType = None[2]
            if itemType == 'artist':
                artistPlayItem = LPQobuzPlayItem()
                artistPlayItem.trackId = data[3]
                artistPlayItem.trackName = data[0]
                LPQobuzArtistDetailViewController = LPQobuzArtistDetailViewController
                import HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController
                Ui_qobuzArtistDetailViewWidget = Ui_qobuzArtistDetailViewWidget
                import HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistPlayItem), 'qobuzdetail')

    
    def itemDoubleClick(self, index):
        '''处理 artist see-all 页面双击播放。

        :param index: 当前双击的表格索引。
        :returns: None。
        '''
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        playList = None.tableView.model().playList
        playItem = playList.list[index.row()]
        if self.section == 'Most popular':
            playSection = 'top_tracks'
        else:
            playSection = 'tracks_appears_on'
        playList.header.playSection = playSection
        xml = playList.generateXML(str(index.row() + 1), playSection, **('playSection',))
        self.playQobuzPlayList(playList, playItem, xml, index.row(), 'qobuz artist see all', playList.header, **('playIndex', 'logPrefix', 'header'))

    
    def onFavClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        playItem.isFavorite = not (playItem.isFavorite)
        itemId = playItem.trackId
        changeType = 'add' if playItem.isFavorite else 'delete'
        callback = partial(self.favoriteCallback, changeType, LPHeaderType.LP_HEADER_TYPE_SONG, itemId)
        reqFunc = self.qobuz.requestMgr.changeFavoriteStatus
        self.qobuz.requestMgr.fetch(reqFunc, callback, LPHeaderType.LP_HEADER_TYPE_SONG, itemId, changeType)

    
    def onOptClicked(self, index):
        data = self.tableView.model()._data
        playItem = data[index.row()]
        trackMoreMenu = LPQobuzTrackMoreMenu(playItem, self.playItem, self.tableView)
        trackMoreMenu.setupUI()
        trackMoreMenu.showMenu(QCursor.pos())

    __classcell__ = None

