# Source Generated with Decompyle++
# File: LPDeviceItemWrapper.pyc (Python 3.9)

'''
@Time ： 2026/2/5 12:36
@Auth ： Chris
@File ：LPDeviceItemWrapper.py
@Desc:
'''
import threading
import time
from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QCoreApplication, pyqtSlot, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QPixmap, QImage
import LPGlobalUI
from HOME.DeviceDashboard.LPDeviceCoverImageHelper import coverCanvasPixmap
from HOME.DeviceSetting.LPDeviceSettingViewController import LPDeviceSettingViewController
from HOME.DeviceSetting.LPDeviceSettingViewController_ui import Ui_deviceSettingViewWidget
from LPClientFramework import LPUtility, LPStreamServiceManager
from LPClientFramework.LPConfig import LPUIPath, LPFontConfig
from LPClientFramework.LPPalette import extractThemeColorRgbFromImage
from LPClientFramework.LPUtility import logger

class LPDeviceItemWrapper(QObject):
    updateUISignal = pyqtSignal()
    deviceNameChanged = pyqtSignal()
    trackNameChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    playStateChanged = pyqtSignal()
    artistNameChanged = pyqtSignal()
    coverChanged = pyqtSignal()
    bgColorChanged = pyqtSignal()
    sourceIconChanged = pyqtSignal()
    muteChanged = pyqtSignal()
    fixedVolumeChanged = pyqtSignal()
    
    def __init__(self = None, deviceNode = None):
        super().__init__()
        self.node = deviceNode
        LPUtility.registerDeviceInfoChanged(self)
        self.updateUISignal.connect(self._updateItem)
        self.originalBackgroundColor = QColor(77, 77, 77)
        self._bgColor = self.originalBackgroundColor
        self.artwork = ''
        self.isSourceShow = False
        self._mute = False
        self._fixedVolume = False
        self._coverCache = ''
        self._coverPixmapKey = None
        self._hasArtwork = False
        self._coverUpdateTimer = QTimer(self)
        self._coverUpdateTimer.setSingleShot(True)
        self._coverUpdateTimer.timeout.connect(self._updateCoverImageAsync)
        self._createdAt = time.monotonic()
        self._inView = False
        self._updateCoverImageAsync()

    
    def __del__(self):
        self.dispose()

    
    def dispose(self):
        pass
    # WARNING: Decompyle incomplete

    
    def device(self):
        if self.node is None:
            return None
        master = None(self.node, 'masterDevice', None)
        if master is not None:
            return master
        if None(self.node, 'uuid') and hasattr(self.node, 'mediaInfo'):
            return self.node

    device = pyqtProperty('QVariant', True, **('constant',))(device)
    
    def deviceUuid(self):
        device = self.device
        if device is None:
            return ''
        if not None(device, 'uuid', ''):
            pass
        return ''

    deviceUuid = pyqtProperty(str, deviceNameChanged, **('notify',))(deviceUuid)
    
    def nameFont(self):
        return LPFontConfig.Main_Text

    nameFont = pyqtProperty(float, True, **('constant',))(nameFont)
    
    def trackNameFont(self):
        return LPFontConfig.Main_Text

    trackNameFont = pyqtProperty(float, True, **('constant',))(trackNameFont)
    
    def artistNameFont(self):
        return LPFontConfig.Sub_Text

    artistNameFont = pyqtProperty(float, True, **('constant',))(artistNameFont)
    
    def volNumFont(self):
        return LPFontConfig.Sub_Text

    volNumFont = pyqtProperty(float, True, **('constant',))(volNumFont)
    
    def deviceName(self):
        device = self.device
        if device is None:
            return ''
        if not None.name:
            pass
        return ''

    deviceName = pyqtProperty(str, deviceNameChanged, **('notify',))(deviceName)
    
    def trackName(self):
        device = self.device
        if device is None:
            return ''
        hasMusicSelected = None.checkHasMusicSelected(device)
        if not hasMusicSelected:
            return QCoreApplication.translate('Device Dashboard', 'No Music Selected')
        if not None.mediaInfo.trackName:
            pass
        retur