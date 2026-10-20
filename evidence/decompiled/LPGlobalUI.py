# Source Generated with Decompyle++
# File: LPGlobalUI.pyc (Python 3.9)

import math
import sys
from typing import Optional
from PyQt6 import QtCore, uic, QtGui, QtWidgets
from PyQt6.QtCore import pyqtProperty, pyqtSignal, QObject, Qt, QTranslator
from PyQt6.QtGui import QPainter
from PyQt6.QtSvg import QSvgRenderer
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog
from HOME.LPToaster import LPToaster
from LPClientFramework import LPUtility, LPPublicDefine
from LPClientFramework.LPConfig.LPUIConfig import UIConfig
from LPClientFramework.LPEventTrack import LPEventTrack
from LPClientFramework.LPFeature.LPFeaturesManager import LPFeaturesManager
from LPClientFramework.LPHibernation import LPHibernationManager
from LPClientFramework.LPSignalBus import LPSignalBus
from LPClientFramework.LPUtility import logger
translator = None
mainWindow = None
currentDevice = None
rootStackedWidget = None
uiConfig = UIConfig()
featureManager = LPFeaturesManager()
deviceManager = None
ssdpServer = None
hibernationManager = LPHibernationManager().instance()
eventTrack = LPEventTrack()
signalBus = LPSignalBus()

class LPWiiMRadioCountryCodeResolver(QObject):
    countryCodeChanged = pyqtSignal()
    subcountryCodeChanged = pyqtSignal()
    stateChanged = pyqtSignal()
    
    def __init__(self = None, parent = None):
        '''
        初始化全局国家代码解析器。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._country_code = ''
        self._subcountry_code = ''
        self._has_resolved = False
        self._is_loading = False
        self._provider = None
        self._request_token = ''

    
    def countryCode(self = None):
        '''
        返回当前缓存的国家代码。

        :param: 无。
        :return: 两位国家代码；未知时为空字符串。
        '''
        return self._country_code

    countryCode = None(countryCode)
    
    def subcountryCode(self = None):
        '''
        返回当前缓存的子地区代码。

        :param: 无。
        :return: 子地区代码；未知时为空字符串。
        '''
        return self._subcountry_code

    subcountryCode = None(subcountryCode)
    
    def hasResolved(self = None):
        '''
        返回是否已经完成过一次解析。

        :param: 无。
        :return: 已完成解析返回 True。
        '''
        return self._has_resolved

    hasResolved = None(hasResolved)
    
    def isLoading(self = None):
        '''
        返回是否正在请求国家代码。

        :param: 无。
        :return: 请求中返回 True。
        '''
        return self._is_loading

    isLoading = None(isLoading)
    
    def ensureLoaded(self = None):
        '''
        幂等触发国家代码加载。

        :param: 无。
        :return: None。
        '''
        if self._has_resolved or self._is_loading:
            return None
        provider = None._ensureProvider()
        self._is_loading = True
        self.stateChanged.emit()
        self._request_token = provider.fetchLocationCountryCode(self._handleLocationResult, { }, **('callback', 'context'))
        logger.debug(f'''[WiiMRadio] start resolving global countryCode token={self._request_token}''')

    
    def _ensureProvider(self):
        '''
        懒创建 WiiMRadio 数据提供器。

        :param: 无。
        :return: 数据提供器对象。
        '''
        if self._provider is None:
            LPWiiMRadioDataProvider = LPWiiMRadioDataProvider
            import HOME.StreamService.WiiMRadio.utils.LPWiiMRadioDataProvider
            self._provider = LPWiiMRadioDataProvider(self, **('parent',))
        return self._provider

    
    def _handleLocationResult(self = None, result = None):
        '''
        处理 location API 返回并更新全局缓存。

        :param result: 国家代码请求结果。
        :return: None。
        '''
        success = bool(result.get('success')) if isinstance(result, dict) else False
        error = str('') if isinstance(result, dict) else ''
        next_country_code = ''
        next_subcountry_code = ''
        if success:
            if not result.get('countryCode', ''):
                pass
            next_country_code = str('').strip().upper()
            if not result.get('subcountryCode', ''):
                pass
            next_subcountry_code = str('').strip()
        country_changed = next_country_code != self._country_code
        subcountry_changed = next_subcountry_code != self._subcountry_code
        self._country_code = next_country_code
        self._subcountry_code = next_subcountry_code
        self._has_resolved = True
        self._is_loading = False
        self._request_token = ''
        if country_changed:
            self.countryCodeChanged.emit()
        if subcountry_changed:
            self.subcountryCodeChanged.emit()
        self.stateChanged.emit()
        if success:
            logger.debug(f'''[WiiMRadio] global countryCode resolved={self._country_code}, subcountryCode={self._subcountry_code}''')
            return None
        if not error:
            pass
        None.warning(f'''[WiiMRadio] global countryCode resolve failed, fallback to global result, error={'empty'}''')

    __classcell__ = None

wiimRadioCountryCodeResolver = LPWiiMRadioCountryCodeResolver()
THEME_BACKGROUND_COLOR = QtGui.QColor(14, 14, 14, 255)
THEME_DISABLE_COLOR = QtGui.QColor(108, 108, 108, 255)
THEME_LIGHT_COLOR = QtGui.QColor(255, 255, 255, 200)
THEME_DEFAULT_COLOR = QtGui.QColor('white')
THEME_ACCENT_COLOR = QtGui.QColor(79, 89, 247, 255)
THEME_HIGH_COLOR = THEME_ACCENT_COLOR
THEME_HIGH_HIGH_COLOR = THEME_ACCENT_COLOR
THEME_HIGH_HIGH_DISABLED_COLOR = QtGui.QColor(102, 110, 224, 90)
THEME_TABLE_HOVER_BACK_COLOR = QtGui.QColor(65, 65, 65)
THEME_ITEM_BACK_COLOR = QtGui.QColor(32, 32, 32)
THEME_TABLE_HIGHLIGHT_BACK_COLOR = QtGui.QColor(72, 72, 72)
THEME_TOAST_BACK_COLOR = QtGui.QColor(37, 96, 197)
THEME_CLOSE_BACK_COLOR = QtGui.QColor(191, 0, 33)
THEME_BUTTON_BACK_COLOR = QtGui.QColor(72, 72, 72)
THEME_BUTTON_HOVER_BACK_COLOR = QtGui.QColor(77, 86, 219, 255)
THEME_BACKGROUND_COLOR_UI = QtGui.QColor(19, 19, 19, 255)
THEME_FONT_COLOR_UI = QtGui.QColor(255, 255, 255)
THEME_BUTTON_BACK_COLOR_UI = THEME_ACCENT_COLOR
THEME_BUTTON_DEFAULT_COLOR_UI = QtGui.QColor(130, 130, 130)
THEME_DIALOG_BACK_COLOR_UI = QtGui.QColor(40, 40, 40)
THEME_Item_HOVER_BACK_COLOR_UI = QtGui.QColor(255, 255, 255, 30)
THEME_LIGHT_COLOR_UI = QtGui.QColor(255, 255, 255, 166)
QSS_THEME_LIGHT_COLOR_UI = THEME_LIGHT_COLOR_UI.name(QtGui.QColor.NameFormat.HexArgb)
QSS_THEME_BUTTON_BACK_PRESS_COLOR = 'rgba(77, 86, 219, 128)'
QSS_THEME_TABLE_HOVER_BACK_COLOR = 'rgba(31, 31, 31, 255 )'
QSS_CLOSE_BACK_COLOR = 'rgba(191, 0, 33, 255 )'
QSS_MENU_HOVER_COLOR = 'rgba(255, 255, 255, 0.06)'

def getTopWidget():
    return rootStackedWidget.currentWidget()


def canNextWidget():
    return rootStackedWidget.currentIndex() < rootStackedWidget.count() - 1


def nextWidget():
    if not canNextWidget():
        return None
    topWidget = None.currentWidget()
    if topWidget:
        method = getattr(topWidget, 'viewWillDisappear', None)
        if method and callable(method):
            topWidget.viewWillDisappear()
    rootStackedWidget.setCurrentIndex(rootStackedWidget.currentIndex() + 1)
    topWidget = rootStackedWidget.currentWidget()
    logger.debug('[UI] =========================== next page= %s' % topWidget.__class__.__name__)
    method = getattr(topWidget, 'viewWillAppear', None)
    if method and callable(method):
        topWidget.viewWillAppear()


def canPrevWidget():
    return rootStackedWidget.currentIndex() != 0


def prevWidget():
    if not canPrevWidget():
        return None
    topWidget = None.currentWidget()
    if topWidget:
        method = getattr(topWidget, 'viewWillDisappear', None)
        if method and callable(method):
            topWidget.viewWillDisappear()
    rootStackedWidget.setCurrentIndex(rootStackedWidget.currentIndex() - 1)
    topWidget = rootStackedWidget.currentWidget()
    logger.debug('