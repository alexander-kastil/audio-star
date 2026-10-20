# Source Generated with Decompyle++
# File: LPUriHandler.pyc (Python 3.9)

'''
@Time ： 2025/8/5 10:23
@Auth ： Chris
@File ：LPUriHandler.py
@Desc:
'''
import enum
import platform
import sys
import time as _time
import urllib.parse as urllib
from PyQt6.QtCore import QTimer
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger

class LPUriType(enum.Enum):
    '''WiiM Home 支持处理的 URI 类型。'''
    LP_Uri_Active_Window = 'wiim://active'
    LP_Uri_ShowApp_Window = 'wiim://showApp'
    LP_Uri_OAuth_Callback = 'com.linkplay.wiimhome://callback'
    LP_Uri_Wiim_OAuth_Callback = 'wiim://callback'


def isSupportedUri(uri = None):
    '''
    判断 URI 是否属于 WiiM Home 可处理的 deep link。

    :param uri: 外部传入的 URI。
    :return: 支持处理返回 True。
    '''
    if not uri:
        pass
    normalized_uri = str('')
    if not normalized_uri.startswith('wiim'):
        pass
    return normalized_uri.startswith('com.linkplay.wiimhome://')


def handlerUri(uri = None):
    '''
    分发 WiiM Home deep link。

    :param uri: 外部传入的 URI。
    :return: None。
    '''
    logger.debug('[LPUriHandler]....')
    if uri.startswith(LPUriType.LP_Uri_OAuth_Callback.value) or uri.startswith(LPUriType.LP_Uri_Wiim_OAuth_Callback.value):
        handleOAuthCallback(uri)
    elif uri.startswith(LPUriType.LP_Uri_Active_Window.value):
        activeWindow()
    elif uri.startswith(LPUriType.LP_Uri_ShowApp_Window.value):
        logger.debug('[LPUriHandler] showApp')
        LPGlobalUI.mainWindow.showApp()


def handleOAuthCallback(uri = None):
    '''
    处理远端 auth.wiimhome.com 返回的 OAuth callback deep link。

    :param uri: 形如 com.linkplay.wiimhome://callback?... 的 URI。
    :return: None。
    '''
    if not uri:
        pass
    parsed = urllib.parse.urlparse(str(''))
    if parsed.scheme not in ('com.linkplay.wiimhome', 'wiim') or parsed.netloc != 'callback':
        return None
    query = None.parse.parse_qs(parsed.query)
    if _firstQueryValue(query, 'category') != 'oauth':
        return None
    service = None(query, 'service').lower()
    source = _sourceFromOAuthService(service)
    if not source:
        logger.warning('[LPUriHandler] ignore OAuth callback because service unsupported: %s', service)
        return None
    code = None(query, 'code')
    if not code:
        logger.warning('[LPUriHandler] ignore OAuth callback because code missing service=%s', service)
        return None
    notify = {
        'exchange_code': None,
        'source': source }
    state = _firstQueryValue(query, 'state')
    if state:
        notify['state'] = state
    logger.debug('[LPUriHandler] OAuth callback service=%s state=%s', service, state)
    LPUtility.postNotification('OAuthCodeChanged', {
        'device': LPGlobalUI.currentDevice,
        'notify': notify })


def _firstQueryValue(query = None, key = None):
    '''
    从 parse_qs 结果读取第一个字符串值。

    :param query: query 参数字典。
    :param key: 字段名。
    :return: 字符串值，缺失时返回空字符串。
    '''
    values = query.get(key, [])
    if not values:
        return ''
    if not values[0]:
        pass
    return None('')


def _sourceFromOAuthService(service = None):
    '''
    将 auth.wiimhome.com 的 service 名转换为内部音源名。

    :param service: 回调 service 参数。
    :return: LPPlayListSource 字符串值；不支持时返回空字符串。
    '''
    if service == 'tidal':
        return LPPlayListSource.Tidal.value
    if None == 'qobuz':
        return LPPlayListSource.Qobuz.value


def activeWindow():
    '''
    激活 WiiM Home 主窗口。

    :return: None。
    '''
    QTimer.singleShot(0, _doActiveWindow)


def _doActiveWindow():
    '''
    实际执行 Windows 窗口激活操作。

    :return: None。
    '''
    logger.debug('[LPUriHandler] active window')
    mainWindow = LPGlobalUI.mainWindow
    if not mainWindow:
        logger.debug('[LPUriHandler] active window --> no mainWindow')
        return None
    if None.system() == 'Windows':
        logger.debug('[LPUriHandler] active window --> Windows')
        import win32gui
        import win32con
        import win32process
        import win32api
        import ctypes
        fg_window = win32gui.GetForegroundWindow()
        (fg_thread, _) = win32process.GetWindowThreadProcessId(fg_window)
        current_thread = win32api.GetCurrentThreadId()
        ctypes.windll.user32.AttachThreadInput(fg_thread, current_thread, True)
        hwnd = int(mainWindow.winId())
        placement = win32gui.GetWindowPlacement(hwnd)
        showCmd = placement[1]
        if showCmd == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        elif showCmd == win32con.SW_SHOWMAXIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(hwnd)
        ctypes.windll.user32.AttachThreadInput(fg_thread, current_thread, False)
        logger.debug('windows active end')
    elif platform.system() == 'Darwin':
        logger.debug('[LPUriHandler] active window --> mac')
        NSApp = NSApp
        import AppKit
        NSApp.activateIgnoringOtherApps_(True)
    else:
        logger.debug('[LPUriHandler] active window --> else')
        mainWindow.showNormal()
        mainWindow.raise_()
        mainWindow.activateWindow()

