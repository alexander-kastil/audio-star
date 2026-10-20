# Source Generated with Decompyle++
# File: LPMiniBarViewController.pyc (Python 3.9)

'''
@Time ： 2025/9/23 13:33
@Auth ： Chris
@File ：LPMiniBarViewController.py
@Desc:
'''
import datetime
import math
import time
from email.policy import default
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QObject, QCoreApplication
from PyQt6.QtGui import QIcon, QPixmap, QCursor, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QMainWindow
import LPGlobalUI
from HOME.Minibar.LPMinibarMarqueeLabel import LPMinibarMarqueeLabel
from HOME.Minibar.LPMinibarQueueButton import LPMinibarQueueButton
from HOME.Minibar.LPVolumeSliderViewController import LPVolumeSliderViewController
from HOME.Minibar.UI.LPMinibarVolumeSlider_ui import Ui_volumeSliderWidget
from HOME.DeviceDashboard.LPDeviceItemWrapper import LPDeviceItemWrapper
from HOME.DeviceDashboard.LPEditGroupDialogViewController import LPEditGroupDialogViewController
from HOME.Queue.LPQueueDialog import LPQueueDialog
from HOME.Queue.UI.LPQueueDialog_ui import Ui_queueDialog
from LPClientFramework import LPUtility, LPStreamServiceManager
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MiniBar_Subtitle, DEFAULT, Min_Text, Sub_Text, Main_Text
from LPClientFramework.LPDeviceManager.LPGroup import LPGroupObject, LPGroupType_Temp
from LPClientFramework.LPDeviceManager.LPGroupManager import LPGroupManager
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPBadgeButtonEventFilter import LPBadgeButtonEventFilter
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonCusorEventFilter import LPButtonCursorEventFilter
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPCheckableButtonEventFilter import LPCheckableButtonEventFilter
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPGifPlayButtonEventFilter import LPGifPlayButtonEventFilter
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPVolumeButtonEventFilter import LPVolumeButtonEventFilter
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPQueueManager import LPQueueState
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPTrackMoreMenu import LPTrackMoreMenu

class LPMiniBarViewController(QObject):
    updateUISignal = pyqtSignal(object)
    updateTitleSignal = pyqtSignal(object)
    updateCoverImageSignal = pyqtSignal(object)
    updatePlayButtonSignal = pyqtSignal(object)
    updateProgressSignal = pyqtSignal(object)
    updateVolumeSignal = pyqtSignal(object)
    updateQueueButtonLoopModeSignal = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        '''
        初始化 minibar 控制器。

        参数:
            parent: minibar 所属的主窗口或播放页控件。
        返回值:
            None。
        '''
        super().__init__(parent)
        self.canViewArtist = False
        self.artistItem = None
        self.parent = parent
        self.miniBarFrame = parent.miniBarFrame
        self.minibarMoreButton = parent.minibarMoreButton
        self.minibarMoreButton.setIcon(QIcon(LPGlobalUI.imagePath('more.png')))
        self.minibarMoreButton.clicked.connect(self.showTackMore)
        self.coverButton = parent.coverButton
        self.trackButton = parent.trackButton
        self.artistButton = parent.artistButton
        self.msIconLabel = parent.msIconLabel
        self.prevButton = parent.playPrevButton
        self.playButton = parent.playButton
        self.nextButton = parent.playNextButton
        self.progressSlider = parent.progressSlider
        self.leftTimeLabel = parent.leftTimeLabel
        self.rightTimeLabel = parent.rightTimeLabel
        self.volumeButton = parent.volumeButton
        self.volumeLabel = parent.volumeLabel
        self.deviceButton = parent.deviceButton
        self.deviceLabel = self._installDeviceMarqueeLabel(parent)
        self.queueButton = parent.queueButton
        self.queueLabel = getattr(parent, 'queueLabel', None)
        if self.queueLabel is None:
            self.queueLabel = getattr(parent, 'label_5', None)
        self.queueFrame = getattr(parent, 'queueFrame', None)
        self.volumeController = LPGlobalUI.loadUI(LPUIPath.MiniBarVolumeSliderUI, Ui_volumeSliderWidget, LPVolumeSliderViewController, self.volumeButton)
        self.volumeController.hide()
        self.volumeSlider = self.volumeController.volumeSlider
        self.queueDialog = None
        self._miniGroupEditDialogController = None
        self._deviceButtonIconKey = None
        self._deviceButtonSelected = False
        self._queueButtonSelected = False
        self.groupMgr = LPGroupManager.instance()
        self.setupUi()

    
    def setupUi(self):
        '''
        初始化 minibar 控件样式、信号和状态。

        参数:
            无。
        返回值:
            None。
        '''
        self.volumeController.setFixedWidth(40)
        self.coverButton.setIcon(QIcon(LPGlobalUI.imagePath('miniBar/trackDefault.png')))
        self.coverButton.clicked.connect(self.onCoverPressed)
        self.queueButton.isQueueShow = False
        self.queueButton.setCheckable(True)
        self.queueButton.clicked.connect(self.onQueuePressed)
        self._setDeviceButtonIcon(False, False)
        self.deviceButton.clicked.connect(self.onDeviceButtonPressed)
        if self.queueLabel is not None:
            self.queueLabel.setText(QCoreApplication.translate('minibar', 'Queue'))
        self._setQueueButtonSelected(False)
        defaultImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/vol.png'), LPGlobalUI.THEME_BUTTON_DEFAULT_COLOR_UI)
        hoverImage = LPGlobalUI.imagePath('miniBar/vol.png')
        LPVolumeButtonEventFilter(self.volumeButton, self.volumeController, QIcon(defaultImage), QIcon(hoverImage), QIcon(defaultImage))
        self.artistButton.clicked.connect(self.onArtistButtonPressed)
        self.prevButton.clicked.connect(self.prevButtonPressed)
        self.playButton.clicked.connect(self.playButtonPressed)
        self._updateQTPlayButton(None)
        self.nextButton.clicked.connect(self.nextButtonPressed)
        self.rightTimeLabel.setMinimumWidth(38)
        self.rightTimeLabel.setMaximumWidth(42)
        self.progressSlider.userUpdateValueChanged.connect(self.progressSliderChanged)
        self.progressSlider.userUpdateValueChanging.connect(self.progressSliderChanging)
        self.progressSlider.useFixedTrackGradient = True
        self.progressSlider.updateUISignal.emit()
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/vol.png'), LPGlobalUI.THEME_LIGHT_COLOR)
        self.volumeButton.clicked.connect(self.muteButtonPressed)
        self.volumeSlider.userUpdateValueChanged.connect(self.volumeSliderChanged)
        self.volumeSlider.userUpdateValueChanging.connect(self.volumeSliderChanging)
        self.volumeSlider.updateUISignal.emit()
        self.updateUISignal.connect(self._updateQT)
        self.updateTitleSignal.connect(self._updateQTTitle)
        self.updateCoverImageSignal.connect(self._updateQTCoverImage)
        self.updatePlayButtonSignal.connect(self._updateQTPlayButton)
        self.updateProgressSignal.connect(self._updateProgress)
        self.updateVolumeSignal.connect(self._updateVolume)
        self.updateQueueButtonLoopModeSignal.connect(self._updateQueueButtonLoopMode)
        if isinstance(self.parent, QMainWindow):
            self.progressTimer = Thread(self._progressTimerMethod, **('target',))
            self.progressTimer.setDaemon(True)
            self.progressTimer.start()
        self.map = {
            'prev': {
                'button': self.prevButton,
                'imgUrl': 'miniBar/left.png' },
            'next': {
                'button': self.nextButton,
                'imgUrl': 'miniBar/right.png' } }
        self._restMapGuiBehavior()
        stylesheetTemplate = Template('\n                    QLabel#leftTimeLabel, #rightTimeLabel {\n                        font-size: ${minibarSubtitleFontSize}pt;\n                        color: $grayFontColor;\n                    }\n                    QLabel#deviceLabel, #queueLabel, #volumeLabel {\n                        font-size: ${buttonSubTitleLabelFontSize}pt;\n                        color: $grayFontColor;\n                    }\n                    QPushButton {\n                        background: transparent;\n                    }\n                    QPushButton#trackButton {\n                        font-size: ${trackButtonFontSize}pt;\n                    }\n                    QPushButton#artistButton {\n                        font-size: ${artistButtonFontSize}pt;\n                    }\n                    QFrame#miniBarFrame{\n                        background: black;\n                        border-top: 1px solid  rgb(18, 18, 18);\n                    }\n            ')
        self.miniBarFrame.setStyleSheet(stylesheetTemplate.substitute(f'''{Min_Text}''', f'''{Min_Text}''', f'''{Main_Text}''', f'''{Sub_Text}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DISABLE_COLOR.name(), **('minibarSubtitleFontSize', 'buttonSubTitleLabelFontSize', 'trackButtonFontSize', 'artistButtonFontSize', 'fontCor', 'grayFontColor')))
        if self.deviceLabel is not None:
            self.deviceLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        if self.queueLabel is not None:
            self.queueLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self._syncMiniBarEntryLabelStyles()

    
    def showTackMore(self):
        '''
        展示当前曲目的更多操作菜单。

        参数:
            无。
        返回值:
            None。
        '''
        menu = LPTrackMoreMenu(LPGlobalUI.currentDevice.mediaInfo.trackSource, self.minibarMoreButton)
        menu.showMenu()

    
    def onDeviceButtonPressed(self):
        '''
        打开 minibar 设备/分组编辑弹窗。

        参数:
            无。
        返回值:
            None。
        '''
        current_device = LPGlobalUI.currentDevice
        if current_device is None:
            return None
        dashboard = None(self.parent, 'deviceDashboardViewController', None)
        if dashboard is not None:
            wrapper = None
            wrapper_getter = getattr(dashboard, '_groupEditWrapperForDevice', None)
            if callable(wrapper_getter):
                wrapper = wrapper_getter(current_device)
            if wrapper is None:
                wrapper = LPDeviceItemWrapper(current_device)
            open_method = getattr(dashboard, 'openEditGroupDialog', None)
            if callable(open_method):
                dialog_controller = getattr(dashboard, 'editGroupDialogViewController', None)
                open_with_mode = getattr(dialog_controller, 'openDialogWithMode', None)
                if callable(open_with_mode):
                    open_with_mode(wrapper, 'minibar')
                    self._bindGroupEditDialogState(dialog_controller)
                    self._setDeviceButtonSelected(True)
                else:
                    open_method(wrapper)
                return None
            if None._miniGroupEditDialogController is None:
                host = LPGlobalUI.mainWindow if LPGlobalUI.mainWindow is not None else self.parent
                self._miniGroupEditDialogController = LPEditGroupDialogViewController.createForHostWindow(host, **('parent',))
        wrapper = LPDeviceItemWrapper(current_device)
        open_with_mode = getattr(self._miniGroupEditDialogController, 'openDialogWithMode', None)
        if callable(open_with_mode):
            open_with_mode(wrapper, 'minibar')
            self._bindGroupEditDialogState(self._miniGroupEditDialogController)
            self._setDeviceButtonSelected(True)
        else:
            self._miniGroupEditDialogController.openDialog(wrapper)

    
    def updateUI(self, device, infoType, detail):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            self.updateUISignal.emit(device)
            if infoType == 'media' and detail.get('trackName', None):
                self._updateQTTitleAsync(device)
            elif infoType == 'device':
                self._updateQTTitleAsync(device)

    
    def _progressTimerMethod(self):
