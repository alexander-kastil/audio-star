# Source Generated with Decompyle++
# File: LPUtility.pyc (Python 3.9)

import base64
import time
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmapCache, QPixmap, QPainter, QColor, QFont, QPen, QBitmap, QImage, QPainterPath
from PIL import Image, ImageFilter
import io
from socketserver import ThreadingMixIn
from http.server import HTTPServer
from PyQt6.QtCore import QStandardPaths, QRunnable, pyqtSignal, QObject, QLocale, Qt, QSettings, QBuffer, QByteArray, QIODevice, QUrl
from pathlib import Path
import json
import os
import uuid
import sys
import logging
from urllib3.exceptions import InsecureRequestWarning
import requests
from requests_futures.sessions import FuturesSession
import threading
import hashlib
from mediafile import MediaFile
import codecs
import platform
import subprocess
import LPGlobalUI
from LPClientFramework import LPPublicDefine
from LPClientFramework.CacheLog import startCacheLog
from LPClientFramework.util.aes import AESCipher
from LPClientFramework.LPSMBService import LPSMBService

def currentLan():
    retLan = 'en'
    supportLan = [
        'en',
        'zh']
    currentLocale = QLocale()
    tempLan = currentLocale.languageToCode(currentLocale.language())
    tempScript = currentLocale.scriptToCode(currentLocale.script())
    if tempLan in supportLan:
        retLan = tempLan
    return {
        'lan': retLan,
        'script': tempScript }


def appLocalDataPath():
    pass
# WARNING: Decompyle incomplete

with codecs.open('%s/config.json' % appLocalDataPath(), 'r', 'utf-8', 'ignore', **('errors',)) as configFile:
    configJson = json.loads(configFile.read())
    appVersion = configJson['version']
    appRelease = configJson['release']
    None(None, None, None)
with None:
    if not None:
        pass
bundleId = 'com.linkplay.wiimhome'
validFileType = [
    'm3u',
    'm3u8',
    'asx',
    'pls',
    'smil',
    'nsc',
    'mp3',
    'aac',
    'alac',
    'ape',
    'flac',
    'wav',
    'wma',
    'ogg',
    'm4a',
    'aiff',
    'aif']
musicFileType = [
    'mp3',
    'aac',
    'alac',
    'ape',
    'flac',
    'wav',
    'wma',
    'ogg',
    'm4a',
    'aiff',
    'aif']
specialSource = [
    LPPublicDefine.MEDIATYPE_LINEIN,
    LPPublicDefine.MEDIATYPE_BLUETOOTH,
    LPPublicDefine.MEDIATYPE_EXTERNAL_USB,
    LPPublicDefine.MEDIATYPE_USB_DAC,
    LPPublicDefine.MEDIATYPE_EXTERNAL_TF,
    LPPublicDefine.MEDIATYPE_OPTICAL,
    LPPublicDefine.MEDIATYPE_OPTICAL2,
    LPPublicDefine.MEDIATYPE_AIRPLAY,
    LPPublicDefine.MEDIATYPE_CO_AXIAL,
    LPPublicDefine.MEDIATYPE_CO_AXIAL2,
    LPPublicDefine.MEDIATYPE_HDMI,
    LPPublicDefine.MEDIATYPE_PHONO,
    LPPublicDefine.MEDIATYPE_AUXIN]
mediaServerPort = 22345
upnpServerPort = 22346
oauthServerPort = 22347
upnpServer = None
mediaServer = None
oauthServer = None
cacheDir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)) / bundleId
SSCacheDir = cacheDir / 'SS'
logDir = cacheDir / 'log'
logger = logging.getLogger('linkplay')
if not os.path.exists(logDir):
    os.makedirs(logDir, True, **('exist_ok',))
startCacheLog(logDir, getattr(sys, 'frozen', False))

def logAcctBifurcate(device, note, cond = (None,)):
    """诊断工具：打印账号刷新链路中 LPDevice 对象与条件的身份信息。

    用于排查 app 启动阶段默认选中设备不刷新侧边栏账号的根因，重点验证是否存在
    “同 UUID、不同 Python 对象 / 不同 Condition” 的分叉，使首次等待线程错过
    capability 完成通知。该函数仅为诊断用途，定位完成后应整体移除。

    参数:
        device (LPDevice | None): 相关设备对象，可为 None（仅打印 note）。
        note (str): 触发点说明，例如 'device.__init__'、'cap-done.before-notify'、
            'acctThread.enter'。
        cond (threading.Condition | None): 显式指定的条件对象；为 None 时取
            device.streamServiceCapCondition。仅当 device 不为 None 时有效。

    返回:
        None。
    """
    return None
    cond_obj = cond if cond is not None else getattr(device, 'streamServiceCapCondition', None)
    logger.info('[acct-bifurcate] note=%s id(device)=%s id(cond)=%s uuid=%s ip=%s ver=%s thread=%s', note, id(device), id(cond_obj) if cond_obj is not None else None, getattr(device, 'uuid', None), getattr(device, 'ip', None), getattr(device, 'streamServiceVersion', None), threading.current_thread().name)


class LPAsyncTaskFinishSigal(QObject):
    finish = pyqtSignal(object)


class LPAsyncTask(QRunnable):
    
    def __init__(self = None, workMethod = None, *args, **kwargs):
        super(LPAsyncTask, self).__init__()
        self.signal = LPAsyncTaskFinishSigal()
        self.workMethod = workMethod
        self.args = args
        self.kwargs = kwargs

    
    def run(self):
        pass
    # WARNING: Decompyle incomplete

    __classcell__ = None

from LPClientFramework.util.LPNetworkUtility import LPNetworkUtility, LPWindowsNetworkInfoReader, LPWindowsWlanReader, AF_INET, IF_TYPE_ETHERNET_CSMACD, IF_TYPE_IEEE80211

def fetchNetworkInfo(log = (False,)):
    '''获取当前网络信息（网关 IP、接口名、子网掩码、本机 IP）。

    参数:
        log (bool): 是否打印调试日志。
    返回:
        dict: 包含 gateway / interface / netmask / localIP 的字典；
            获取失败时返回固定字段的空值字典。
    '''
    return LPNetworkUtility.fetchNetworkInfo(log)


def fetchNetworkType(log = (False,)):
    '''判断当前默认接口的网络类型。

    参数:
        log (bool): 是否打印调试日志。
    返回:
        str | None: "wifi" / "eth"；无法判定时返回 None。
    '''
    return LPNetworkUtility.fetchNetworkType(log)


def getMacosGateway():
    '''读取 macOS 的 IPv4 默认网关。

    参数:
        无。
    返回:
        str | None: 网关 IP；读取失败时返回 None。
    '''
    return LPNetworkUtility.getMacosGateway()


def currentSSID(currentInterfaceIsWifi, log = (True, False)):
    '''获取当前 Wi-Fi 的 SSID。

    参数:
        currentInterfaceIsWifi (bool): True 则只有当当前 interface 为 wifi 时才返回信息；
            否则只要 interface 里有 wifi 就返回。
        log (bool): 是否输出调试日志。
    返回:
        str | None: 当前 Wi-Fi SSID；未连接或获取失败时返回 None。
    '''
    return LPNetworkUtility.currentSSID(currentInterfaceIsWifi, log)


def currentBSSID(currentInterfaceIsWifi, log = (True, False)):
    '''获取当前 Wi-Fi 热点的 BSSID（埋点诊断用的同网比较依据）。

    参数:
        currentInterfaceIsWifi (bool): True 时仅当前接口为 Wi-Fi 才返回。
        log (bool): 是否输出调试日志。
    返回:
        str | None: BSSID 字符串（如 aa:bb:cc:dd:ee:ff）；获取失败返回 None。
    '''
    return LPNetworkUtility.currentBSSID(currentInterfaceIsWifi, log)


def ssidToHexString(ssid):
    '''把 SSID 明文转换为 UTF-8 字节的大写十六进制串。

    参数:
        ssid (str): SSID 明文。
    返回:
        str: 大写 hex 字符串；入参为空时返回空串。
    '''
    return LPNetworkUtility.ssidToHexString(ssid)


def invalidateNetworkCaches():
    '''使网络信息与 SSID/BSSID 缓存立即失效，强制下次调用读取最新系统状态。

    参数:
        无。
    返回:
        None。
    '''
    return LPNetworkUtility.invalidateNetworkCaches()


def icmpPingHost(ip, timeout = (3,)):
    '''对指定主机做一次 ICMP Ping 探测（设备发现诊断的 ping_ok 判定位）。

    参数:
        ip (str): 目标 IPv4 地址。
        timeout (int): 超时秒数。
    返回:
        bool: 收到回包返回 True；超时或异常返回 False。
    '''
    return LPNetworkUtility.icmpPingHost(ip, timeout)


def tcpProbeHost(ip, port, timeout = (443, 3)):
    '''对指定主机端口做 TCP 连通探测（设备发现诊断的 tcp443_ok 判定位）。

    参数:
        ip (str): 目标 IPv4 地址。
        port (int): 目标端口，默认 443。
        timeout (int): 连接超时秒数。
    返回:
        bool: 连接成功返回 True；超时或异常返回 False。
    '''
    return LPNetworkUtility.tcpProbeHost(ip, port, timeout)

cacheCoverDir = cacheDir / 'cover'
userDataDir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)) / bundleId
logger.debug('AppVersion: %s, Builddate: %s' % (appVersion, appRelease))
logger.debug('cacheDir: %s' % cacheCoverDir)
logger.debug('userDir: %s' % userDataDir)
if not os.path.exists(userDataDir):
    os.mkdir(str(userDataDir))
if not os.path.exists(cacheCoverDir):
    os.makedirs(cacheCoverDir, True, **('exist_ok',))
configPath = userDataDir / 'wiimhome-userconfig.json'
userConfigLock = threading.RLock()
myMusicDirArrayLock = threading.RLock()

def _defaultMyMusicDirArray():
    '''
    获取用户配置的默认本地音乐目录列表。

    参数:
        无
    返回:
        list[str]: 默认本地音乐目录数组。
    '''
    return [
        str(Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)))]


def _defaultUserConfig():
    '''
    构造默认用户配置字典。

    参数:
        无
    返回:
        dict: 默认用户配置内容。
    '''
    return {
        'mymusic-dir': _defaultMyMusicDirArray() }


def _normalizeMyMusicDirConfig(configDict):
    '''
    规范化用户配置中的本地音乐目录字段。

    参数:
        configDict (dict | None): 原始用户配置字典。
    返回:
        tuple[dict, bool]: 规范化后的配置字典，以及是否发生了修正。
    '''
    if not isinstance(configDict, dict):
        configDict = { }
    myMusicDirValue = configDict.get('mymusic-dir', None)
    if isinstance(myMusicDirValue, list):
        return (configDict, False)
    configDict['mymusic-dir'] = None()
    return (configDict, True)


def _saveUserConfigSafely(configDict):
    '''
    安全写入用户配置文件。

    参数:
        configDict (dict): 需要保存的用户配置字典。
    返回:
        dict: 实际写入后的用户配置字典。
    '''
    (configDict, _) = _normalizeMyMusicDirConfig(configDict)
    with userConfigLock:
        with open(configPath, 'w', 'utf-8', **('encoding',)) as file:
            file.write(json.dumps(configDict))
            None(None, None, None)
        with None:
            if not None:
                pass
        None(None, None, None)
    with None:
        if not None:
            pass
    return configDict


def _loadUserConfigSafely():
    '''
    安全读取用户配置文件；遇到空文件、损坏文件或缺失文件时自动回退并重建。

    参数:
        无
    返回:
        dict: 用户配置字典。
    '''
    defaultConfig = _defaultUserConfig()
# WARNING: Decompyle incomplete

myMusicDirArray = _loadUserConfigSafely().get('mymusic-dir', _defaultMyMusicDirArray())

def getMyMusicDirSnapshot():
    '''
    获取当前本地音乐目录列表的线程安全快照。

    参数:
        无
    返回:
        list[str]: 当前本地音乐目录数组副本。
    '''
    with myMusicDirArrayLock:
        None(None, None, None)
        return list(myMusicDirArray)
        with None:
            if not None:
                pass


def myMusicDirCount():
    '''
    获取当前本地音乐目录数量。

    参数:
        无
    返回:
        int: 当前目录数量。
    '''
    with myMusicDirArrayLock:
        None(None, None, None)
        return len(myMusicDirArray)
        with None:
            if not None:
                pass


def findOwningMyMusicDir(filePath):
