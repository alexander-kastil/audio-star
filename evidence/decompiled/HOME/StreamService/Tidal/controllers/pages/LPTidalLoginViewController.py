# Source Generated with Decompyle++
# File: LPTidalLoginViewController.pyc (Python 3.9)

'''TIDAL QWidget 登录页控制器。'''
from string import Template
from typing import Optional
from PyQt6.QtCore import QTimer, pyqtSlot
from PyQt6.QtWidgets import QWidget
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, Qobuz_Sub_Title
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPUtility import logger

class LPTidalLoginViewController(QWidget):
    '''展示 TIDAL OAuth 登录入口并在登录成功后进入 TIDAL Shell。'''
    
    def __init__(self = None, parent = None, enterHomeOnSuccess = None):
        '''
        初始化 TIDAL QWidget 登录页。

        :param parent: 父级 QWidget。
        :param enterHomeOnSuccess: 登录成功后是否进入 TIDAL 首页。
        :return: None。
        '''
        super().__init__(parent)
        self._login_manager = LPTidalLoginManager.instance(self)
        self._enter_home_on_success = bool(enterHomeOnSuccess)
        self._login_entering = False
        self._login_signal_connected = False
        self._view_revision = 0
        Ui_tidalLoginWidget = Ui_tidalLoginWidget
        import HOME.StreamService.Tidal.controllers.pages.UI.LPTidalLoginViewController_ui
        self._ui = Ui_tidalLoginWidget()
        self._ui.setupUi(self)
        self.tidalLabel = self._ui.tidalLabel
        self.tipLabel = self._ui.tipLabel
        self.loginButton = self._ui.loginButton
        self.setupUi(self)

    
    def setupUi(self = None, ui = None):
        '''
        完成 Designer UI 加载后的样式和信号配置。

        :param ui: 已加载控件属性的当前页面。
        :return: None。
        '''
        _ = ui
        stylesheet_template = Template('\n            QLabel#tidalLabel {\n                font-size: ${titleFontSize}pt;\n                color: $fontColor;\n            }\n            QLabel#tipLabel {\n                font-size: ${tipFontSize}pt;\n                color: $tipFontColor;\n            }\n            QPushButton#loginButton {\n                font-size: ${buttonFontSize}pt;\n                background-color: $buttonBackground;\n                color: $fontColor;\n                border-radius: 5px;\n            }\n        ')
        self.setStyleSheet(stylesheet_template.substitute(f'''{MyMusic_Title}''', f'''{Qobuz_Sub_Title}''', f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DISABLE_COLOR.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('titleFontSize', 'tipFontSize', 'buttonFontSize', 'fontColor', 'tipFontColor', 'buttonBackground')))
        self.loginButton.clicked.connect(self.onBrowserLoginClicked)

    
    def __del__(self):
        '''
        析构时兜底断开登录成功信号。

        :return: None。
        '''
        self._disconnectLoginSignal()

    
    def viewWillAppear(self = None):
        '''
        页面显示时恢复登录成功监听，并同步设备侧 TIDAL 登录状态。

        :return: None。
        '''
        self._view_revision = int(getattr(self, '_view_revision', 0)) + 1
        self._login_entering = False
        self._connectLoginSignal()
        self._login_manager.clearErrorMessage()
        self._login_manager.syncAccountFromDevice(getattr(LPGlobalUI, 'currentDevice', None))

    
    def viewWillDisappear(self = None):
        '''
        页面隐藏时断开登录成功监听，避免隐藏页面抢占导航。

        :return: None。
        '''
        self._view_revision = int(getattr(self, '_view_revision', 0)) + 1
        self._login_entering = False
        self._disconnectLoginSignal()

    
    def _connectLoginSignal(self = None):
        '''幂等连接登录成功信号。

        :return: None。
        '''
        if bool(getattr(self, '_login_signal_connected', False)):
            return None
        None._login_manager.loginSucceeded.connect(self._onLoginSucceeded)
        self._login_signal_connected = True

 