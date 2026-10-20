# Source Generated with Decompyle++
# File: LPWinSparkleUpdater.pyc (Python 3.9)

'''
Windows WinSparkle 更新管理模块。
该模块负责：
1. 动态加载 WinSparkle.dll；
2. 读取配置并解析 appcast feed；
3. 初始化 WinSparkle 并触发自动/手动检查；
4. 注册更新安装前关机协同回调；
5. 在应用退出时清理 WinSparkle 资源。
'''
import ctypes
import json
import os
import platform
import re
import sys
import threading
import urllib.request as urllib
import xml.etree.ElementTree
ET = ElementTree
etree
from pathlib import Path
from LPClientFramework.LPUtility import appVersion, logger

class LPWinSparkleUpdater:
    '''Windows 平台 WinSparkle 更新管理器。'''
    
    def __init__(self):
        '''
        初始化 WinSparkle 更新器状态。

        参数:
            无
        返回:
            无
        '''
        self._dll = None
        self._ready = False
        self._config = self._loadConfig()
        self._canShutdownHandler = None
        self._shutdownRequestHandler = None
        self._canShutdownCallback = None
        self._shutdownRequestCallback = None
        callback_type = getattr(ctypes, 'WINFUNCTYPE', ctypes.CFUNCTYPE)
        self._canShutdownCallbackType = callback_type(ctypes.c_int)
        self._shutdownRequestCallbackType = callback_type(None)
        self._userRunInstallerCallbackType = callback_type(ctypes.c_int, ctypes.c_wchar_p)
        self._onUpdateFoundCallback = None
        self._onNoUpdateFoundCallback = None
        self._onUserRunInstallerCallback = None
        self._didFindUpdateCallback = None
        self._didNotFindUpdateCallback = None
        self._updateCheckErrorCallback = None
        self._userRunInstallerCallback = None
        self._updateFoundCallbackType = callback_type(None)
        self._noUpdateFoundCallbackType = callback_type(None)
        self._errorCallbackType = callback_type(None)
        self._backgroundCheckThread = None
        self._lastCheckDetail = { }
        self._temporaryFeedURL = ''

    
    def setShutdownHooks(self, canShutdownHandler, shutdownRequestHandler):
        '''
        设置 WinSparkle 关机协同回调处理器。

        参数:
            canShutdownHandler (callable): 返回 bool，表示当前是否允许退出。
            shutdownRequestHandler (callable): 接收到安装前关机请求时执行。
        返回:
            无
        '''
        self._canShutdownHandler = canShutdownHandler
        self._shutdownRequestHandler = shutdownRequestHandler

    
    def _loadConfig(self):
        '''
        读取应用配置文件。

        参数:
            无
        返回:
            dict: 解析后的配置字典；读取失败时返回空字典。
        '''
        if hasattr(sys, '_MEIPASS'):
            config_path = Path(sys._MEIPASS) / 'data' / 'config.json'
        else:
            repo_root = Path(__file__).resolve().parent.parent
            candidates = [
                repo_root / 'HOME' / 'data' / 'config.json',
                Path(__file__).resolve().parent / 'data' / 'config.json']
            config_path = None
            for candidate in candidates:
                if candidate.is_file():
                    config_path = candidate
                
                if config_path is None:
                    config_path = candidates[0]
    # WARNING: Decompyle incomplete

    
    def _sparkleConfig(self):
        '''
        获取 sparkle 配置段。

        参数:
            无
        返回:
            dict: sparkle 节点配置，不存在时返回空字典。
        '''
        sparkle = self._config.get('sparkle', { })
        if isinstance(sparkle, dict):
            return sparkle

    
    def _normalizeShortVersion(self, versionValue):
        '''
        将版本文本归一化为 WinSparkle 可比较的点分版本号。

        参数:
            versionValue (str): 版本信息文本。
        返回:
            str: 归一化后的点分版本号字符串。
        '''
        groups = (lambda .0: [ item for item in .0 if item ])(re.split('[^0-9]+', str(versionValue)))
        if not groups:
            return '0'
        return None.join((lambda .0: for item in .0:
str(int(item)))(groups))

    
    def _resolveCurrentVersion(self):
        '''
        解析本地用于 WinSparkle 比对的当前版本号。

        参数:
            无
        返回:
            str: 本地当前版本号。
        '''
        version_value = self._config.get('version', appVersion)
        return self._normalizeShortVersion(version_value)

    
    def _compareVersions(self, leftVersion, rightVersion):
        '''
        比较两个版本号大小。

        参数:
            leftVersion (str): 左侧版本号。
            rightVersion (str): 右侧版本号。
        返回:
            int: 左侧更大返回 1，相等返回 0，更小返回 -1。
        '''
        left_parts = (lambda .0: [ int(item) for item in .0 ])(self._normalizeShortVersion(leftVersion).split('.'))
        right_parts = (lambda .0: [ int(item) for item in .0 ])(self._normalizeShortVersion(rightVersion).split('.'))
        max_len = max(len(left_parts), len(right_parts))
        left_parts.extend([
            0] * (max_len - len(left_parts)))
        right_parts.extend([
            0] * (max_len - len(right_parts)))
        if left_parts > right_parts:
            return 1
        if None < right_parts:
            return -1

    
    def _dllCandidates(self):
