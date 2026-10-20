# Source Generated with Decompyle++
# File: LPQobuzLoginViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/15 18:34
@Auth ： Chris
@File ：LPQobuzLoginViewController.py
@Desc:
'''
from string import Template
import LPGlobalUI
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title, MyMusic_Title
from LPClientFramework.LPUtility import logger

class LPQobuzLoginViewController(LPQobuzBaseViewController):
    
    def __init__(self = None):
        super().__init__()

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QLabel#qobuzLabel {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                    color: $fontColor;                \n                }\n                QLabel#tipLabel {\n                    font-size: ${tipFontSize}pt;\n                    color: $tipFontColor;                \n                }\n                \n                QPushButton#loginButton {\n                    font-size: ${loginButtonFontSize}pt;\n                    background-color: $loginButtonBg;\n                    color: $fontColor;\n                    border-radius: 5px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{MyMusic_Title}''', f'''{Qobuz_Sub_Title}''', f'''{Qobuz_Sub_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DISABLE_COLOR.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('stackWidgetTiteFontSize', 'loginButtonFontSize', 'tipFontSize', 'fontColor', 'tipFontColor', 'loginButtonBg')))
        self.loginButton.clicked.connect(self.onLoginButtonClicked)

    
    def viewWillAppear(self):
        logger.debug('Qobuz LPQobuzLoginViewController viewWillAppear')

    
    def viewWillDisappear(self):
        logger.debug('Qobuz  LPQobuzLoginViewController viewWillDisappear')

    
    def onLoginButtonClicked(self):
        self.qobuz.loginMgr.beginBrowserLogin()

    __classcell__ = None

