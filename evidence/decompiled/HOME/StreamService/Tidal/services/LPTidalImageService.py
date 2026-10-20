# Source Generated with Decompyle++
# File: LPTidalImageService.pyc (Python 3.9)

'''
TIDAL 图片缓存服务 adapter。
'''
import hashlib
import logging
import threading
from pathlib import Path
from typing import Optional, Set
from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from LPClientFramework.LPImageService.LPGlobalQmlImageService import LPGlobalQmlImageService
from LPClientFramework.LPImageService.LPImageProfiles import TIDAL_COVER_320_PROFILE, imageProfile
logger = logging.getLogger('linkplay')

class LPTidalImageService(QObject):
    thumbnailReady = pyqtSignal(str, str)
    thumbnailFailed = pyqtSignal(str, object)
    THUMBNAIL_SIZE = 320
    CACHE_TTL_SECONDS = 604800
    FAILURE_RETRY_SECONDS = 60
    _instance: Optional['LPTidalImageService'] = None
    _instance_lock = threading.Lock()
    
    def __init__(self = None, parent = None):
        '''
        初始化 TIDAL 图片服务 adapter。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._profile = TIDAL_COVER_320_PROFILE
        cacheCoverDir = cacheCoverDir
        import LPClientFramework.LPUtility
        self._cache_dir = Path(cacheCoverDir)
        self._cache_dir.mkdir(True, True, **('parents', 'exist_ok'))
        self._cancelled = set()
        self._lock = threading.RLock()
        self._owner_generation = 0
        self._known_owner_keys = set()
        self._image_service = LPGlobalQmlImageService.instance()
        self._image_service.thumbnailReady.connect(self._handleGlobalThumbnailReady)
        self._image_service.thumbnailFailed.connect(self._handleGlobalThumbnailFailed)

    
    def instance(cls = None):
        '''
        返回 TIDAL 图片服务 adapter 单例。

        :return: 图片服务单例。
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
    
    def cancelPendingAndClear(self = None):
        '''
        取消当前 TIDAL 会话的在途图片请求并清空失败退避。

        :return: None。
        '''
        with self._lock:
            old_owner = self._owner_key_locked()
            old_known_owners = set(self._known_owner_keys)
            self._owner_generation += 1
            self._known_owner_keys.clear()
            self._cancelled.clear()
            self(None, None, None)
        with None:
            if not None:
                pass
        for owner_key in sorted(old_known_owners | {
            old_owner}):
            self._image_service.cancelOwner(owner_key)
        self._image_service.clearFailure(self._profile, **('profile',))

    
    def cancelOwner(self = None, ownerKey = None):
        '''
        失效指定 TIDAL 页面或 tab 的图片 owner。

        :param ownerKey: 页面或 tab owner 后缀。
        :return: None。
        '''
        with self._lock:
            owner = self._owner_key_locked(ownerKey)
            self._known_owner_keys.add(owner)
            None(None, None, None)
        with None:
            if not None:
                pass
        self._image_service.cancelOwner(owner)

    
    def ensureThumbnail(self = None, imageUrl = None, priority = None, ownerKey = ('preload', '')):
        '''
        确保指定 TIDAL 图片 URL 的本地缩略图可用。

        :param imageUrl: 远端或本地图片 URL。
        :param priority: 调度优先级。
        :param ownerKey: 页面或 tab owner 后缀。
        :return: 已缓存时返回本地 file URL；未就绪时返回空字符串。
        '''
        with self._lock:
            owner = self._owner_key_locked(ownerKey)
            self._known_owner_keys.add(owner)
            None(None, None, None)
        with None:
            if not None:
                pass
        return self._image_service.ensureThumbnail(imageUrl, self._profile, priority, owner, **('priority', 'ownerKey'))

    
    def thumbnailPath(self = None, imageUrl = None):
        '''
        返回指定图片 URL 当前可用的本地缩略图路径。

        :param imageUrl: 远端或本地图片 URL。
        :return: 本地 file URL；未命中时返回空字符串。
        '''
        return self._image_service.thumbnailPath(imageUrl, self._profile)

    
    def requestThumbnail(self = None, itemId = None, imageUrl = None):
        '''
        请求图片缩略图，命中缓存时立即发出旧双参数 ready 信号。

        :param itemId: 条目 ID。
        :param imageUrl: 图片 URL。
        :return: None。
        '''
        if not itemId:
            pass
        key = str('').strip()
        if not imageUrl:
            pass
        url = str('').strip()
        if not key or url:
            return None
        path = None.ensureThumbnail(url, 'visible', **('priority',))
        if path:
            self.thumbnailReady.emit(url, path)

    
    def cancelRequest(self = None, itemId = None):
        '''
        记录指定条目取消请求，保留旧接口兼容。

        :param itemId: 条目 ID。
        :return: None。
        '''
        if not itemId:
            pass
        key = str('').strip()
        if not key:
            return None
        with None._lock:
            self._cancelled.add(key)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _resolve_cache_path(self = None, itemId = None, imageUrl = None):
        '''
        计算 TIDAL 图片缓存文件路径。

        :param itemId: 条目 ID。
        :param imageUrl: 图片 URL。
        :return: 缓存文件路径。
        '''
        _ = itemId
        return self._cache_file_path(imageUrl)

    
    def _cache_file_path(self = None, imageUrl = None):
        '''
        根据图片 URL 计算新全局服务的 TIDAL 缩略图缓存路径。

        :param imageUrl: 图片 URL。
        :return: 缓存文件路径。
        '''
        profile = imageProfile(self._profile)
        if not imageUrl:
            pass
        cache_id = hashlib.md5(str('').strip().encode('utf-8')).hexdigest()
        return self._cache_dir / f'''{profile.name}_{cache_id}_{profile.size}.png'''

    
    def _file_url(self = None, localPath = None):
        '''
        将本地路径转换为 QML 可消费的 encoded file URL。

        :param localPath: 本地路径。
        :return: file URL 字符串。
        '''
        return bytes(QUrl.fromLocalFile(str(localPath)).toEncoded()).decode('utf-8')

    
    def _owner_key_locked(self = None, ownerKey = None):
        '''
        返回当前 TIDAL 图片 owner key，调用方需持锁。

        :param ownerKey: 页面或 tab owner 后缀。
        :return: owner key。
        '''
        if not ownerKey:
            pass
        normalized_owner = str('').strip()
        if normalized_owner.startswith('tidal:'):
            return normalized_owner
        session_owner = f'''{self._owner_generation}'''
        if not normalized_owner:
            return session_owner
        return f'''{None}:{normalized_owner}'''

    
    def _handleGlobalThumbnailReady(self = None, imageUrl = None, imagePath = None, profile = {
        'imageUrl': str,
        'imagePath': str,
        'profile': str,
        'return': None }):
        '''
        将全局三参数 ready 信号转换为 TIDAL 旧双参数信号。

        :param imageUrl: 图片 URL。
        :param imagePath: 本地 file URL。
        :param profile: 图片 profile 名称。
        :return: None。
        '''
        if not profile:
            pass
        if str('').strip() != self._profile:
            return None
        None.thumbnailReady.emit(imageUrl, imagePath)

    
    def _handleGlobalThumbnailFailed(self = None, imageUrl = None, profile = None, error = {
        'imageUrl': str,
        'profile': str,
        'error': object,
        'return': None }):
        '''
        将全局三参数 failed 信号转换为 TIDAL 旧双参数信号。

        :param imageUrl: 图片 URL。
        :param profile: 图片 profile 名称。
        :param error: 异常对象。
        :return: None。
        '''
        if not profile:
            pass
        if str('').strip() != self._profile:
            return None
        None.debug('[TidalImageService][CacheTrace] failure profile=%s url=%s error=%s', profile, imageUrl, error)
        self.thumbnailFailed.emit(imageUrl, error)

    __classcell__ = None

