# Source Generated with Decompyle++
# File: LPDeviceSettingSoundViewController.pyc (Python 3.9)

import json
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication
from threading import Thread
import time
from PyQt6.sip import isdeleted
import re
import LPGlobalUI
from HOME.DeviceSetting import LPDeviceSettingApCastViewController, LPDeviceSettingBtSourceViewController
from HOME.DeviceSetting.LPDeviceSettingApCastViewController_ui import Ui_apCastViewWidget
from HOME.DeviceSetting.LPDeviceSettingAutoSyncViewController import LPDeviceSettingAutoSyncViewController
from HOME.DeviceSetting.LPDeviceSettingAutoSyncViewController_ui import Ui_autoSyncViewWidget
from HOME.DeviceSetting.LPDeviceSettingBtSourceViewController_ui import Ui_btSourceViewWidget
from LPClientFramework import LPDeviceAudioOutput, LPDeviceAudioInput
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import DeviceSettings_Subtitle
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPPlayList.LPLocalMusicPlayList import LPLocalMusicPlayList, LPLocalMusicPlayHeader
from LPClientFramework.LPPlayList.LPPlayList import LPPlayItem
from LPClientFramework.LPPublicDefine import LPAudioOutEnum, LPAudioInputEnum, LPAudioPhonoEnum, LPDeviceCapability
from LPClientFramework.LPUtility import logger

class LPDeviceSettingSoundViewController(QWidget):
    showAutoSyncSignal = pyqtSignal(bool)
    updateSoundSignal = pyqtSignal()
    
    def __init__(self = None, deviceId = None, showLoadingButtonSignal = None):
        super(LPDeviceSettingSoundViewController, self).__init__()
        self.deviceId = deviceId
        self.showLoadingButtonSignal = showLoadingButtonSignal
        self.auxOutLevel = 2
        self.auxOutArray = []
        self.volumeLimit = 0
        self.audioChannel = 0
        self.volumeBalance = -2
        self.crossFade = False
        self.sampleRate = 44100
        self.bitDepth = 16
        self.spdifFixedResolution = 0
        self.coaxSampleRate = 44100
        self.coaxBitDepth = 16
        self.coaxFixedResolution = 0
        self.currentOutput = LPAudioOutEnum.AudioOutput_None
        self.currentOutputDeviceName = None
        self.latency = 0
        self.outputArray = []
        self.btConnectName = None
        self.showAudiocast = None
        self.audiocastConnectName = ''
        self.uacConnectName = ''
        self.digitalFilterSupportList = []
        self.digitalFilterType = -1
        self.subwooferStatus = False
        self.subwooferLevel = 0
        self.subwooferCF = 0
        self.subwooferPhase = 0
        self.subwooferSubdelay = None
        self.auxAutoSensing = False
        self.spdifAutoSensing = False
        self.audioInputArray = []
        self.lineinInputSampleRate = 44100
        self.lineinInputBitDepth = 16
        self.perSourceEnable = -1
        self.cecEnable = -1
        self.phonoType = -1
        self.syncNumber = 0
        self.autoSyncWidget = None
        self.audioChannelArray = [
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Mono'),
                'value': 3 },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Stereo'),
                'value': 0 },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Left Channel'),
                'value': 1 },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Right Channel'),
                'value': 2 }]
        self.bitDepthArray = [
            {
                'title': QCoreApplication.translate('DeviceSetting', '16 bits'),
                'value': 16,
                'filePart': '16bits' },
            {
                'title': QCoreApplication.translate('DeviceSetting', '24 bits'),
                'value': 24,
                'filePart': '24bits' }]
        self.lineinInputBitDepthArray = [
            {
                'title': QCoreApplication.translate('DeviceSetting', '16 bits'),
                'value': 16,
                'filePart': '16bits' },
            {
                'title': QCoreApplication.translate('DeviceSetting', '24 bits'),
                'value': 32,
                'filePart': '24bits' }]
        self.sampleRateArray = [
            {
                'title': QCoreApplication.translate('DeviceSetting', '44.1 kHz'),
                'value': 44100,
                'filePart': '44kHz' },
            {
                'title': QCoreApplication.translate('DeviceSetting', '48 kHz'),
                'value': 48000,
                'filePart': '48kHz' },
            {
                'title': QCoreApplication.translate('DeviceSetting', '96 kHz'),
                'value': 96000,
                'filePart': '96kHz' },
            {
                'title': QCoreApplication.translate('DeviceSetting', '192 kHz'),
                'value': 192000,
                'filePart': '192kHz' }]

    
    def setupUi(self = None, ui = None):
