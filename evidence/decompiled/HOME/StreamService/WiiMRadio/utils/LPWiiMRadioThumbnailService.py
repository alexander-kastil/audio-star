# Source Generated with Decompyle++
# File: LPWiiMRadioThumbnailService.pyc (Python 3.9)

'''
WiiMRadio favicon 缩略图服务 adapter。
'''
import threading
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework.LPImageService.LPGlobalImageScheduler import LPGlobalImageScheduler
from LPClientFramework.LPImageService.LPGlobalQmlImageService import LPGlobalQmlImageService
from LPClientFramework.LPImageService.LPImageProfiles import WIIMRADIO_FAVICON_PROFILE

class LPWiiMRadioThumbnailService(QObject):
    thumbnailReady = pyqtSignal(str, str)
    CACHE_VERSION = 'v3'
    THUMBNAIL_SIZE = 155
    CACHE_TTL_SECONDS = 86400
    FAILURE_RETRY_SECONDS = 60
    _instance: Optional['LPWiiMRadioThumbnailService'] = None
    _instance_lock = threading.Lock()
    
    def __init__(self = None, parent = None):
        '''
        初始化 WiiMRadio 图片服务 adapter。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._profile = WIIMRADIO_FAVICON_PROFILE
        self._image_service = LPGlobalQmlImageService.instance()
        self._image_service.thumbnailReady.connect(self._handleGlobalThumbnailReady)

    
    def instance(cls = None):
        '''
        返回 WiiMRadio 图片服务 adapter 单例。

        :param: 无。
        :return: adapter 单例。
        '''
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            None(None, None, None)
        with None:
            if not None:
                pass
        return cls._instance

    instance = None(instance)
    
    def ensureThumbnail(self = None, url = None, priority = None):
        '''
        确保 favicon 缩略图可用。

        :param url: favicon URL。
        :param priority: 调度优先级。
        :return: 已缓存时返回本地 file URL；未就绪时返回空字符串。
        '''
        return self._image_service.ensureThumbnail(url, self._profile, priority, 'wiimradio', **('priority', 'ownerKey'))

    
    def thumbnailPath(self = None, url = None):
        '''
        查询 favicon 当前已缓存的缩略图路径。

        :param url: favicon URL。
        :return: 本地 file URL；未命中时返回空字符串。
        '''
        return self._image_service.thumbnailPath(url, self._profile)

    
    def _handleGlobalThumbnailReady(self = None, url = None, thumbnailPath = None, profile = {
        'url': str,
        'thumbnailPath': str,
        'profile': str,
        'return': None }):
        '''
        将全局三参数 ready 信号转换为 WiiMRadio 旧双参数信号。

        :param url: 原始图片 URL。
        :param thumbnailPath: 本地 file URL。
        :param profile: 图片 profile 名称。
        :return: None。
        '''
        if not profile:
            pass
        if str('').strip() != self._profile:
            return None
        None.thumbnailReady.emit(url, thumbnailPath)

    __classcell__ = None

