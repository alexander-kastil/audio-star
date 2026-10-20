# Source Generated with Decompyle++
# File: LPQobuzArtistDetailViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/4 10:29
@Auth ： Chris
@File ：LPQobuzArtistDetailViewController.py
@Desc:
'''
from string import Template
from threading import Thread
from PyQt6.QtCore import QEvent, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap, QIcon, QFontMetrics, QTextLayout, QTextOption
import LPGlobalUI
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailListFrameViewController import LPQobuzArtistDetailListFrameViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailTableFrameViewController import LPQobuzArtistDetailTableFrameViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzDetailBaseViewController import LPQobuzDetailBaseViewController, ShuffleCacheType
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailListFrameViewController_ui import Ui_qobuzArtistDetailListViewFrameWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailTableFrameViewController_ui import Ui_qobuzArtistDetailTableViewFrameWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Component.LPQobuzArtistBiographyDialog import LPQobuzArtistBiographyDialog
from HOME.StreamService.Qobuz.Component.UI.LPQobuzArtistBioDialog_ui import Ui_qobuzBiographyDialog
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title, DEFAULT
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem
from LPCommonWidgets.skeleton.LPTableViewSkeleton import LPTableViewSkeletonTableModel, LPTableViewSkeletonDelegate

def _elideBioText(text, font, width, maxLines = (3,)):
    '''把简介文本按给定宽度省略到最多 maxLines 行，超长时最后一行尾部追加省略号。

    :param text: 原始简介纯文本。
    :param font: 标签当前字体。
    :param width: 标签可用宽度。
    :param maxLines: 最大显示行数。
    :return: 可直接设置到 QLabel 的省略后文本。
    '''
    if text or width <= 0:
        return text
    text = None.rstrip()
    metrics = QFontMetrics(font)
    option = QTextOption()
    option.setWrapMode(QTextOption.WrapMode.WordWrap)
    layout = QTextLayout(text, font)
    layout.setTextOption(option)
    lineRanges = []
    truncated = False
    layout.beginLayout()
    line = layout.createLine()
    if line.isValid():
        line.setLineWidth(width)
        start = line.textStart()
        length = line.textLength()
        lineRanges.append((start, length))
        if len(lineRanges) >= maxLines:
            truncated = start + length < len(text)
        else:
            line = layout.createLine()
    layout.endLayout()
    if not lineRanges or truncated:
        return text
    parts = None
    for start, length in enumerate(lineRanges):
        piece = text[start:start + length].rstrip()
        if index == len(lineRanges) - 1:
            piece = metrics.elidedText(piece + '…', Qt.TextElideMode.ElideRight, width)
        parts.append(piece)
    return '\n'.join(parts)


class LPQobuzArtistDetailViewController(LPQobuzDetailBaseViewController):
    updateDeviceInfoSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updateArtistDetailSignal = pyqtSignal()
    loadSectionSignal = pyqtSignal(object)
    updateHeadFrameSignal = pyqtSignal(object)
    loadSkeletonSignal = pyqtSignal()
    
    def __init__(self = None, playItem = None):
        super().__init__()
        self.playItem = playItem
        self.itemId = playItem.trackId
        self.itemType = LPHeaderType.LP_HEADER_TYPE_ARTIST
        self.shuffleCacheType = ShuffleCacheType.ARTIST_SHUFFLE
        self.coverImage = None
        self.updateArtistDetailSignal.connect(self._updateArtistDetail)
        self.loadSkeletonSignal.connect(self._loadSkeleton)
        self.updateCoverImageSignal.connect(self._updateCoverImage)
        self.loadSectionSignal.connect(self._loadSection)
        self.updateHeadFrameSignal.connect(self._updateHeadFrame)
        self.header = None
        self.tableFrames = []
        self.resultDict = None
        self._updatingBioText = False

    
    def _loadSkeleton(self):
        self.loadingOverlay.showOverlay()

    
    def _endSkeleton(self):
        self.loadingOverlay.hideOverlay()

    
    def _updateTableview(self):
        for tableFrame in self.tableFrames:
            tableFrame.tableView.update()

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.presetButton.hide()
        self.titleLabel.setText(self.playItem.trackName)
        self.readButton.hide()
        self.readButton.clicked.connect(self.onReadButtonClicked)
        self.updateCoverImageSignal.emit(None)
        self.playNowButton.setIcon(QIcon(LPGlobalUI.imagePath('minibar/play.png')))
        self.shuffleButton.setIcon(QIcon(self.defaultShufflePixmap))
        self.shuffleButton.clicked.connect(self.shuffleButtonPressed)
        self._initShuffleButtonStatus()
        self.favoriteButton.setIcon(QIcon(self.unFavoritePixmap))
        self.favoriteButton.clicked.connect(self.favoriteButtonPressed)
        self.initFavoriteButtonStatus()
        self.moreButton.hide()
        self.readButton.hide()
        self.decriptionLabel.hide()
        self.decriptionLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.decriptionLabel.installEventFilter(self)
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${titeFontSize}pt;\n                }\n                QLabel#decriptionLabel {\n                    font-size: ${defaultFontSize}pt;\n                    color: rgba(255, 255, 255, 168);\n                }\n                QButton#artistButton {\n                    font-size: ${artistSubTiteFontSize}pt;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#SA_SplitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QLabel#SA_TitleLabel {\n                    font-size: ${subTitleFontSize}pt;                \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${subTitleFontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton#readButton:hover {\n                    color: $buttonHoverColor;\n                }\n                QPushButton#SimilarAlbumsLeftButton, #SimilarAlbumsRightButton, #SimilarAlbumsMoreButton {\n                    background-color: $weeklyQTitleFrameBg;\n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{DEFAULT}''', f'''{MyMusic_Subtitle}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('titeFontSize', 'defaultFontSize', 'artistSubTiteFontSize', 'fontColor', 'subTitleFontSize', 'weeklyQTitleFrameBg', 'buttonHoverColor')))

    
    def _updateCoverImage(self, pixmap):
        self.coverImage = pixmap
        if not self.coverImage:
            self.coverImage = QPixmap(LPGlobalUI.imagePath('artist_l.png'))
        self.coverImage = LPUtility.roundCornerImage(self.coverImage, 480)
        icon = QIcon()
        icon.addPixmap(self.coverImage)
        self.coverImageView.setIcon(icon)
        self.coverImageView.setIconSize(self.coverImageView.size())

    
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

    
    def _updateArtistDetail(self):
        
        def onDataLoadCallback(result = None):
            if result.is_success():
                self.resultDict = result.data
                self.updateHeadFrameSignal.emit(self.resultDict)
                self.loadSectionSignal.emit(self.resultDict)

        reqFunc = self.qobuz.requestMgr.fetchArtistDetailData
        self.qobuz.requestMgr.fetch(reqFunc, onDataLoadCallback, self.playItem.trackId)

    _updateArtistDetail = pyqtSlot()(_updateArtistDetail)
    
    def _loadSection(self, resultDict):
        self._endSkeleton()
        vLayout = self.contentFrame.layout()
        LPQobuzUtil.clearSpecificWidgetsFromLayout(vLayout, (LPQobuzArtistDetailListFrameViewController, LPQobuzArtistDetailTableFrameViewController))
        for section, playList in resultDict.items():
            headType = playList.header.headType
            if playList.list or headType == LPHeaderType.LP_HEADER_TYPE_COLLECTION:
                self.checkPlayListFavorite(playList)
                frameView = LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailTableFrameViewControllerUI, Ui_qobuzArtistDetailTableViewFrameWidget, LPQobuzArtistDetailTableFrameViewController, section, playList, self)
                self.tableFrames.append(frameView)
            else:
                frameView = LPGlobalUI.loadUI(LPUIPath.QobuzArtistDetailListFrameViewControllerUI, Ui_qobuzArtistDetailListViewFrameWidget, LPQobuzArtistDetailListFrameViewController, section, playList)
            vLayout.addWidget(frameView)

    
    def _updateHeadFrame(self, resultDict):
        for section, playList in resultDict.items():
            self.header = playList.header
        continue
        if not self.header:
            return None
        if None.header.describe:
            self.decriptionLabel.setWordWrap(True)
            metrics = QFontMetrics(self.decriptionLabel.font())
            line_height = metrics.lineSpacing()
            self.decriptionLabel.setMaximumHeight(line_height * 3)
            self.decriptionLabel.setVisible(True)
            self.readButton.show()
            QTimer.singleShot(0, self._refreshBioPreview)
        else:
            self.decriptionLabel.hide()
            self.readButton.hide()
        pixmap = LPUtility.getCachedPixmapWithUrl(self.header.imageUrl)
        if not pixmap:
            
            def _fetchCoverImageMethod():
                respDict = LPUtility.fetchUrlQPixmap(self.header.imageUrl)
                _pixmap = respDict.get('image', None)
                if _pixmap:
                    self.updateCoverImageSignal.emit(_pixmap)

            t = Thread(_fetchCoverImageMethod, True, **('target', 'daemon'))
            t.start()
        else:
            self.updateCoverImageSignal.emit(pixmap)

    
    def _refreshBioPreview(self):
        '''按简介标签当前宽度重新生成最多 3 行的省略预览文本。'''
        if not self._updatingBioText and self.header or self.header.describe:
            return None
        if not None.decriptionLabel.isVisible():
            return None
        width = None.decriptionLabel.width()
        if width <= 0:
            return None
        describeText = None.header.describe.replace('<p>', '').replace('</p>', '')
        elidedText = _elideBioText(describeText, self.decriptionLabel.font(), width, 3)
        self._updatingBioText = True
        
        try:
            if self.decriptionLabel.text() != elidedText:
                self.decriptionLabel.setText(elidedText)
        finally:
            self._updatingBioText = False
        self._updatingBioText = False
        return None


    
    def eventFilter(self = None, obj = None, event = None):
        '''拦截简介标签尺寸变化，宽度变化后重新计算省略文本。'''
        if obj is self.decriptionLabel and event.type() == QEvent.Type.Resize:
            self._refreshBioPreview()
        return super().eventFilter(obj, event)

    
    def onReadButtonClicked(self):
        if self.header and self.header.describe:
            bioDialog = LPGlobalUI.loadUI(LPUIPath.QobuzArtistBioDialogUI, Ui_qobuzBiographyDialog, LPQobuzArtistBiographyDialog, self.playItem.trackName, self.header.describe, self)
            bioDialog.show()

    
    def updateUI(self):
        if self.resultDict:
            self.updateHeadFrameSignal.emit(self.resultDict)
            self.loadSectionSignal.emit(self.resultDict)
        elif not self.qobuz.requestMgr.checkArtistCached(self.itemId):
            self.loadSkeletonSignal.emit()
        self.updateArtistDetailSignal.emit()

    
    def _initShuffleButtonStatus(self):
        if not self.qobuz.fileCache.readCache(ShuffleCacheType.ARTIST_SHUFFLE):
            pass
        data = { }
        shuffleIds = data.get(ShuffleCacheType.ARTIST_SHUFFLE.value, [])
        if self.itemId in shuffleIds:
            self.isShuffle = True
        self.updateShuffleButtonSignal.emit(self.shuffleButton)

    __classcell__ = None

