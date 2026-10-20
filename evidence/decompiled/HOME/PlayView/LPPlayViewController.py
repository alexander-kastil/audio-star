# Source Generated with Decompyle++
# File: LPPlayViewController.pyc (Python 3.9)

'''
@Time ： 2025/9/22 14:35
@Auth ： Chris
@File ：LPPlayViewController.py
@Desc:
'''
import enum
import platform
from string import Template
from threading import Thread
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QCoreApplication, QTimer, QPropertyAnimation, QEvent, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter, QBrush, QImage, QFontMetrics
from PyQt6.QtWidgets import QWidget, QButtonGroup, QApplication
import LPGlobalUI
from HOME.Minibar.LPMiniBarViewController import LPMiniBarViewController
from HOME.Minibar.LPVolumeSliderViewController import LPVolumeSliderViewController
from HOME.Minibar.UI.LPMinibar_ui import Ui_minibarWidget
from HOME.PlayView import LPPlayViewUtil
from HOME.PlayView.LPPlayViewBackWidget import LPPlayViewBackWidget
from HOME.PlayView.LPPlayViewFullScreenContentController import LPPlayViewFullScreenContentController
from HOME.LPPlaybackLayoutPolicy import useCompactPlayViewLayout
from HOME.PlayView.LPPlayViewNormalContentController import LPPlayViewNormalContentController
from HOME.PlayView.UI.LPPlayViewFullScreenContent_ui import Ui_playviewFullScreenWidget
from HOME.PlayView.UI.LPPlayViewNormalContent_ui import Ui_playviewNormalWidget
from HOME.Queue.LPQueueDialog import LPQueueDialog
from LPClientFramework import LPStreamServiceManager, LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import PlayView_Track_Title, PlayView_Source_Title, PlayView_Format_Title, PlayView_Album_Title, MiniBar_Subtitle
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPTrackMoreMenu import LPTrackMoreMenu

class LPPlayViewStatus(enum.Enum):
    Normal = 0
    FullScreen = 1
    Immersive = 2

SOURCE_INFO_DEFAULT_WIDTH = 340
SOURCE_INFO_ROW_RESERVED_GAP = 48
SOURCE_LABEL_TEXT_PADDING = 8
MOUSE_ACTIVITY_COALESCE_INTERVAL = 150

class LPPlayViewController(QWidget):
    '''负责播放页布局、全屏交互和沉浸状态切换。'''
    updateUISignal = pyqtSignal(object)
    backgroundFinishSignal = pyqtSignal()
    updateCoverImageSignal = pyqtSignal(object)
    updateFormatSignal = pyqtSignal(object)
    updateTitleSignal = pyqtSignal(object)
    updatePlayStateSignal = pyqtSignal(object)
    updateFullScreenSectionSignal = pyqtSignal(object)
    updateBGSignal = pyqtSignal(object)
    fullscreenChangedSignal = pyqtSignal()
    
    def __init__(self = None, closeButtonMethod = None, parent = None):
        '''初始化播放页控制器。

        参数:
            closeButtonMethod: 关闭播放页时调用的方法。
            parent: 可选的父级控件。
        返回值:
            None。
        '''
        super().__init__(parent)
        self.artworkPixmap = None
        self.formatStr = ''
        self.closeButtonMethod = closeButtonMethod
        self.minibar = None
        self.originalBackgroundColor = QColor(18, 18, 18, 255)
        self.bgPixmap = None
        self.updateUISignal.connect(self._updateQT)
        self.backgroundFinishSignal.connect(self._doUpdate)
        self.updateBGSignal.connect(self._updateBackgound)
        self.fullscreenChangedSignal.connect(self.onFullScreenChanged)
        self.firstTimeEnterQueue = True
        self.isCompactPlayViewLayout = False
        self.isImmersive = False
        self.lastCursorPos = None
        self.immersiveTimer = QTimer(self)
        self.immersiveTimer.setInterval(5000)
        self.immersiveTimer.setSingleShot(True)
        self.immersiveTimer.timeout.connect(self.onImmersive)
        self.mouseActivityTimer = QTimer(self)
        self.mouseActivityTimer.setInterval(MOUSE_ACTIVITY_COALESCE_INTERVAL)
        self.mouseActivityTimer.setSingleShot(True)
        self.mouseActivityTimer.timeout.connect(self._restartImmersiveTimer)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    
    def onImmersive(self):
        logger.debug('[play view] onImmersive')
        status = self.status
        if status not in (LPPlayViewStatus.FullScreen, LPPlayViewStatus.Immersive):
            return None
        self.isImmersive = None
        self.hideBars()
        self.hideTabButton()
        self.hideFullScreenButton()
        self.showWiimLogo()
        self.closeTopWidgets()

    
    def hideTabButton(self):
        self.fullscreenTabFrame.hide()

    
    def hideFullScreenButton(self):
        self.moreButton.hide()
        self.fullscreenButton.hide()

    
    def hideWiimLogo(self):
        self.wiimIconButton.hide()

    
    def showFullScreenButton(self):
        self.fullscreenButton.show()

    
    def showTabButton(self):
        if useCompactPlayViewLayout(LPGlobalUI.currentDevice):
            self.fullscreenTabFrame.hide()
            return None
        None.fullscreenTabFrame.show()

    
    def showWiimLogo(self):
        self.wiimIconButton.show()

    
    def handleMouseMove(self, event):
        '''处理全屏播放页的用户活动并退出沉浸态。

        参数:
            event: 应用级事件过滤器转发的鼠标、悬停或滚轮事件。
        返回值:
            None。
        '''
        status = self.status
        if status not in (LPPlayViewStatus.FullScreen, LPPlayViewStatus.Immersive):
            return None
        if None.immersiveTimer.isActive():
            self.immersiveTimer.stop()
        self.mouseActivityTimer.start()
        if not self.isImmersive:
            return None
        None.debug('[play view] leave immersive after user interaction')
        self.isImmersive = False
        self.showBars()
        self.showTabButton()
        self.showFullScreenButton()
        self.hideWiimLogo()

    
    def _restartImmersiveTimer(self):
        '''在合并的一批用户活动结束后启动沉浸倒计时。'''
        if self.status not in (LPPlayViewStatus.FullScreen, LPPlayViewStatus.Immersive):
            return None
        None.immersiveTimer.start()

    
    def showBars(self):
        '''显示底部控制栏并终止冲突的隐藏动画。'''
        for bar in (self.minibar.miniBarFrame,):
            animation = getattr(bar, '_anim', None)
            if animation is not None:
                animation.stop()
            if not bar.isVisible():
                bar.show()
                anim = QPropertyAnimation(bar, b'windowOpacity')
                anim.setDuration(300)
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.start()
                bar._anim = anim
                continue
            bar.setWindowOpacity(1)

    
    def hideBars(self):
