# Source Generated with Decompyle++
# File: LPQobuzWeeklyQFrameSection.pyc (Python 3.9)

'''
@Time ： 2025/7/11 16:13
@Auth ： Chris
@File ：LPQobuzWeeklyQFrameSection.py
@Desc:
'''
from string import Template
from threading import Thread
from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
import LPGlobalUI
from HOME.StreamService.Qobuz.Detail.LPQobuzWeeklyQDetailViewController import LPQobuzWeeklyQDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzWeeklyQDetailViewController_ui import Ui_qobuzWeeklyQDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title, DEFAULT
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayHeader, LPQobuzPlayList, LPQobuzPlayItem
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPListViewSkeleton import LPListViewSkeletonListModel, LPListViewSkeletonDelegateWithSize

class LPQobuzWeeklyQFrameSection(LPQobuzBaseViewController):
    updateRecommendUISignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object, object)
    
    def __init__(self = None, section = None, playList = None):
        super().__init__()
        self.section = section
        self.playList = playList
        self.itemType = LPHeaderType.LP_HEADER_TYPE_COLLECTION
        self.updateRecommendUISignal.connect(self._updateRecommendUI)
        self.updateCoverImageSignal.connect(self._updateCoverImage)
        self.forePixmap = None

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.sectionTitleLabel.setText(self.section)
        self.RecommendContentFrame.mousePressEvent = self.weeklyQClick
        self.weeklyQPlayButton.clicked.connect(self._playWeeklyQ)
        stylesheetTemplate = Template('\n                QLabel#sectionTitleLabel {\n                    font-size: ${sectionTitleFontSize}pt;\n                }\n                QLabel#weeklyQDescriptionLabel {\n                    color: $descriptionFontColor;\n                }\n                QLabel#baselineLabel {\n                    font-size: ${baselineFontSize}pt;\n                    color: $baseLineFontColor;\n                }\n                QFrame {\n                    color: $fontColor;\n                }\n\n                QFrame#splitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${sectionTitleFontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton#leftButton, #rightButton, #moreButton {\n                    background-color: $buttonBg;\n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_HIGH_HIGH_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name(), f'''{Qobuz_Sub_Title}''', f'''{DEFAULT}''', LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), **('fontColor', 'baseLineFontColor', 'descriptionFontColor', 'sectionTitleFontSize', 'baselineFontSize', 'buttonBg')))

    
    def showSkeleton(self):
        model = LPListViewSkeletonListModel(6, self.listView)
        self.listView.setModel(model)
        delegate = LPListViewSkeletonDelegateWithSize(self.listView, 190, 265)
        self.listView.setItemDelegate(delegate)

    
    def showContent(self, section, playlist):
        self.playList = playlist
        self.playList.header.searchUrl = 'https://www.qobuz.com/api.json/0.2/dynamic-tracks/get?type=weekly'
        self.updateRecommendUISignal.emit()

    
    def _updateRecommendUI(self):
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/play.png'), LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        LPButtonEventFilter(self.weeklyQPlayButton, QIcon(LPGlobalUI.imagePath('miniBar/play.png')), QIcon(tintImage), QIcon(tintImage), 'image')
        baseline = self.playList.header.weeklyQBaseline
        title = self.playList.header.headTitle
        description = self.playList.header.descText
        if baseline:
            self.baselineLabel.setText(baseline)
        if title:
            self.weeklyQNameLabel.setText(title)
        if description:
            self.weeklyQDescriptionLabel.setText(description)
        self.updateGraphics()

    _updateRecommendUI = pyqtSlot()(_updateRecommendUI)
    
    def updateGraphics(self):
        graphics = self.playList.header.graphics
        for key, url in graphics.items():
            pixmap = LPUtility.getCachedPixmapWithUrl(url)
            if not pixmap:
                
                def _fetchCoverImageMethod(key = None, url = None):
                    respDict = LPUtility.fetchUrlQPixmap(url)
                    _pixmap = respDict.get('image', None)
                    if _pixmap:
                        self.updateCoverImageSignal.emit(key, _pixmap)

                t = Thread(_fetchCoverImageMethod, (key, url), True, **('target', 'args', 'daemon'))
                t.start()
                continue
            self.updateCoverImageSignal.emit(key, pixmap)

    
    def _updateCoverImage(self, key, pixmap):
        if key == 'background':
            self.backLabel.setGeometry(self.weeklyQImageFrame.rect())
            self.backLabel.setPixmap(pixmap)
            self.backLabel.setScaledContents(True)
        elif key == 'foreground':
            self.forePixmap = pixmap
            scaledPixmap = self.foregroundScaled()
            self.foreLabel.setStyleSheet('background: transparent;')
            if scaledPixmap:
                self.foreLabel.setPixmap(scaledPixmap)
                self.foreLabel.resize(scaledPixmap.size())
            self.foregroundAlignmentCenter()

    
    def weeklyQClick(self, event):
        LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzWeeklyQDetailViewControllerUI, Ui_qobuzWeeklyQDetailViewWidget, LPQobuzWeeklyQDetailViewController), 'qobuzdetail')

    
    def _playWeeklyQ(self):
        if self.playList:
            device = LPGlobalUI.currentDevice
            if not device:
                logger.error('error, no device found')
                return None
            playItem = None.playList.list[0]
            xml = self.playList.generateXML(str(1))
            self.playQobuzPlayList(self.playList, playItem, xml, 0, 'qobuz weekly track', **('playIndex', 'logPrefix'))

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        self.backLabel.setGeometry(self.weeklyQImageFrame.rect())
        pixmap = self.foregroundScaled()
        if pixmap:
            self.foreLabel.resize(pixmap.size())
            self.foreLabel.setPixmap(pixmap)
        self.foregroundAlignmentCenter()

    
    def foregroundAlignmentCenter(self):
        parentW = self.weeklyQImageFrame.width()
        parentH = self.weeklyQImageFrame.height()
        w = self.foreLabel.width()
        h = self.foreLabel.height()
        self.foreLabel.move((parentW - w) // 2, (parentH - h) // 2)

    
    def foregroundScaled(self):
        if self.forePixmap:
            scale = self.weeklyQImageFrame.width() / self.weeklyQImageFrame.height()
            if scale < 2:
                target_width = self.weeklyQImageFrame.width() - 20
                scaledPixmap = self.forePixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
            else:
                target_height = self.weeklyQImageFrame.height() - 20
                scaledPixmap = self.forePixmap.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
            return scaledPixmap

    __classcell__ = None

