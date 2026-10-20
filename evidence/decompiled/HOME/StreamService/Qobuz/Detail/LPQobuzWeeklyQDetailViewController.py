# Source Generated with Decompyle++
# File: LPQobuzWeeklyQDetailViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/12 18:23
@Auth ： Chris
@File ：LPQobuzWeeklyQDetailViewController.py
@Desc:
'''
from functools import partial
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QTableView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Detail.LPQobuzDetailBaseViewController import LPQobuzDetailBaseViewController, ShuffleCacheType
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzWeeklyQDetailViewController(LPQobuzDetailBaseViewController):
    updateDeviceInfoSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updateWeeklyQDetailSignal = pyqtSignal()
    initHeadFrameSignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        self.itemType = LPHeaderType.LP_HEADER_TYPE_COLLECTION
        self.shuffleCacheType = ShuffleCacheType.WEEKLYQ_SHUFFLE
        self.onFavClickedMethod = self.onFavClicked
        self.onOptClickedMethod = self.onOptClicked
        self.coverImage = None
        self.updateCoverImageSignal.connect(self._updateCoverImage)
        self.updateWeeklyQDetailSignal.connect(self._updateWeeklyQDetail)
        self.initHeadFrameSignal.connect(self._initHeadFrame)

    
    def _initHeadFrame(self):
        self.titleLabel.setText(self.playList.header.headTitle)
        pixmap = LPUtility.getCachedPixmapWithUrl(self.playList.header.imageUrl)
        if not pixmap:
            
            def _fetchCoverImageMethod():
                respDict = LPUtility.fetchUrlQPixmap(self.playList.header.imageUrl)
                _pixmap = respDict.get('image', None)
                if _pixmap:
                    self.updateCoverImageSignal.emit(_pixmap)

            t = Thread(_fetchCoverImageMethod, True, **('target', 'daemon'))
            t.start()
        else:
            self.updateCoverImageSignal.emit(pixmap)
        descriptionList = []
        if self.playList.header.totalTracks:
            descriptionList.append(str(self.playList.header.totalTracks) + ' Tracks')
        if self.playList.header.duration:
            duration = LPQobuzUtil.formatAlbumDuration(self.playList.header.duration)
            descriptionList.append(duration)
        descriptionText = ' · '.join(descriptionList)
        self.descriptionLabel.setText(descriptionText)
        self.playNowButton.setIcon(QIcon(LPGlobalUI.imagePath('minibar/play.png')))
        slotFunc = partial(self.playNowButtonPressed, self.tableView)
        self.playNowButton.clicked.connect(slotFunc)
        self.shuffleButton.setIcon(QIcon(self.defaultShufflePixmap))
        self.shuffleButton.clicked.connect(self.shuffleButtonPressed)
        self._initShuffleButtonStatus()
        self.presetButton.setIcon(QIcon(LPGlobalUI.imagePath('track_more_preset.png')))
        self.presetButton.clicked.connect(self.presetButtonPressed)
        self.presetButton.source = self.source
        self.moreButton.hide()

    
    def setupUi(self = None, ui = None):
