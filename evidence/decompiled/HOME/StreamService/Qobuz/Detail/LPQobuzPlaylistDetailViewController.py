# Source Generated with Decompyle++
# File: LPQobuzPlaylistDetailViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/10 13:37
@Auth ： Chris
@File ：LPQobuzPlaylistDetailViewController.py
@Desc:
'''
import json
import threading
from functools import partial
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, Qt, QRectF, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QCursor, QPainterPath, QRegion
from PyQt6.QtWidgets import QTableView, QMessageBox, QHeaderView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzDetailBaseViewController import LPQobuzDetailBaseViewController, ShuffleCacheType
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import PlaylistIDCacheType
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzDetailTip
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPClientFramework.LPUtility import logger

class LPQobuzPlaylistDetailViewController(LPQobuzDetailBaseViewController):
    updateDeviceInfoSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updatePlaylistDetailSignal = pyqtSignal()
    noContentSignal = pyqtSignal()
    updateHeadSignal = pyqtSignal()
    
    def __init__(self = None, playItem = None):
        super().__init__()
        self.playItem = playItem
        self.itemId = playItem.trackId
        self.itemType = LPHeaderType.LP_HEADER_TYPE_PLAYLIST
        self.shuffleCacheType = ShuffleCacheType.PLAYLIST_SHUFFLE
        self.loading = False
        self.coverImage = None
        self.updatePlaylistDetailSignal.connect(self._updatePlaylistDetail)
        self.updateCoverImageSignal.connect(self._updateCoverImage)
        self.noContentSignal.connect(self.onNoContent)
        self.updateHeadSignal.connect(self.updateHead)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.dataBinding = [
            {
                'id': 'track',
                'component': self.tableView,
                'model': LPQobuzTracksTableWithCoverModel,
                'delegate': LPQobuzTrackTableWithCoverDelegate,
                'signal': self.updatePlaylistDetailSignal }]
        componentList = (lambda .0: [ binding['component'] for binding in .0 ])(self.dataBinding)
        for component in componentList:
            if isinstance(component, QTableView):
                component.doubleClicked.connect(self.itemDoubleClick)
                component.clicked.connect(self.onTableViewItemClick)
                component.setupUI()
                component.verticalHeader().setDefaultSectionSize(60)
                component.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
                self.scrollBar = component.verticalScrollBar()
                self.scrollBar.valueChanged.connect(self.onScroll)
                continue
                self.titleLabel.setText(self.playItem.trackName)
                self.updateButtonShow()
                self.updateDesc(self.playItem.isPublic, self.playItem.trackOwner, self.playItem.tracksCount, self.playItem.trackDuration)
                self.updateCoverImageSignal.emit(None)
                self.emptyLabel.setText(QCoreApplication.translate('qobuz playlist detail', QobuzDetailTip.NO_Show_Results.value))
                if not self.playItem.trackImage:
                    pass
        imageUrl = self.playItem.playlistImageList
        if isinstance(imageUrl, str):
            pixmap = LPUtility.getCachedPixmapWithUrl(imageUrl)
            if not pixmap:
                
                def _fetchCoverImageMethod():
                    respDict = LPUtility.fetchUrlQPixmap(imageUrl)
                    _pixmap = respDict.get('image', None)
                    if _pixmap:
                        self.updateCoverImageSignal.emit(_pixmap)

                t = Thread(_fetchCoverImageMethod, True, **('target', 'daemon'))
                t.start()
            else:
                self.updateCoverImageSignal.emit(pixmap)
        elif isinstance(imageUrl, list):
            pixmap = None
            if not pixmap:
                
                def _fetchCoverImageMethod():
                    pixmaps = []
                    for url in imageUrl:
                        respDict = LPUtility.fetchUrlQPixmap(url)
                        _pixmap = respDict.get('image', None)
                        if _pixmap:
                            pixmaps.append(_pixmap)
                            continue
                            if len(pixmaps) == len(imageUrl):
                                pixmap = LPQobuzUtil.composeFourPixmaps(pixmaps, self.coverImageView.width())
                                self.updateCoverImageSignal.emit(pixmap)

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
        self.presetButton.source = LPPlayListSource.Qobuz.value
        self.moreButton.hide()
        self.deleteButton.setIcon(QIcon(LPGlobalUI.imagePath('delete.png')))
        self.deleteButton.clicked.connect(self.onDeleteButtonPressed)
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${titeFontSize}pt;\n                }\n                QLabel#descriptionLabel {\n                    color: rgba(255, 255, 255, 168);\n                }\n                QPushButton#titleButton {\n                    font-size: ${titeFontSize}pt;\n                }\n                QPushButton#artistButton {\n                    font-size: ${artistSubTiteFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                    border:none;\n                }\n\n                QFrame#SA_SplitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#SA_TitleLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{MyMusic_Subtitle}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', **('titeFontSize', 'artistSubTiteFontSize', 'fontColor', 'subTitleFontSize')))

    
    def updateHead(self):
        header = self.playList.header
        self.updateDesc(header.isPublic, header.trackOwner, header.total, header.duration)

    
    def updateDesc(self, isPublic, trackOwner, tracksCount, trackDuration):
        if isPublic:
            descriptionText = 'Public playlist'
        else:
            descriptionText = 'Private playlist'
        if trackOwner:
            descriptionText += ' by ' + trackOwner
        if tracksCount:
            descriptionText += ' · ' + str(tracksCount) + ' tracks'
        if trackDuration:
            descriptionText += ' · ' + LPQobuzUtil.formatAlbumDuration(trackDuration)
        self.descriptionLabel.setText(descriptionText)

    
    def updateButtonShow(self):
        currentAccount = getattr(getattr(self.qobuz, 'loginMgr', None), 'account', None)
        currentOwnerId = getattr(currentAccount, 'userId', None)
        personal = False
        if currentOwnerId and str(currentOwnerId) == str(self.playItem.ownerId):
            personal = True
        if personal:
            self.favoriteButton.hide()
            self.deleteButton.setVisible(True)
        else:
            self.deleteButton.hide()
            self.favoriteButton.setVisible(True)

    
    def onDeleteButtonPressed(self):
        box = QMessageBox(self)
        box.setWindowFlags(box.windowFlags() | Qt.WindowType.FramelessWindowHint)
        box.setText(QCoreApplication.translate('qobuz playlist detail', "Are you sure you want to delete this playlist? This action \ncan't be undone."))
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.button(QMessageBox.StandardButton.Yes).setText(QCoreApplication.translate('qobuz playlist detail', 'Confirm'))
        box.button(QMessageBox.StandardButton.No).setText(QCoreApplication.translate('qobuz playlist detail', 'Cancel'))
        box.setStyleSheet('\n            QMessageBox {\n            background: %s;\n            border-radius: 10px;\n            }\n            QMessageBox QLabel {\n            color: %s;\n            padding-top: 30px;\n            padding-left: 10px;\n            padding-right: 10px;\n            background: transparent;\n            min-width:400 px;\n            }\n            QPushButton {background-color: transparent;\n            border-radius: 5px;\n            padding: 5px 10px 5px 10px;\n            color: %s;\n            }\n            QPushButton:hover {\n            color: %s;\n            }\n            QPushButton:focus {\n            color: %s;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_HIGH_HIGH_COLOR.name(), LPGlobalUI.THEME_HIGH_COLOR.name()))
        box.resize(300, 240)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.show()
        path = QPainterPath()
        rect = QRectF(0, 0, box.geometry().size().width(), box.geometry().size().height())
        path.addRoundedRect(rect, 10, 10)
        mask = QRegion(path.toFillPolygon().toPolygon())
        box.setMask(mask)
        select = box.exec()
        if select == QMessageBox.StandardButton.Yes:
            self.deletePlaylist()

    
    def deletePlaylist(self):
        
        def callback(result = None):
            if result.is_success():
                status = result.data
                if status == 'success':
                    logger.debug(f'''[qobuz playlist detail] delete playlist success--> id= {self.playItem.trackId} name={self.playItem.trackName}''')
                    LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz playlist detail', 'Delete playlist Ok'), LPGlobalUI.mainWindow)
                    LPGlobalUI.navigationManager.pop(LPGlobalUI.getTopWidget())
                else:
                    logger.debug(f'''[qobuz playlist detail] delete playlist failed--> id= {self.playItem.trackId} name={self.playItem.trackName}''')
                    LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz playlist detail', 'Delete playlist failed'), LPGlobalUI.mainWindow)

        reqFunc = self.qobuz.requestMgr.fetchDeletePlaylistData
        self.qobuz.requestMgr.fetch(reqFunc, callback, self.playItem.trackId)

    
    def _updateCoverImage(self, pixmap):
        self.coverImage = pixmap
        if not self.coverImage:
            self.coverImage = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        else:
            self.coverImage = LPUtility.createBlurredPixmap(self.coverImage)
        icon = QIcon()
        icon.addPixmap(self.coverImage)
        self.coverImageView.setIcon(icon)

    
    def viewWillAppear(self):
        LPUtility.registerDeviceInfoChanged(self)
        self.updateUI()

    
    def viewWillDisappear(self):
        LPUtility.deRegisterDeviceInfoChanged(self)

    
    def updateUI(self):
        for binding in self.dataBinding:
            if self.playList:
                self.updateHeadSignal.emit()
                self.checkPlayListFavorite(self.playList)
                self.initTableViewSignal.emit(self.tableView)
                continue
            self._loadSkeleton()
            binding.get('signal', None).emit()

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None.get('playState', None) is not None:
            self.updateTableviewSignal.emit()

    
    def _updatePlaylistDetail(self):
        
        def finishedMethod(result = None):
            playList = result.data
            self.total = playList.header.total
            self.checkPlayListFavorite(playList)
            if self.offset == 0:
                self.playList = playList
                if not self.playList.list:
                    self.noContentSignal.emit()
                    return None
                None.initTableViewSignal.emit(self.tableView)
                self.updateHeadSignal.emit()
            else:
                self.tableView.model().addItemList(playList)
            self.offset += self.limit
            self.loading = False

        reqFunc = self.qobuz.requestMgr.fetchPlaylistDetailData
        self.qobuz.requestMgr.fetch(reqFunc, finishedMethod, self.itemId, self.offset, self.limit, False, **('useCache',))

    
    def onNoContent(self):
        self.playNowButton.hide()
        self.shuffleButton.hide()
        self.favoriteButton.hide()
        self.presetButton.hide()
        self.moreButton.hide()
        self.stackedWidget.setCurrentIndex(1)

    onNoContent = pyqtSlot()(onNoContent)
    
    def _initShuffleButtonStatus(self):
        if not self.qobuz.fileCache.readCache(ShuffleCacheType.PLAYLIST_SHUFFLE):
            pass
        data = { }
        shuffleIds = data.get(ShuffleCacheType.PLAYLIST_SHUFFLE.value, [])
        if self.itemId in shuffleIds:
            self.isShuffle = True
        self.updateShuffleButtonSignal.emit(self.shuffleButton)

    
    def onScroll(self, value):
        if value + self.scrollBar.pageStep() >= self.scrollBar.maximum() - 10:
            self.loadMore()

    
    def loadMore(self):
        if self.loading:
            return None
        if None.offset >= self.total:
            return None
        self.loading = None
        self.updatePlaylistDetailSignal.emit()

    
    def removeTrack(self, playItem):
        row = None
        for index, item in enumerate(self.playList.list):
            if item == playItem:
                row = index
            
            if row is None:
                return None
            model = None.tableView.model()
            modelIndex = model.index(row, 0)
            LPQobuzUtil.deleteRow(self.tableView, modelIndex)
            
            def callback(result = None):
                status = result.data
                if status == 'success':
                    LPGlobalUI.toast.showToast(QCoreApplication.translate('qobuz playlist detail', 'Remove track Ok'), LPGlobalUI.mainWindow)
                    logger.debug(f'''[qobuz playlist detail removeTrack] ret = {status} trackName={playItem.trackName} trackId={playItem.trackId} playlistTrackId={playItem.playlistTrackId}''')
                    self.offset = 0
                    self.total = self.defaultTotal
                    self.playList = None
                    self.scrollBar.setValue(0)
                    self._loadSkeleton()
                    self.loadMore()

            reqFunc = self.qobuz.requestMgr.fetchRemoveFromPlaylistData
            self.qobuz.requestMgr.fetch(reqFunc, callback, str(self.playItem.trackId), str(playItem.playlistTrackId))
            return None

    removeTrack = pyqtSlot(object)(removeTrack)
    __classcell__ = None

