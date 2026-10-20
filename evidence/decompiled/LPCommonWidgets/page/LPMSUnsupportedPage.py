# Source Generated with Decompyle++
# File: LPMSUnsupportedPage.pyc (Python 3.9)

'''
@Time ： 2025/7/30 13:55
@Auth ： Chris
@File ：LPMSUnsupportedPage.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QWidget
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title

class LPMSUnsupportedPage(QWidget):
    
    def __init__(self = None, source = None):
        super().__init__()
        self.source = source

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QLabel{\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                    color: $fontColor;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), **('stackWidgetTiteFontSize', 'fontColor')))
        noteText = QCoreApplication.translate('MSUnsupportedPage', f'''Current device doesn\'t support {self.source}''')
        self.noteLabel.setText(noteText)

    __classcell__ = None

