# Source Generated with Decompyle++
# File: LPMenuBarController.pyc (Python 3.9)

'''主菜单栏与 macOS 原生应用菜单控制器。

将从 WiiMHome.py 中拆分出的菜单栏相关代码迁移至此，职责包括：
- QMenuBar（Play/Pause、Check for Updates、About 菜单）的构建；
- macOS 原生应用菜单（About/Check for Updates/Send Feedback）的注入与位置校正；
- Sparkle “Check for Updates” 菜单项可用性状态同步。
'''
import platform
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu
import LPGlobalUI
from HOME.LPAboutViewController import LPAboutViewController
from HOME.LPAboutViewController_ui import Ui_aboutViewWidget
from HOME.Menu.LPMenuBridge import ensureMacMenuActionBridgeClass
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPUtility import logger

class LPMenuBarController(QObject):
    '''主菜单栏 + macOS 原生应用菜单控制器。'''
    
    def __init__(self = None, owner = None, isUpdateReady = None, onCheckForUpdates = None, onOpenFeedback = None):
        '''初始化主菜单栏控制器。

        参数:
            owner (QMainWindow): 主窗口实例，提供 menuBar()/action_playpause 等 UI 部件。
            isUpdateReady (callable): 返回更新器是否就绪的可调用对象。
            onCheckForUpdates (callable): 触发手动检查更新的回调。
            onOpenFeedback (callable): 打开反馈对话框的回调。
        返回:
            无。
        '''
        super().__init__()
        self.owner = owner
        self._isUpdateReady = isUpdateReady
        self._onCheckForUpdates = onCheckForUpdates
        self._onOpenFeedback = onOpenFeedback
        self.checkForUpdatesAction = None
        self._macMenuActionBridge = None

    
    def checkForUpdates(self):
        '''桥接动作委托：触发手动检查更新。

        参数:
            无
        返回:
            无
        '''
        if self._onCheckForUpdates:
            self._onCheckForUpdates()

    
    def openFeedback(self):
        '''桥接动作委托：打开反馈对话框。

        参数:
            无
        返回:
            无
        '''
        if self._onOpenFeedback:
            self._onOpenFeedback()

    
    def setupMenuBar(self):
        '''
        初始化主菜单栏动作。

        参数:
            无
        返回:
            无
        '''
        
        def _playPauseAction():
            if not LPGlobalUI.currentDevice:
                return None
            if None.currentDevice.mediaInfo.playState == 'PLAYING':
                LPGlobalUI.currentDevice.updateMediaInfo({
                    'playState': 'PAUSED_PLAYBACK' })
                LPGlobalUI.currentDevice.asyncUpnpPost('Pause', None)
            else:
                LPGlobalUI.currentDevice.updateMediaInfo({
                    'playState': 'PLAYING' })
                LPGlobalUI.currentDevice.asyncUpnpPost('Play', None)

        self.owner.action_playpause.triggered.connect(_playPauseAction)
        if platform.system() == 'Windows':
            self.owner.menuBar().hide()
        menuBar = self.owner.menuBar()
        if platform.system() == 'Darwin':
            self.checkForUpdatesAction = QAction('Check for Updates', self.owner)
            self.checkForUpdatesAction.setEnabled(self._isUpdateReady())
            self.checkForUpdatesAction.triggered.connect(self._onCheckForUpdates)
            self.refreshSparkleMenuState()
            QTimer.singleShot(0, self.ensureMacNativeSparkleMenuItem)
            QTimer.singleShot(0, self.ensureMacNativeFeedbackMenuItem)
        
        def _showAboutDialog():
            aboutDialog = LPGlobalUI.loadUI(LPUIPath.AboutViewControllerUI, Ui_aboutViewWidget, LPAboutViewController)
            aboutDialog.setParent(LPGlobalUI.mainWindow)
            aboutDialog.setGeometry(0, 30, LPGlobalUI.mainWindow.size().width(), LPGlobalUI.mainWindow.size().height() - 30)
            aboutDialog.show()

        aboutMenu = 