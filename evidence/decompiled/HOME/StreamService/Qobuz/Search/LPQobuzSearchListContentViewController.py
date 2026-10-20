# Source Generated with Decompyle++
# File: LPQobuzSearchListContentViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/8 10:12
@Auth ： Chris
@File ：LPQobuzSearchContentViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import pyqtSignal, QModelIndex, QCoreApplication
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzArtistDelegate, LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistListModel, LPQobuzPlaylistDelegate
from HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController import LPQobuzAlbumDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController import LPQobuzPlaylistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchBaseViewController import LPQobuzSearchBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSearchTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType

class LPQobuzSearchListContentViewController(LPQobuzSearchBaseViewController):
    initViewSignal = pyqtSignal(object, object)
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.parent = parent
        self.setParent(parent)
        self.offset = 50
        self.limit = 50
        self.total = self.defaultTotal
        self.loading = False
        self.firstShow = True
        self.itemType = None
        self.queryText = ''
        self.viewBinding = {
            'Artists': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ARTIST,
                'model': LPQobuzListModel,
                'delegate': LPQobuzArtistDelegate },
            'Albums': {
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'model': LPQobuzListModel,
                'delegate': LPQobuzAlbumDelegate },
            'Playlists': {
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST,
                'model': LPQobuzPlaylistListModel,
                'delegate': LPQobuzPlaylistDelegate } }
        self.initViewSignal.connect(self._initView)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.setupUI()
        self.listView.setFlow(self.listViewDefaultFlow)
        self.listView.setSpacing(self.listViewDefaultSpacing)
        self.listView.clicked.connect(self.onItemClicked)
        self.scrollBar = self.listView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onScroll)
        stylesheetTemplate = Template('\n                        QWidget {\n                            border: none;\n                        }\n                        QFrame {\n                            color: $fontColor;\n                        }\n                ')
        self.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), **('fontColor',)))

    
    def _initView(self, summaryDict, tag):
        binding = self.viewBinding.get(tag)
        self.headType = binding['headType']
        modelClass = binding['model']
        delegateClass = binding['delegate']
        playList = summaryDict.get(LPQobuzUtil.qobuzHeadTypeMapping.get(self.headType))
        self.queryText = playList.header.searchQueryText
        self.total = playList.header.total
        if len(playList.list) > 0:
            self.stackedWidget.setCurrentIndex(0)
            model = modelClass(playList, self.listView)
            self.listView.setModel(model)
            delegate = delegateClass(self.listView)
            self.listView.setItemDelegate(delegate)
        else:
            self.emptyLabel.setText(QCoreApplication.translate('qobuz search', QobuzSearchTip.NO_Results.value))
            self.stackedWidget.setCurrentIndex(1)

    
    def onScroll(self, value):
        if not self.headType:
            return None
        if None + self.scrollBar.pageStep() >= self.scrollBar.maximum() - 10:
            self.loadMore()

    
    def loadMore(self):
        if self.loading:
            return None
        if None.offset >= self.total:
            return None
        self.loading = None
        self.loadData()

    
    def loadData(self = None):
        super().loadData()
        reqFunc = self.qobuz.requestMgr.fetchSearchData
        self.qobuz.requestMgr.fetch(reqFunc, self.onDataLoadCallback, self.queryText, self.headType, self.offset, self.limit)

    
    def onDataLoadCallback(self = None, result = None):
        super().onDataLoadCallback()
        playList = result.data
        self.listView.model().addItemList(playList)
        self.offset += self.limit
        self.loading = False

    
    def onItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        playList = None.listView.model().playList
        if playList and playList.list:
            headType = playList.header.headType
            if headType == LPHeaderType.LP_HEADER_TYPE_ALBUM:
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, playItem), 'qobuzdetail')
            elif headType == LPHeaderType.LP_HEADER_TYPE_PLAYLIST:
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzPlaylistDetailViewControllerUI, Ui_qobuzPlaylistDetailViewWidget, LPQobuzPlaylistDetailViewController, playItem), 'qobuzdetail')
            elif headType == LPHeaderType.LP_HEADER_TYPE_ARTIST:
                LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, playItem), 'qobuzdetail')

    __classcell__ = None

