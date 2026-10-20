# Source Generated with Decompyle++
# File: LPQobuzLogoutDialog.pyc (Python 3.9)

'''
@Time ： 2025/7/14 15:39
@Auth ： Chris
@File ：LPQobuzLogoutDialog.py
@Desc:
'''
import json
from string import Template
from threading import Thread
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QCoreApplication, QRectF
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtWidgets import QDialog, QMessageBox
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzAccount
from LPClientFramework.LPUtility import logger

class LPQobuzLogoutDialog(QDialog):
    updateAutoPlaySignal = pyqtSignal()
    logoutSignal = pyqtSignal()
    
    def __init__(self = None, account = None, button = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.parentButton = button
        self.account = account
        self.autoPlay = False
        self.updateAutoPlaySignal.connect(self._updateAutoPlay)
        self.logoutSignal.connect(self._logout)
        self.maxStreaming = self.account.maxStreaming
        self.userStreaming = None
        self.userReplayGain = None
        self.streamingArray = [
            {
                'title': 'HiRes - 24 bits / up to 192 kHz',
                'quality': 4 },
            {
                'title': 'HiRes - 24 bits / up to 96 kHz',
                'quality': 3 },
            {
                'title': 'CD - 16 bits / 44,1 kHz',
                'quality': 2 },
            {
                'title': 'MP3 - 320kbps',
                'quality': 1 }]
        self.replayGainArray = [
            {
                'title': 'Disabled',
                'val': 1 },
            {
                'title': 'Track Gain',
                'val': 0 }]
        self.cacheData = {
            'quality': None,
            'replayGain': None }
        self.qobuz = LPQobuzManager.instance()

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qssTemplate = Template('  \n                QWidget{\n                    border:none;\n                    background-color: transparent;\n                }              \n                QFrame{\n                    border:none;\n                    background-color: transparent;\n                }\n                QFrame#mainFrame{\n                    border-radius: 20px;\n                    background-color: $dialogBg;\n                    min-width: 350px;\n                    max-width: 350px;\n                }\n                QFrame#subscriptFrame{\n                    border-radius: 10px;\n                    background-color: $highBg;\n                    color: $highFontColor;\n                }\n                QLabel {\n                    color: $fontColor;\n                }\n\n                QPushButton#logoutButton {\n                    color: red;\n                }\n                QPushButton#cancelButton:hover {\n                    background-color: #3E3E3E;\n                }\n\n                ')
        self.setStyleSheet(qssTemplate.substitute(LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, **('highFontColor', 'highBg', 'fontColor', 'dialogBg', 'buttonBg', 'buttonHoverBg')))
        self.autoPlayToggle.clicked.connect(self._autoPlayToggleClicked)
        self.streamingBox.setupUI()
        self.replayGainBox.setupUI()
        self.logoutButton.clicked.connect(self.showConfirmBox)
        self.checkCacheData()
        self.requestAutoPlay()
        self.initComponent()

    
    def initComponent(self):
        subscription = self.account.subscription
        if subscription:
            if not self.account.subscription:
                pass
            self.subscriptInfoLabel.setText('')
        else:
            self.subscriptFrame.hide()
        if not self.account.email:
            pass
        self.emailInfoLabel.setText('')
        if not self.account.showName:
            pass
        self.accountInfoLabel.setText('')
        self.autoPlayTiplLabel.setStyleSheet('\n                                                color: %s\n                                             ' % LPGlobalUI.THEME_DISABLE_COLOR.name())
        self.updateStreaming()
        self.updateReplayGain()

    
    def _updateAutoPlay(self):
        self.autoPlayToggle.setChecked(self.autoPlay)

    
    def _autoPlayToggleClicked(self, state):
        self.setAutoPlay(state)

    
    def showDialog(self):
        button_bottom_right = self.parentButton.mapToGlobal(self.parentButton.rect().bottomRight())
        menu_size = self.sizeHint()
        menu_x = button_bottom_right.x() - menu_size.width()
        menu_y = button_bottom_right.y() + 10
        self.move(menu_x, menu_y)
        self.show()

    
    def focusOutEvent(self = None, event = None):
        self.close()
        super().focusOutEvent(event)

    
    def requestAutoPlay(self):
        
        def _asyncUpdate():
            device = LPGlobalUI.currentDevice
            if device is None:
                return None
            response = None.commonHttpGet(f'''getStreamServiceConfig:{LPPlayListSource.Qobuz.value}''')
            if response.get('status_code', 0) == 200:
                body = json.loads(response.get('body', ''))
                self.autoPlay = body.get('payload', { }).get('autoplay', False)
                self.updateAutoPlaySignal.emit()

        t = Thread(_asyncUpdate, True, **('target', 'daemon'))
        t.start()

    
    def setAutoPlay(self = None, autoPlay = None):
        
        def _asyncUpdate():
            device = LPGlobalUI.currentDevice
            if device is None:
                return None
            payload = {
                'source': None,
                'payload': {
                    'autoplay': autoPlay } }
            response = device.commonHttpPost('setStreamServiceConfig', payload)
            if response.get('status_code', 0) == 200:
                self.autoPlay = not (self.autoPlay)
            else:
                LPGlobalUI.toast.showToast(QCoreApplication.translate('QobuzLogout', 'Set AutoPlay Failed'), LPGlobalUI.mainWindow)
            self.updateAutoPlaySignal.emit()

        t = Thread(_asyncUpdate, True, **('target', 'daemon'))
        t.start()

    
    def updateStreaming(self):
        itemsArray = []
        displayItems = (lambda .0 = None: [ item for item in .0 if item['quality'] <= self.maxStreaming ])(self.streamingArray)
        for item in displayItems:
            itemsArray.append(item['title'])
            self.streamingBox.addItem(item['title'], item['quality'])
        matchedIndex = None
        for i in range(self.streamingBox.count()):
            if self.streamingBox.itemData(i, Qt.ItemDataRole.UserRole, **('role',)) == self.userStreaming:
                matchedIndex = i
            
            if matchedIndex is not None:
                self.streamingBox.setCurrentIndex(matchedIndex)
            else:
                self.streamingBox.setCurrentIndex(0)
        self.streamingBox.currentIndexChanged.connect(self.streamingIndexChanged)

    
    def updateReplayGain(self):
        for item in self.replayGainArray:
            self.replayGainBox.addItem(item['title'], item['val'])
        matchedIndex = None
        for i in range(self.replayGainBox.count()):
            if self.replayGainBox.itemData(i, Qt.ItemDataRole.UserRole, **('role',)) == self.userReplayGain:
                matchedIndex = i
            
            if matchedIndex is not None:
                self.replayGainBox.setCurrentIndex(matchedIndex)
            else:
                self.replayGainBox.setCurrentIndex(0)
        self.replayGainBox.currentIndexChanged.connect(self.replayGainIndexChanged)

    
    def checkCacheData(self):
        settings = LPUtility.settings
        userId = self.account.userId
        settings.beginGroup(f'''{LPPlayListSource.Qobuz.value}/{userId}''')
        self.userStreaming = settings.value('quality', None)
        self.userReplayGain = settings.value('replayGain', None)
        settings.endGroup()
        logger.debug(f'''[LPQobuzLogoutDialog] checkCacheData self.userStreaming={self.userStreaming} self.userReplayGain={self.userReplayGain}''')

    
    def setCacheData(self, key, value):
        settings = LPUtility.settings
        userId = self.account.userId
        if not userId:
            return None
        None.beginGroup(f'''{LPPlayListSource.Qobuz.value}/{userId}''')
        settings.setValue(key, value)
        settings.endGroup()
        logger.debug(f'''[LPQobuzLogoutDialog] setCacheData key={key} key={value}''')

    
    def streamingIndexChanged(self, index):
        logger.debug(f'''streamingIndexChanged {index}:{self.streamingBox.itemData(index, Qt.ItemDataRole.UserRole, **('role',))}''')
        quality = self.streamingBox.itemData(index, Qt.ItemDataRole.UserRole, **('role',))
        self.userStreaming = quality
        self.account.userStreaming = quality
        self.setCacheData('quality', quality)

    
    def replayGainIndexChanged(self, index):
        logger.debug(f'''replayGainIndexChanged {index}:{self.streamingBox.itemData(index, Qt.ItemDataRole.UserRole, **('role',))}''')
        val = self.replayGainBox.itemData(index, Qt.ItemDataRole.UserRole, **('role',))
        self.userReplayGain = val
        self.setCacheData('replayGain', val)

    
    def _logout(self):
        if self.parent.account.userId:
            self.qobuz.loginMgr.logout()
            self.close()

    
    def showConfirmBox(self):
        box = QMessageBox(LPGlobalUI.mainWindow)
        box.setWindowFlags(box.windowFlags() | Qt.WindowType.FramelessWindowHint)
        box.setText(QCoreApplication.translate('Qobuz logout', 'Would you like to log out?'))
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.button(QMessageBox.StandardButton.Yes).setText(QCoreApplication.translate('qobuz playlist detail', 'Log out'))
        box.button(QMessageBox.StandardButton.No).setText(QCoreApplication.translate('qobuz playlist detail', 'Cancel'))
        for button in box.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        box.setStyleSheet('\n            QMessageBox {\n            background: %s;\n            border-radius: 10px;\n            }\n            QMessageBox QLabel {\n            color: %s;\n            padding-top: 30px;\n            padding-left: 10px;\n            padding-right: 10px;\n            background: transparent;\n            min-width:400 px;\n            }\n            QPushButton {background-color: transparent;\n            border-radius: 5px;\n            padding: 5px 10px 5px 10px;\n            color: %s;\n            }\n            QPushButton:hover {\n            color: %s;\n            }\n            QPushButton:focus {\n            color: %s;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_HIGH_HIGH_COLOR.name(), LPGlobalUI.THEME_HIGH_COLOR.name()))
        box.resize(300, 240)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.show()
        path = QPainterPath()
        rect = QRectF(0, 0, box.geometry().size().width(), box.geometry().size().height())
        path.addRoundedRect(rect, 10, 10)
        mask = QRegion(path.toFillPolygon().toPolygon())
        box.setMask(mask)
        select = box.exec()
        if select == QMessageBox.StandardButton.Yes:
            self.logoutSignal.emit()

    __classcell__ = None

