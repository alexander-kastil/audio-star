# Source Generated with Decompyle++
# File: LPQobuzArtistBiographyDialog.pyc (Python 3.9)

'''
@Time ： 2025/7/17 14:42
@Auth ： Chris
@File ：LPQobuzListFrameSection.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog
import LPGlobalUI
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT, Qobuz_Pure_Text, Qobuz_Sub_Title, MyMusic_Subtitle, ItemCard_Title

class LPQobuzArtistBiographyDialog(QDialog):
    
    def __init__(self = None, artistName = None, biography = None, parent = None):
        super().__init__(parent)
        self.artistName = artistName
        self.biography = biography

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.closeButton.setIcon(QIcon(LPGlobalUI.imagePath('dialog_close.png')))
        self.closeButton.clicked.connect(self.close)
        qssTemplate = Template('  \n                QWidget{\n                    border:none;\n                    background-color: transparent;\n                }              \n                QFrame{\n                    border:none;\n                    background-color: transparent;\n                }\n                QFrame#mainFrame{\n                    border-radius: 20px;\n                    background-color: $dialogBg;\n                    min-width: 700px;\n                    max-width: 700px;\n                }\n                QLabel {\n                    color: $fontColor;\n                }\n                QLabel#titleLabel {\n                    font-size: ${titleFontSize}pt;\n                }\n                QLabel#artistLabel {\n                    font-size: ${artistFontSize}pt;\n                }\n                QTextBrowser {\n                    font-size: ${textFontSize}pt;\n                    color: rgba(255, 255, 255, 168);\n                    \n                }\n\n                ')
        self.setStyleSheet(qssTemplate.substitute(LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, f'''{Qobuz_Pure_Text}''', f'''{ItemCard_Title}''', f'''{Qobuz_Sub_Title}''', **('highFontColor', 'highBg', 'fontColor', 'dialogBg', 'buttonBg', 'buttonHoverBg', 'textFontSize', 'titleFontSize', 'artistFontSize')))
        self.artistLabel.setText(self.artistName)
        self.textBrowser.setHtml(LPQobuzUtil.fixHtmlEntities(self.biography))

    
    def focusOutEvent(self = None, event = None):
        self.close()
        super().focusOutEvent(event)

    __classcell__ = None

