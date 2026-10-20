# Source Generated with Decompyle++
# File: LPMSNoNetworkPage.pyc (Python 3.9)

'''
@Time ： 2025/7/30 13:56
@Auth ： Chris
@File ：LPMSNoNetworkPage.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QWidget
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, MyMusic_Subtitle

class LPMSNoNetworkPage(QWidget):
    
    def __init__(self = None, source = None):
        super().__init__()
        self.source = source

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QLabel#noteLabel{\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                    color: $fontColor;\n                }\n                QPushButton#retryButton {\n                    font-size: ${retryButtonFontSize}pt;\n                    background-color: $retryButtonBg;\n                    color: $btnFontColor;\n                    border-radius: 5px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', LPGlobalUI.THEME_DISABLE_COLOR.name(), LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), f'''{MyMusic_Subtitle}''', **('stackWidgetTiteFontSize', 'fontColor', 'btnFontColor', 'retryButtonBg', 'retryButtonFontSize')))
        noteText = QCoreApplication.translate('MSNoNetworkPage', 'This page is unavailable')
        self.noteLabel.setText(str(noteText))
        self.retryButton.setText(QCoreApplication.translate('MSNoNetworkPage', 'Try again'))
        self.retryButton.clicked.connect(self.onRetry)

    
    def onRetry(self):
        LPGlobalUI.navigationManager.pop(self)

    __classcell__ = None

