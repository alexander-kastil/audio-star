# Source Generated with Decompyle++
# File: LPPlayViewNormalContentController.pyc (Python 3.9)

'''
@Time ： 2025/9/23 16:22
@Auth ： Chris
@File ：LPPlayViewNormalContentController.py
@Desc:
'''
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication, QTimer, QVariantAnimation, QEasingCurve, QSize, QPoint
from PyQt6.QtGui import QPixmap, QIcon, QMovie, QFont, QFontMetricsF
from PyQt6.QtWidgets import QWidget, QButtonGroup, QLabel, QFrame, QHBoxLayout, QSizePolicy
import LPGlobalUI
from HOME.PlayView import LPPlayViewUtil
from HOME.LPPlaybackLayoutPolicy import useCompactPlayViewLayout
from HOME.PlayView.LPPlayViewQueueSectionController import LPPlayViewQueueSectionController
from HOME.PlayView.LPPlayViewTrackLabel import LPPlayViewTrackLabel
from HOME.PlayView.UI.LPPlayViewQueueSection_ui import Ui_playviewQueueSection
from HOME.Queue.LPQueueViewController import LPQueueViewController
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Big_Title, Main_Text, Sub_Title
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPUtility import logger
ALBUM_TITLE_BOTTOM_GAP = 16
COMPACT_COVER_MIN_SIDE = 240
COMPACT_COVER_HEIGHT_RATIO = 0.62
COMPACT_COVER_HORIZONTAL_RESERVED = 160
COMPACT_COVER_VERTICAL_MARGIN = 24
COMPACT_COVER_PLAYING_SCALE = 1.15
_LABEL_FONT_BASE_HEIGHT = 814
_LABEL_FONT_MIN_SCALE = 0.7
TRACK_TITLE_ROW_WIDTH_RATIO = 0.8

class LPPlayViewNormalContentController(QWidget):
    updateUISignal = pyqtSignal(object)
    updateCoverImageSignal = pyqtSignal(object)
    updateBGSignal = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.playView = parent
        self.playingMovie = QMovie(LPGlobalUI.imagePath('write_playing.gif'))
        self.pausePixmap = QPixmap(LPGlobalUI.imagePath('write_pause.png'))
        self.updateUISignal.connect(self._updateContent)
        self.playView.updateCoverImageSignal.connect(self._updateQTCoverImage)
        self.playView.updateFormatSignal.connect(self._updateFormat)
        self.playView.updateTitleSignal.connect(self._updateQTTitle)
        self.playView.updatePlayStateSignal.connect(self._updatePlayState)
        self.queueListView = None
        self.currentPage = None
        self.isCompactLayout = False
        self.coverBaseSide = 0
        self.coverCurrentSide = 0
        self.currentCoverPixmap = None
        self.coverScaleAnimation = None
        self.compactLayoutAdjustPending = False

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self._initCompactInfoWidgets()
        self._initCoverImage()
        self._updateFormat(self.playView.formatStr)
        self._updateQTTitle(LPGlobalUI.currentDevice)
        self.formatLabel.setObjectName('normalFormatLabel')
        stylesheetTemplate = Template('\n\n                        QLabel#normalFormatLabel {\n                            color: rgba(255, 255, 255, 0.65);\n                        }\n                        QFrame#tabFrame {\n                            background-color: rgba(255, 255, 255, 21);\n                            border-radius: 8px;\n                            \n                        }\n                        QPushButton#queueButton, #lyricsButton{\n                            background-color: transparent;\n                            color: rgba(255, 255, 255, 166)                         \n                        }\n                        QPushButton#queueButton:checked, #lyricsButton:checked{\n                            background-color: white; \n                            color: black;\n                            border-radius: 8px;                         \n                        }\n                ')
        self.setStyleSheet(stylesheetTemplate.substitute())
        self.pages = {
            'queue': LPGlobalUI.loadUI(LPUIPath.PlayViewQueueSectionUI, Ui_playviewQueueSection, LPPlayViewQueueSectionController, self) }
        for page in self.pages.values():
            self.stackedWidget.addWidget(page)
        self.updateLayoutMode(LPGlobalUI.currentDevice)
        self._scaleLabelFonts()

    
    def onGroupClicked(self, button):
        button.update()

    
    def onEnter(self):
        logger.debug('[playview normal] ===onEnter===')
        self.updateLayoutMode(LPGlobalUI.currentDevice)
        if self.isCompactLayout:
            return None
        if None.currentPage:
            self.switchTo(self.currentPage)
        else:
            self.switchTo('queue')

    
    def onLeave(self):
        logger.debug('[playview normal] ===onLeave===')

    
    def _start(self):
        if self.currentPage:
            self.switchTo(self.currentPage)
        else:
            self.switchTo('queue')

    
    def switchTo(self = None, pageName = None):
        logger.debug(f'''[play view normal switchTo] == {pageName}''')
        page = self.pages[pageName]
        self.currentPage = pageName
        LPPlayViewUtil.setCurrentWidget(self.stackedWidget, page)

    
    def _initQueuePage(self):
        self.queueListView = LPQueueViewController()
        frameHLayout = self.queueFrame.layout()
        frameHLayout.addWidget(self.queueListView)

    
    def _updateContent(self, device):
        if device is None:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
        self.updateLayoutMode(device)

    
    def _initCompactInfoWidgets(self):
        '''
        动态插入 radio 居中布局专用码率与标题区，避免修改生成的 *_ui.py 文件。

        :return: None。
        '''
        self.compactFormatLabel = QLabel(self.leftFrame)
        self.compactFormatLabel.setObjectName('compactFormatLabel')
        self.compactFormatLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compactFormatLabel.setStyleSheet('color: rgba(255, 255, 255, 0.65);')
        self.compactTitleRow = QFrame(self.leftFrame)
        self.compactTitleRow.setObjectName('compactTitleRow')
        titleLayout = QHBoxLayout(self.compactTitleRow)
        titleLayout.setContentsMargins(0, 0, 0, 0)
        titleLayout.setSpacing(8)
        self.compactTitleLabel = LPPlayViewTrackLabel(self.compactTitleRow)
        self.compactTitleLabel.setObjectName('compactTitleLabel')
        self.compactTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compactTitleLabel.setStyleSheet('color: rgba(255, 255, 255);')
        self.compactPlayingLabel = QLabel(self.compactTitleRow)
        self.compactPlayingLabel.setObjectName('compactPlayingLabel')
        self.compactPlayingLabel.setFixedSize(12, 12)
        self.compactPlayingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLayout.addStretch(1)
        titleLayout.addWidget(self.compactPlayingLabel)
        titleLayout.addWidget(self.compactTitleLabel)
        titleLayout.addStretch(1)
        self.compactSubtitleLabel = QLabel(self.leftFrame)
        self.compactSubtitleLabel.setObjectName('compactSubtitleLabel')
        self.compactSubtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compactSubtitleLabel.setStyleSheet('color: rgba(255, 255, 255, 0.65);')
        layout = self.leftFrame.layout()
        layout.insertSpacing(2, 28)
        layout.insertWidget(3, self.compactFormatLabel)
        layout.insertSpacing(4, 6)
        layout.insertWidget(5, self.compactTitleRow, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.insertSpacing(6, 4)
        layout.insertWidget(7, self.compactSubtitleLabel)
        self.compactFormatLabel.hide()
        self.compactTitleRow.hide()
        self.compactSubtitleLabel.hide()
        self.albumTitleLabel = QLabel(self.leftFrame)
        self.albumTitleLabel.setObjectName('albumTitleLabel')
        self.albumTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.albumTitleLabel.setStyleSheet('color: rgba(255, 255, 255, 0.65);')
        self.leftFrame.layout().insertWidget(1, self.albumTitleLabel)
        self.leftFrame.layout().insertSpacing(2, ALBUM_TITLE_BOTTOM_GAP)
        self.albumTitleGapItem = self.leftFrame.layout().itemAt(2)
        self.albumTitleLabel.hide()
        self._updateAlbumTitleGap(False)
        self._updateCompactTitleRowWidth()

    
    def updateLayoutMode(self, device):
        '''
        根据当前音源类型切换布局；该方法需要支持 radio 与非 radio 的双向切换。
        '''
        compact = useCompactPlayViewLayout(device)
        if compact == self.isCompactLayout:
            if compact:
                if self.coverBaseSide <= 0:
                    self.adjustCompactCover()
                elif not self.coverCurrentSide:
                    pass
                self.coverCurrentSide(self._targetCoverSide(device))
                return None
            None.adjustCover()
            return None
        self.isCompactLayout = None
        self.middleSpacer.setVisible(not compact)
        self.rightFrame.setVisible(not compact)
        self.frame_4.setVisible(not compact)
        self._syncFormatLabelVisibility(self.playView.formatStr)
        self.compactTitleRow.setVisible(compact)
        self.compactSubtitleLabel.setVisible(compact)
        if compact:
            pass
        self.albumTitleLabel.setVisible(bool(self.albumTitleLabel.text()))
        self.coverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._updateCompactTitleRowWidth()
        layout = self.normalFrame.layout()
        if compact:
            layout.setStretch(0, 1)
            layout.setStretch(1, 0)
            layout.setStretch(2, 0)
            layout.setStretch(3, 0)
            layout.setStretch(4, 1)
            self.leftFrame.setMinimumWidth(280)
            self.leftFrame.setMaximumWidth(16777215)
        else:
            self._resetCompactCoverState()
            self._updateCompactCoverSpacing(30)
            layout.setStretch(0, 1)
            layout.setStretch(1, 3)
            layout.setStretch(2, 1)
            layout.setStretch(3, 6)
            layout.setStretch(4, 1)
            self.leftFrame.setMinimumWidth(280)
            self.leftFrame.setMaximumWidth(16777215)
        self._updateQTTitle(device)
        if compact:
            self._scaleLabelFonts()
            self.adjustCover()
            self._scheduleCompactLayoutAdjustment()
        else:
            QTimer.singleShot(0, self._adjustNormalCoverAfterLayout)

    
    def _resetCompactCoverState(self):
        '''
        退出居中封面布局时清理动画和缓存尺寸，避免普通布局沿用 radio 封面边长。
        '''
        if self.coverScaleAnimation:
            self.coverScaleAnimation.stop()
            self.coverScaleAnimation = None
        self.coverBaseSide = 0
        self.coverCurrentSide = 0

    
    def _adjustNormalCoverAfterLayout(self):
        '''
        等待 Qt 完成布局重排后再计算普通封面尺寸，并重新进入 queue 页面刷新队列。
        '''
        if self.isCompactLayout:
            return None
        None.adjustCover()
        self._scaleLabelFonts()
        if not self.currentPage:
            pass
        self.switchTo('queue')

    
    def _updateQTTitle(self, device):
        if not hasattr(self, 'compactTitleLabel'):
            return None
        if None:
            pass
        elif not None:
            pass
        album = ''.strip()
        if hasattr(self, 'albumTitleLabel'):
            previousVisible = not self.albumTitleLabel.isHidden()
            previousHeight = self.albumTitleLabel.sizeHint().height() if previousVisible else 0
            self.albumTitleLabel.setText(album)
            if self.isCompactLayout:
                pass
            albumVisible = bool(album)
            self.albumTitleLabel.setVisible(albumVisible)
            gapChanged = self._updateAlbumTitleGap(albumVisible)
            currentHeight = self.albumTitleLabel.sizeHint().height() if albumVisible else 0
            if not previousVisible != albumVisible and previousHeight != currentHeight:
                pass
            geometryChanged = gapChanged
            if self.isCompactLayout and geometryChanged:
                self._scheduleCompactLayoutAdjustment()
        if device is None:
            self.compactTitleLabel.setText('')
            self.compactSubtitleLabel.setText('')
            return None
        if not None.mediaInfo.trackName:
            pass
        trackName = ''.strip()
        if not device.mediaInfo.artist:
            pass
        artist = ''.strip()
        if not getattr(device.mediaInfo, 'itemName', None):
            pass
        itemName = ''.strip()
        if not trackName:
            pass
        title = itemName
        subtitleParts = []
        if artist:
            subtitleParts.append(artist)
        self.compactTitleLabel.setText(title)
        self.compactSubtitleLabel.setText(' · '.join(subtitleParts))

    
    def _updateAlbumTitleGap(self, visible):
        '''
        根据 album 标题显隐同步其下方间距，隐藏时不保留空白高度。

        :param visible: album 标题当前是否显示。
        :return: 间距高度发生变化时返回 True，否则返回 False。
        '''
        gapItem = getattr(self, 'albumTitleGapItem', None)
        if gapItem is None or gapItem.spacerItem() is None:
            return False
        targetHeight = ALBUM_TITLE_BOTTOM_GAP if None else 0
        spacerItem = gapItem.spacerItem()
        if spacerItem.sizeHint().height() == targetHeight:
            return False
        None.changeSize(0, targetHeight, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.leftFrame.layout().invalidate()
        return True

    
    def _updatePlayState(self, device):
        if not self.isCompactLayout:
            return None
        None._updateCompactPlayingIndicator(device)
        self._animateCompactCover(self._targetCoverSide(device))

    
    def _updateCompactPlayingIndicator(self, device):
        '''同步非全屏 compact 布局的播放图标并保持曲目名为白色。

        :param device: 当前播放设备；为空时显示暂停图标。
        :return: None。
        '''
        self.compactTitleLabel.setStyleSheet('color: white;')
        if device and device.mediaInfo.playState == 'PLAYING':
            if self.playingMovie.state() != QMovie.MovieState.Running:
                self.compactPlayingLabel.setMovie(self.playingMovie)
                self.playingMovie.start()
            return None
        if None.playingMovie.state() == QMovie.MovieState.Running:
            self.playingMovie.stop()
        scaled = self.pausePixmap.scaled(self.compactPlayingLabel.width(), self.compactPlayingLabel.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.compactPlayingLabel.setPixmap(scaled)

    
    def _updateFormat(self, formatStr):
        '''
        同步普通布局和居中封面布局里的码率文本。

        :param formatStr: 播放格式字符串，例如 kbps、bits、kHz 组合；为空时隐藏。
        :return: None。
        '''
        self._syncFormatLabelVisibility(formatStr)

    
    def _syncFormatLabelVisibility(self, formatStr):
        '''
        根据当前布局模式显示对应的码率标签，避免 compact 布局复用被隐藏的 frame_4。

        :param formatStr: 播放格式字符串；为空时两个标签都隐藏。
        :return: None。
        '''
        if not formatStr:
            self.formatLabel.hide()
            self.compactFormatLabel.hide()
        else:
            self.formatLabel.setText(formatStr)
            self.compactFormatLabel.setText(formatStr)
            self.formatLabel.setVisible(not (self.isCompactLayout))
            self.compactFormatLabel.setVisible(self.isCompactLayout)

    
    def _labelFontScale(self):
        '''
        根据 normalFrame 当前高度计算字号缩放因子，与封面缩放同源。

        :return: 缩放比例，钳制在 [_LABEL_FONT_MIN_SCALE, 1.0] 区间；几何无效时返回 1.0。
        '''
        height = self.normalFrame.height()
        if height <= 0:
            return 1
        ratio = None / _LABEL_FONT_BASE_HEIGHT
        return max(_LABEL_FONT_MIN_SCALE, min(1, ratio))

    
    def _scaleLabelFonts(self):
        '''
        重算左侧信息区字号；音质字号固定对齐 Queue 曲目标题，其余字号随窗口缩放。

        字号与字重统一用 QFont 控制，避免被 stylesheet 里的 font-* 属性覆盖
        （Qt 一旦 stylesheet 含 font-* 就接管字体，QFont 设置会失效，因此
        stylesheet 只保留 color）。

        :return: None。
        '''
        scale = self._labelFontScale()
        
        def applyFont(label = None, basePt = None, weight = None, scalable = None):
            font = label.font()
            font.setPointSizeF(basePt * scale if scalable else basePt)
            font.setWeight(weight)
            label.setFont(font)

        applyFont(self.formatLabel, Main_Text, False, **('scalable',))
        applyFont(self.compactFormatLabel, Main_Text, False, **('scalable',))
        applyFont(self.albumTitleLabel, Sub_Title, QFont.Weight.Medium, **('weight',))
        applyFont(self.compactTitleLabel, Big_Title, QFont.Weight.Bold, **('weight',))
        applyFont(self.compactSubtitleLabel, Sub_Title)
        self._updateCompactPlayingIconSize()

    
    def _updateCompactPlayingIconSize(self):
        '''
        根据曲目标题字体的 capHeight 自动计算播放指示器尺寸，跨平台自适应。

        :return: None。
        '''
        if not hasattr(self, 'compactPlayingLabel'):
            return None
        font = None.compactTitleLabel.font()
        metrics = QFontMetricsF(font)
        iconSize = max(12, int(metrics.capHeight()))
        self.compactPlayingLabel.setFixedSize(iconSize, iconSize)
        self.playingMovie.setScaledSize(QSize(iconSize, iconSize))

    
    def _updateCoverImageAsync(self, device, _async = (None,)):
        if device is None:
            pixmap = None
            self.updateCoverImageSignal.emit(pixmap)
            return None
        if None.artworkPixmap == device.mediaInfo.artworkImage and device.mediaInfo.mediaType != 'AIRPLAY':
            return None
        self.artworkPixmap = None.mediaInfo.artworkImage
        pixmap = self.artworkPixmap
        self.updateCoverImageSignal.emit(pixmap)

    
    def _updateQTCoverImage(self, pixmap):
        self.currentCoverPixmap = pixmap
        if self.isCompactLayout:
            if not self.coverCurrentSide:
                pass
            self._setCoverPixmap(self._targetCoverSide(LPGlobalUI.currentDevice))
            return None
        pixmap = None._ensureCoverPixmap(pixmap)
        canvasSide = min(self.coverLabel.width(), self.coverLabel.height())
        self.coverLabel.setPixmap(LPPlayViewUtil.centerCoverPixmap(pixmap, canvasSide))
        self.updateBGSignal.emit(pixmap)

    
    def _initCoverImage(self):
        pixmap = self.playView.artworkPixmap
        self._updateQTCoverImage(pixmap)

    
    def _ensureCoverPixmap(self, pixmap):
        '''按当前播放输入类型把无效封面统一替换为 PlayView 默认封面。

        :param pixmap: 待显示的原始封面对象。
        :return: 可直接显示的 QPixmap。
        '''
        device = LPGlobalUI.currentDevice
        trackSource = device.mediaInfo.trackSource if device else None
        mediaType = device.mediaInfo.mediaType if device else None
        return LPGlobalUI.ensureCoverPixmap(pixmap, trackSource, 'playview', mediaType)

    
    def _trackTitleRowWidth(self):
        '''根据顶层 App 窗口宽度计算曲目标题行宽度。

        :return: App 窗口宽度的 80%，窗口尚未完成布局时回退到当前页面宽度。
        '''
        windowWidth = self.window().width()
        if windowWidth <= 0:
            windowWidth = self.width()
        return max(0, int(windowWidth * TRACK_TITLE_ROW_WIDTH_RATIO))

    
    def _updateCompactTitleRowWidth(self):
        '''同步紧凑布局曲目标题行的响应式固定宽度。

        :return: None。
        '''
        if not hasattr(self, 'compactTitleRow'):
            return None
        None.compactTitleRow.setFixedWidth(self._trackTitleRowWidth())

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        self._updateCompactTitleRowWidth()
        self._scaleLabelFonts()
        self.adjustCover()
        self._scheduleCompactLayoutAdjustment()

    
    def showEvent(self = None, event = None):
        super().showEvent(event)
        self._updateCompactTitleRowWidth()
        self._scaleLabelFonts()
        self.adjustCover()
        self._scheduleCompactLayoutAdjustment()

    
    def adjustCover(self):
        if self.isCompactLayout:
            self.adjustCompactCover()
            return None
        fw = None.leftFrame.width()
        fh = self.leftFrame.height()
        side = min(fw, fh)
        side = int(side)
        pixmap = self._ensureCoverPixmap(self.playView.artworkPixmap)
        self.coverLabel.setFixedSize(side, side)
        self.coverLabel.setPixmap(LPPlayViewUtil.centerCoverPixmap(pixmap, side))

    
    def adjustCompactCover(self):
        '''
        按可见文字和固定间距的实际占用，为 compact 播放态封面分配剩余空间。

        :return: None。
        '''
        fw = self.normalFrame.width()
        fh = self.normalFrame.height()
        if fw <= 0 or fh <= 0:
            return None
        if None.coverScaleAnimation:
            self.coverScaleAnimation.stop()
            self.coverScaleAnimation = None
        (reservedHeight, preCoverHeight) = self._compactLayoutHeightBudget()
        heightBudget = max(1, fh - reservedHeight)
        verticalMarginBudget = min(COMPACT_COVER_VERTICAL_MARGIN * 2, max(0, heightBudget - COMPACT_COVER_MIN_SIDE))
        heightCapacity = max(1, heightBudget - verticalMarginBudget)
        widthCapacity = max(1, fw - COMPACT_COVER_HORIZONTAL_RESERVED)
        preferredSide = max(1, int(fh * COMPACT_COVER_HEIGHT_RATIO))
        self.coverBaseSide = int(min(preferredSide, widthCapacity, heightCapacity))
        self.leftFrame.setFixedWidth(max(280, min(fw, self.coverBaseSide + COMPACT_COVER_HORIZONTAL_RESERVED), self.compactTitleRow.width()))
        desiredTop = self._compactCoverTopOffset(fh, self.coverBaseSide, preCoverHeight)
        availableTop = max(0, fh - reservedHeight - self.coverBaseSide)
        self._updateCompactCoverSpacing(min(desiredTop, availableTop))
        self._setCoverPixmap(self._targetCoverSide(LPGlobalUI.currentDevice))

    
    def _compactLayoutHeightBudget(self):
