# Source Generated with Decompyle++
# File: LPDeviceSettingVoiceViewController.pyc (Python 3.9)

import re
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QCoreApplication
from PyQt6.sip import isdeleted
from threading import Thread
import LPGlobalUI
from HOME import LPSuperComboBox
from LPClientFramework.LPConfig.LPFontConfig import DeviceSettings_Subtitle
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter

class LPDeviceSettingVoiceViewController(QWidget):
    updateVoiceSignal = pyqtSignal()
    
    def __init__(self = None, deviceId = None, showLoadingButtonSignal = None):
        super(LPDeviceSettingVoiceViewController, self).__init__()
        self.deviceId = deviceId
        self.showLoadingButtonSignal = showLoadingButtonSignal
        self.avsCountry = 'unknown command'
        self.avsLan = QCoreApplication.translate('DeviceSetting', 'English (United States)')
        self.avsHD = False
        self.avsLanguages = [
            {
                'name': QCoreApplication.translate('DeviceSetting', 'English (United States)'),
                'key': 'en-US' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'English (United Kingdom/Ireland)'),
                'key': 'en-GB' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Deutsch (Deutschland/Österreich)'),
                'key': 'de-DE' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Canada'),
                'key': 'en-CA' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Japanese'),
                'key': 'ja-JP' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'English (India)'),
                'key': 'en-IN' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'English (Australia/New Zealand)'),
                'key': 'en-AU' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'French'),
                'key': 'fr-FR' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Italian'),
                'key': 'it-IT' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish (Mexico)'),
                'key': 'es-MX' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish'),
                'key': 'es-ES' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'French (Canada)'),
                'key': 'fr-CA' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Português (Brasil)'),
                'key': 'pt-BR' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Español (United States)'),
                'key': 'es-US' },
            {
                'name': QCoreApplication.translate('DeviceSetting', 'Hindi (India)'),
                'key': 'hi-IN' }]
        self.rowLanguages = [
            {
                'country': 'Netherlands',
                'key': 'en-GB',
                'code': 'NL',
                'name': QCoreApplication.translate('DeviceSetting', 'English UK') },
            {
                'country': 'Colombia',
                'key': 'es-US',
                'code': 'CO',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Sweden',
                'key': 'en-US',
                'code': 'SE',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Poland',
                'key': 'en-US',
                'code': 'PL',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Chile',
                'key': 'es-US',
                'code': 'CL',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Argentina',
                'key': 'es-US',
                'code': 'AR',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Costa Rica',
                'key': 'es-US',
                'code': 'CR',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Peru',
                'key': 'es-US',
                'code': 'PE',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Belgium',
                'key': 'en-US',
                'code': 'BE',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Belgium',
                'key': 'fr-FR',
                'code': 'BE',
                'name': QCoreApplication.translate('DeviceSetting', 'French') },
            {
                'country': 'Switzerland',
                'key': 'de-DE',
                'code': 'CH',
                'name': QCoreApplication.translate('DeviceSetting', 'German') },
            {
                'country': 'Switzerland',
                'key': 'en-US',
                'code': 'CH',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Switzerland',
                'key': 'it-IT',
                'code': 'CH',
                'name': QCoreApplication.translate('DeviceSetting', 'Italian') },
            {
                'country': 'Switzerland',
                'key': 'fr-FR',
                'code': 'CH',
                'name': QCoreApplication.translate('DeviceSetting', 'French') },
            {
                'country': 'Singapore',
                'key': 'en-US',
                'code': 'SG',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Turkey',
                'key': 'en-US',
                'code': 'TR',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Denmark',
                'key': 'en-US',
                'code': 'DK',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Norway',
                'key': 'en-US',
                'code': 'NO',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'United Arab Emirates',
                'key': 'en-US',
                'code': 'AE',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'South Korea',
                'key': 'en-US',
                'code': 'KR',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Malaysia',
                'key': 'en-US',
                'code': 'MY',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Indonesia',
                'key': 'en-US',
                'code': 'ID',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Philippines',
                'key': 'en-US',
                'code': 'PH',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Finland',
                'key': 'en-US',
                'code': 'FI',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Luxembourg',
                'key': 'de-DE',
                'code': 'LU',
                'name': QCoreApplication.translate('DeviceSetting', 'German') },
            {
                'country': 'Luxembourg',
                'key': 'en-US',
                'code': 'LU',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Luxembourg',
                'key': 'fr-FR',
                'code': 'LU',
                'name': QCoreApplication.translate('DeviceSetting', 'French') },
            {
                'country': 'Portugal',
                'key': 'en-US',
                'code': 'PT',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Saudi Arabia',
                'key': 'en-US',
                'code': 'SA',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Thailand',
                'key': 'en-US',
                'code': 'TH',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Dominican Republic',
                'key': 'es-US',
                'code': 'DO',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Ecuador',
                'key': 'es-US',
                'code': 'EC',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') },
            {
                'country': 'Hong Kong',
                'key': 'en-US',
                'code': 'HK',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'South Africa',
                'key': 'en-US',
                'code': 'ZA',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Taiwan',
                'key': 'en-US',
                'code': 'TW',
                'name': QCoreApplication.translate('DeviceSetting', 'English US') },
            {
                'country': 'Puerto Rico',
                'key': 'es-US',
                'code': 'PR',
                'name': QCoreApplication.translate('DeviceSetting', 'Spanish US') }]

    
    def setupUi(self = None, ui = None):
