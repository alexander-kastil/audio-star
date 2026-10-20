# Source Generated with Decompyle++
# File: LPMS4xxErrorPage.pyc (Python 3.9)

'''
@Time ： 2025/7/30 13:56
@Auth ： Chris
@File ：LPMS4xxErrorPage.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QWidget
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, ErrorCodeTip

class LPMS4xxErrorPage(QWidget):
    
    def __init__(self = None, source = None, errorCode = None):
        super().__init__()
        self.source = source
        self.errorCode = errorCode

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QLabel#noteLabel{\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                    color: $fontColor;\n                }\n                QLabel#statusCodeLabel{\n                    font-size: ${statusCodeFontSize}pt;\n                    color: $errorCodeColor;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', f'''{ErrorCodeTip}''', LPGlobalUI.THEME_DISABLE_COLOR.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('stackWidgetTiteFontSize', 'statusCodeFontSize', 'fontColor', 'errorCodeColor')))
        self.statusCodeLabel.setText(str(self.errorCode))
        noteText = QCoreApplication.translate('MSNoNetworkPage', 'This page is unavailable')
        self.noteLabel.setText(noteText)

    __classcell__ = None

