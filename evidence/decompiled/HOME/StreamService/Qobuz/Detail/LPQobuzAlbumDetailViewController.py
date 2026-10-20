# Source Generated with Decompyle++
# File: LPQobuzAlbumDetailViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/4 9:56
@Auth ： Chris
@File ：LPQobuzAlbumDetailViewController.py
@Desc:
'''
import threading
from functools import partial
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot, QModelIndex
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QListView, QTableView, QPushButton, QHeaderView, QAbstractItemView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzAlbumTrackTableView import LPQobuzAlbumTracksTableModel, LPQobuzAlbumTrackTableDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzDetailBaseViewController import LPQobuzDetailBaseViewController, ShuffleCacheType
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.SeeAll.UI.LPQobuzAlbumSeeAllViewController_ui import Ui_qobuzAlbumSeeAllWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPClientFramework.LPUtility import logger

class LPQobuzAlbumDetailViewController(LPQobuzDetailBaseViewController):
    updateDeviceInfoSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updateSimilarAlbumSignal = pyqtSignal(object)
    updateAlbumDetailSignal = pyqtSignal(object)
    updateQualityFrameSignal = pyqtSignal()
    updateHeadFrameSignal = pyqtSignal()
    initListViewSignal = pyqtSignal(object)
    
    def __init__(self = None, playItem = None):
        super().__init__()
        self.playItem = playItem
        self.itemId = playItem.trackId
        self.itemType = LPHeaderType.LP_HEADER_TYPE_ALBUM
        self.onFavClickedMethod = self.onFavClicked
        self.shuffleCacheType = ShuffleCacheType.ALBUM_SHUFFLE
        self.coverImage = None
        self.genreStr = LPQobuzUtil.getPlayItemGenreStr(playItem)
        self.updateCoverImageSignal.connect(self._updateCoverImage)
        self.updateSimilarAlbumSignal.connect(self._updateSimilarAlbums)
        self.updateAlbumDetailSignal.connect(self._updateAlbumDetail)
        self.updateQualityFrameSignal.connect(self.updateQualityFrame)
        self.updateHeadFrameSignal.connect(self.updateHeadFrame)
        self.initListViewSignal.connect(self.initListView)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.viewBinding = [
            {
                'id': 'track',
                'component': self.tableView,
                'headType': LPHeaderType.LP_HEADER_TYPE_COLLECTION,
                'model': LPQobuzAlbumTracksTableModel,
                'delegate': LPQobuzAlbumTrackTableDelegate,
                'signal': self.updateAlbumDetailSignal,
                'playList': None },
            {
                'id': 'SA',
                'component': self.SimilarAlbumsListView,
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM,
                'model': LPQobuzListModel,
                'delegate': LPQobuzAlbumDelegate,
                'signal': self.updateSimilarAlbumSignal,
                'seeAllComponent': self.SimilarAlbumsMoreButton,
                'leftComponent': self.SimilarAlbumsLeftButton,
                'rightComponent': self.SimilarAlbumsRightButton,
                'playList': None }]
        for binding in self.viewBinding:
            component = binding.get('component', None)
            if component and isinstance(component, QListView):
                component.wheelEvent = self.listViewWheelEvent
                component.setFlow(self.listViewDefaultFlow)
                component.setSpacing(self.listViewDefaultSpacing)
                component.clicked.connect(self.onListViewItemClicked)
                component.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
                bar = component.horizontalScrollBar()
                slotFunc = partial(self.updateListViewNavButtons, bar, binding.get('leftComponent', None), binding.get('rightComponent', None))
                bar.rangeChanged.connect(slotFunc)
                bar.valueChanged.connect(slotFunc)
            if component and isinstance(component, QTableView):
                component.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                component.doubleClicked.connect(self.itemDoubleClick)
                component.clicked.connect(self.onTableViewItemClick)
                component.setupUI()
            seeAllButton = binding.get('seeAllComponent', None)
            if seeAllButton and isinstance(seeAllButton, QPushButton):
                seeAllButton.setText(self.seeAllText)
                seeAllButton.setCursor(Qt.CursorShape.PointingHandCursor)
                seeAllButton.setStyleSheet('border-radius: 10px;')
                seeAllButton.clicked.connect(self.onSeeAllButtonClicked)
            leftButton = binding.get('leftComponent', None)
            if leftButton and isinstance(leftButton, QPushButton):
                leftButton.setCursor(Qt.CursorShape.PointingHandCursor)
                leftButton.setStyleSheet('border-radius: 10px;')
                slotFunc = partial(self.onLeftButtonClicked, component)
                leftButton.clicked.connect(slotFunc)
            rightButton = binding.get('rightComponent', None)
            if rightButton and isinstance(rightButton, QPushButton):
                rightButton.setIcon(QIcon(LPGlobalUI.imagePath('nav_next.png')))
                rightButton.setCursor(Qt.CursorShape.PointingHandCursor)
                rightButton.setStyleSheet('border-radius: 10px;')
                slotFunc = partial(self.onRightButtonClicked, component)
                rightButton.clicked.connect(slotFunc)
                continue
                self.titleLabel.setText(self.playItem.trackName)
                descriptionList = []
                if self.playItem.label:
                    descriptionList.append('Released by ' + self.playItem.label)
        if self.playItem.date:
            dateStr = LPQobuzUtil.formatDate(self.playItem.date)
            descriptionList.append(dateStr)
        if self.playItem.tracksCount:
            descriptionList.append(str(self.playItem.tracksCount) + ' Tracks')
        if self.playItem.trackDuration:
            duration = LPQobuzUtil.formatAlbumDuration(self.playItem.trackDuration)
            descriptionList.append(duration)
        descriptionText = ' · '.join(descriptionList)
        self.decriptionLabel.setText(descriptionText)
        if self.playItem.parentalWarning:
            self.artistButton.setIcon(QIcon(LPGlobalUI.imagePath('./qobuz/e_warning.png')))
        artistText = self.playItem.trackArtist
        if artistText:
            artistText = artistText.replace('&', '&&')
            self.artistButton.setText(artistText)
        self.artistButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.artistButton.clicked.connect(self.artistButtonPressed)
        pixmap = LPUtility.getCachedPixmapWithUrl(self.playItem.trackImage)
        if not pixmap:
            
            def _fetchCoverImageMethod():
                respDict = LPUtility.fetchUrlQPixmap(self.playItem.albumImage)
                _pixmap = respDict.get('image', None)
                if _pixmap:
                    self.updateCoverImageSignal.emit(_pixmap)

            t = Thread(_fetchCoverImageMethod, True, **('target', 'daemon'))
            t.start()
        else:
            self.updateCoverImageSignal.emit(pixmap)
        self.playNowButton.setIcon(QIcon(LPGlobalUI.imagePath('minibar/play.png')))
        slotFunc = partial(self.playNowButtonPressed, self.tableView)
        self.playNowButton.clicked.connect(slotFunc)
        self.shuffleButton.setIcon(QIcon(self.defaultShufflePixmap))
        self.shuffleButton.clicked.connect(self.shuffleButtonPressed)
        self._initShuffleButtonStatus()
        self.favoriteButton.setIcon(QIcon(self.unFavoritePixmap))
        self.favoriteButton.clicked.connect(self.favoriteButtonPressed)
        self.initFavoriteButtonStatus()
        self.presetButton.setIcon(QIcon(self.presetPixmap))
        self.presetButton.clicked.connect(self.presetButtonPressed)
        self.presetButton.source = self.source
        self.moreButton.hide()
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${titeFontSize}pt;\n                }\n                QLabel#decriptionLabel {\n                    color: rgba(255, 255, 255, 168);\n                }\n                QButton#artistButton {\n                    font-size: ${artistSubTiteFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#SA_SplitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#SA_TitleLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton#SimilarAlbumsLeftButton, #SimilarAlbumsRightButton, #SimilarAlbumsMoreButton {\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{MyMusic_Subtitle}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('titeFontSize', 'artistSubTiteFontSize', 'fontColor', 'subTitleFontSize', 'weeklyQTitleFrameBg')))

    
    def updateQualityFrame(self):
        if self.playList.header.hires:
            self.hiResButton.setIcon(QIcon(LPGlobalUI.imagePath('qobuz/hi-res.png')))
            qualityStr = self.playList.header.qualityStr
            if qualityStr:
                argList = qualityStr.split('/')
                arg1 = argList[0].split('bits')[0].strip() + '-Bit'
                arg2 = argList[-1].strip()
                self.arg1Label.setText(arg1)
                self.arg2Label.setText(arg2)
            else:
                self.qualityFrame.hide()

    
    def updateHeadFrame(self):
        header = self.playList.header
        if header:
            pixmap = LPUtility.getCachedPixmapWithUrl(header.imageUrl)
            if not pixmap:
                
                def _fetchCoverImageMethod():
                    respDict = LPUtility.fetchUrlQPixmap(header.imageUrl)
                    _pixmap = respDict.get('image', None)
                    if _pixmap:
                        self.updateCoverImageSignal.emit(_pixmap)

                t = Thread(_fetchCoverImageMethod, True, **('target', 'daemon'))
                t.start()
            else:
                self.updateCoverImageSignal.emit(pixmap)
            descriptionList = []
            if header.label:
                descriptionList.append('Released by ' + header.label)
            if header.date:
                dateStr = LPQobuzUtil.formatDate(header.date)
                descriptionList.append(dateStr)
            if header.total:
                descriptionList.append(str(header.total) + ' Tracks')
            if header.duration:
                duration = LPQobuzUtil.formatAlbumDuration(header.duration)
                descriptionList.append(duration)
            descriptionText = ' · '.join(descriptionList)
            self.decriptionLabel.setText(descriptionText)
            if self.playItem.parentalWarning:
                self.artistButton.setIcon(QIcon(LPGlobalUI.imagePath('./qobuz/e_warning.png')))
            artistText = header.trackArtist
            if artistText:
                artistText = artistText.replace('&', '&&')
                self.artistButton.setText(artistText)

    
    def artistButtonPressed(self):
        logger.debug('[LPQobuzAlbumDetailViewController] artistButtonPressed')
        self.viewArtistPage()

    
    def viewArtistPage(self):
        artistPlayItem = LPQobuzPlayItem()
        artistPlayItem.trackId = self.playItem.artistId
        artistPlayItem.trackName = self.playItem.trackArtist
        artistPlayItem.isArtist = True
        LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailViewControllerUI, Ui_qobuzArtistDetailViewWidget, LPQobuzArtistDetailViewController, artistPlayItem), 'qobuzdetail')

    
    def _updateCoverImage(self, pixmap):
        self.coverImage = pixmap
        if not self.coverImage:
            self.coverImage = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon = QIcon()
        icon.addPixmap(self.coverImage)
        self.coverImageView.setIcon(icon)

    
    def viewWillAppear(self):
        LPUtility.registerDeviceInfoChanged(self)
        self.updateUI()

    
    def viewWillDisappear(self):
        LPUtility.deRegisterDeviceInfoChanged(self)

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None.get('playState', None) is not None:
            self.updateTableviewSignal.emit()

    
    def updateUI(self):
        '''按当前 section 状态刷新页面内容。'''
        for binding in self.viewBinding:
            if binding['playList']:
                self.initSection(binding)
                logger.debug(f'''Section == {binding['id']} load from binding''')
                continue
            if not binding['id'] == 'SA' and self.genreStr:
                continue
            binding.get('signal', None).emit(binding)

    
    def _requestSimilarAlbumsIfNeeded(self):
        '''在拿到曲目详情后补发 Similar albums 请求。

        :returns: None
        '''
        for binding in self.viewBinding:
            if binding['id'] != 'SA' or binding['playList']:
                continue
            if self.genreStr and self.playList and self.playList.list:
                for playItem in self.playList.list:
                    genreStr = LPQobuzUtil.getPlayItemGenreStr(playItem)
                    if genreStr:
                        self.genreStr = genreStr
                    
                    binding.get('signal', None).emit(binding)
                    return None
                    return None

    
    def initSection(self, binding):
        if binding['id'] == 'track':
            self.playList = binding['playList']
            self.checkPlayListFavorite(self.playList)
            self.updateQualityFrameSignal.emit()
            self.updateHeadFrameSignal.emit()
            self.initTableViewSignal.emit(self.tableView)
        else:
            self.initListViewSignal.emit(binding)

    
    def onSeeAllButtonClicked(self):
        LPQobuzAlbumSeeAllViewController = LPQobuzAlbumSeeAllViewController
        import HOME.StreamService.Qobuz.SeeAll.LPQobuzAlbumSeeAllViewController
        LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumSeeAllViewControllerUI, Ui_qobuzAlbumSeeAllWidget, LPQobuzAlbumSeeAllViewController, 'Similar albums', self.genreStr), 'qobuzdetail')

    
    def _updateAlbumDetail(self, binding):
        
        def finishedMethod(result = None):
            playList = result.data
            self.total = playList.header.total
            self.checkPlayListFavorite(playList)
            if self.offset == 0:
                self.playList = playList
            else:
                self.tableView.model().addItemList(playList)
            self.offset += self.limit
            self._requestSimilarAlbumsIfNeeded()
            hasMore = self.checkMore()

        self._loadSkeleton(True, **('isFixHeight',))
        reqFunc = self.qobuz.requestMgr.fetchAlbumDetailData
        self.qobuz.requestMgr.fetch(reqFunc, finishedMethod, self.itemId, self.offset, self.limit)

    
    def _initTableview(self, tableView):
        self._endSkeleton()
        model = LPQobuzAlbumTracksTableModel(self.playList, tableView)
        delegate = LPQobuzAlbumTrackTableDelegate(tableView)
        tableView.setModel(model)
        tableView.horizontalHeader().setVisible(True)
        tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        delegate.favClicked.connect(self.onFavClickedMethod)
        delegate.optClicked.connect(self.onOptClicked)
        headerRows = model.getheaderRows()
        if headerRows:
            for row in range(model.rowCount()):
                if row in headerRows:
                    tableView.setRowHeight(row, 95)
                    continue
                tableView.setRowHeight(row, 60)
        tableView.setItemDelegate(delegate)
        tableView.setColumnWidth(0, 50)
        tableView.setColumnWidth(2, 200)
        tableView.setColumnWidth(3, 150)
        tableView.setColumnWidth(4, 50)
        tableView.setColumnWidth(5, 50)
        tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        LPQobuzUtil.adjustTableViewHeight(tableView)

    
    def _updateSimilarAlbums(self, binding):
        bindingCallback = partial(self.onDataLoadCallback, binding)
        reqFunc = self.qobuz.requestMgr.fetchSimilarAlbumData
        self.qobuz.requestMgr.fetch(reqFunc, bindingCallback, self.genreStr)

    _updateSimilarAlbums = pyqtSlot(object)(_updateSimilarAlbums)
    
    def onDataLoadCallback(self = None, binding = None, result = None):
        if result.is_success():
            playList = result.data
            binding['playList'] = playList
            self.initListViewSignal.emit(binding)

    
    def initListView(self, binding):
        component = binding.get('component', None)
        modelClass = binding.get('model', None)
        delegateClass = binding.get('delegate', None)
        playList = binding['playList']
        model = modelClass(playList, component)
        component.setModel(model)
        delegate = delegateClass(component)
        component.setItemDelegate(delegate)

    
    def onListViewItemClicked(self = None, index = None):
        playItem = index.data()
        if not playItem:
            return None
        if None.isAlbum:
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzAlbumDetailViewControllerUI, Ui_qobuzAlbumDetailViewWidget, LPQobuzAlbumDetailViewController, playItem), 'qobuzdetail')

    
    def _initShuffleButtonStatus(self):
        if not self.qobuz.fileCache.readCache(ShuffleCacheType.ALBUM_SHUFFLE):
            pass
        data = { }
        shuffleIds = data.get(ShuffleCacheType.ALBUM_SHUFFLE.value, [])
        if self.itemId in shuffleIds:
            self.isShuffle = True
        self.updateShuffleButtonSignal.emit(self.shuffleButton)

    
    def updateListViewNavButtons(self, bar, leftButton, rightButton):
        LPQobuzUtil.updateListViewNavButtons(bar, leftButton, rightButton)

    
    def onLeftButtonClicked(self, listview):
        LPQobuzUtil.scrollByItems(-1, listview)

    
    def onRightButtonClicked(self, listview):
        LPQobuzUtil.scrollByItems(1, listview)

    __classcell__ = None

