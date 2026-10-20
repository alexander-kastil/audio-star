# Source Generated with Decompyle++
# File: LPQobuzGenresSelector.pyc (Python 3.9)

'''
@Time ： 2025/7/29 17:12
@Auth ： Chris
@File ：LPQobuzGenresSelector.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QPoint, Qt, pyqtSignal, QTimer, QCoreApplication
from PyQt6.QtWidgets import QCheckBox
import LPGlobalUI
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult

class LPQobuzGenresSelector(LPQobuzBaseViewController):
    showSignal = pyqtSignal()
    
    def __init__(self = None, parent = None, genreManager = None):
        super().__init__()
        self.parent = parent
        self.genreManager = genreManager
        self.playList = None
        self.checkboxes = []
        self.selectAllFlag = True
        self.showSignal.connect(self._show)
        self.refreshTimer = QTimer()
        self.refreshTimer.setSingleShot(True)
        self.refreshTimer.timeout.connect(self._doRefresh)
        self.allGenres = []

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.toggleBox.setStyleSheet('\n                QCheckBox::indicator{ \n                    width: 0; height: 0; \n                }\n                QCheckBox{\n                    text-decoration: underline;\n                    color: %s;\n                }\n            ' % LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name())
        self.toggleBox.setText(QCoreApplication.translate('qobuz selector', 'Select all'))
        self.toggleBox.clicked.connect(self.onSelectAllToggled)
        stylesheetTemplate = Template('\n                QFrame{\n                    background-color: $background;\n                    border:none;\n                }               \n                QFrame#mainFrame{\n                    border-radius: 10px;                   \n                }\n                QPushButton {\n                    color: $fontColor;\n                    font-size: ${fontSize}pt;\n                    background-color: transparent;\n                }\n                QPushButton:checked {\n                    text-decoration: underline;\n                    color: $checkedFontColor;\n\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), f'''{DEFAULT}''', **('fontColor', 'checkedFontColor', 'background', 'fontSize')))

    
    def onSelectAllToggled(self, checked):
        if checked:
            for cb in self.checkboxes:
                cb.setChecked(True)
            self.toggleBox.setText(QCoreApplication.translate('qobuz selector', 'Deselect all'))
            self.genreManager.selectAllGenres()
        else:
            for cb in self.checkboxes:
                cb.setChecked(False)
            self.toggleBox.setText(QCoreApplication.translate('qobuz selector', 'Select all'))
            self.genreManager.clearGenres()

    
    def onCheckboxClicked(self):
        checkbox = self.sender()
        self.genreManager.toggleGenre(checkbox.genre)
        self.changeToggleBoxStatus()
        self.refreshTimer.start(300)

    
    def changeToggleBoxStatus(self):
        logger.debug('[qobuz genres selector] changeToggleBoxStatus...')
        if len(self.genreManager.selectedGenres()) == len(self.allGenres):
            logger.debug('[qobuz genres selector] all')
            self.toggleBox.setChecked(True)
            self.toggleBox.setText(QCoreApplication.translate('qobuz selector', 'Deselect all'))
        else:
            logger.debug('[qobuz genres selector] not all')
            self.toggleBox.setChecked(False)
            self.toggleBox.setText(QCoreApplication.translate('qobuz selector', 'Select all'))

    
    def _doRefresh(self):
        self.genreManager.genresChangedSignal.emit(self.genreManager.selectedGenres())

    
    def toggleSelect(self):
        self.selectAllFlag = not (self.selectAllFlag)
        if self.selectAllFlag:
            for cb in self.checkboxes:
                cb.setChecked(True)
            self.toggleButton.setText('Deselect all')
        else:
            for cb in self.checkboxes:
                cb.setChecked(False)
            self.toggleButton.setText('Select all')
        self.genreManager.clearGenres()

    
    def getGenreList(self):
        
        def callback(result = None):
            if result.is_success():
                playList = result.data
                self.allGenres = playList.list
                self.genreManager.setAllGenres(playList.list)
                self.showSignal.emit()

        reqFunc = self.qobuz.requestMgr.fetchGenresData
        self.qobuz.requestMgr.fetch(reqFunc, callback)

    
    def populateGrid(self):
