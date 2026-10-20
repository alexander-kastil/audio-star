# Source Generated with Decompyle++
# File: LPTrayMenuController.pyc (Python 3.9)

'''系统托盘菜单控制器。

将从 WiiMHome.py 中拆分出的托盘菜单代码迁移至此，
负责托盘图标创建（含平台差异）、托盘上下文菜单（打开应用 / 退出）
以及退出流程中的托盘图标清理。
'''
import platform
from PyQt6.QtCore import QCoreApplication, QObject
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon
import LPGlobalUI

class LPTrayMenuController(QObject):
    '''管理系统托盘图标与托盘上下文菜单。'''
    
    def __init__(self = None, owner = None, onShow = None, onQuit = None):
        '''初始化托盘控制器。

        参数:
            owner (QMainWindow): 主窗口实例，作为托盘图标的父对象。
            onShow (callable): 打开/恢复主窗口的回调。
            onQuit (callable): 退出应用的回调。
        返回:
            无。
        '''
        super().__init__()
        self.owner = owner
        self._onShow = onShow
        self._onQuit = onQuit
        self.trayIcon = None

    
    def setupTrayMenu(self):
        '''
        创建托盘图标与上下文菜单。

        参数:
            无
        返回:
            无
        '''
        self.trayIcon = QSystemTrayIcon(self.owner)
        if platform.system() == 'Darwin':
            path = LPGlobalUI.imagePath('tray_ico.png')
            icon = QIcon(path)
            icon.setIsMask(True)
        else:
            path = LPGlobalUI.imagePath('app.ico')
            icon = QIcon(path)
        self.trayIcon.setIcon(icon)
        tray_menu = QMenu()
        showText = QCoreApplication.translate('MainWindow', 'Open WiiM')
        showAction = QAction(showText, tray_menu)
        quitText = QCoreApplication.translate('MainWindow', 'Quit')
        quitAction = QAction(quitText, tray_menu)
        showAction.triggered.connect(self._onShow)
        quitAction.triggered.connect(self._onQuit)
        tray_menu.addAction(showAction)
        tray_menu.addSeparator()
        tray_menu.addAction(quitAction)
        self.trayIcon.setContextMenu(tray_menu)
        
        def onTrayActivated(reason = None):
            '''
            deal click -- windows need
            '''
            if platform.system() == 'Windows' and reason == QSystemTrayIcon.ActivationReason.Trigger:
                self._onShow()

        self.trayIcon.activated.connect(onTrayActivated)
        self.trayIcon.show()

    
    def hideTrayIcon(self):
        '''
        隐藏并销毁托盘图标（退出流程调用）。

        参数:
            无
        返回:
            无
        '''
        if self.trayIcon:
            self.trayIcon.hide()
            self.trayIcon.deleteLater()
            self.trayIcon = None

    __classcell__ = None

