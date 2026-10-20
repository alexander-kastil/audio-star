# Source Generated with Decompyle++
# File: LPGlobalQmlImageService.pyc (Python 3.9)

'''
全局 QML 图片下载、缩略图和缓存服务。
'''
import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple
import requests
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QImage
from LPClientFramework.LPImageService.LPGlobalImageScheduler import LPGlobalImageScheduler
from LPClientFramework.LPImageService.LPImageProfiles import LPImageProfile, imageProfile
from LPClientFramework.LPSMBService import LPSMBService
logger = logging.getLogger('linkplay')

class LPGlobalQmlImageService(QObject):
    thumbnailReady = pyqtSignal(str, str, str)
    thumbnailFailed = pyqtSignal(str, str, object)
    FAILURE_RETRY_SECONDS = 60
    _instance: Optional['LPGlobalQmlImageService'] = None
    _instance_lock = threading.Lock()
    
    def __init__(self = None, parent = None, scheduler = None, cacheDir = None):
        '''
        初始化全局 QML 图片服务。

        :param parent: 父级 QObject。
        :param scheduler: 图片调度器，测试可注入。
        :param cacheDir: 缓存目录，测试可注入。
        :return: None。
        '''
        super().__init__(parent)
        if cacheDir is None:
            cacheCoverDir = cacheCoverDir
            import LPClientFramework.LPUtility
            self._cache_dir = Path(cacheCoverDir)
        else:
            self._cache_dir = Path(cacheDir)
        self._cache_dir.mkdir(True, True, **('parents', 'exist_ok'))
        self._scheduler = scheduler if scheduler is not None else LPGlobalImageScheduler.instance()
        self._lock = threading.RLock()
        self._pending_keys = set()
        self._pending_owners = { }
        self._pending_phases = { }
        self._failure_expire_at = { }
        self._owner_generations = { }
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_failures = 0
        self._failure_backoff_hits = 0

    
    def instance(cls = None):
        '''
        返回全局 QML 图片服务单例。

        :param: 无。
        :return: 服务单例。
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
    
    def ensureThumbnail(self = None, url = None, profile = None, priority = (LPGlobalImageScheduler.PRIORITY_PRELOAD, ''), ownerKey = {
        'url': str,
        'profile': str,
        'priority': str,
        'ownerKey': str,
        'return': str }):
        '''
        确保指定 URL 和 profile 的本地缩略图可用。

        :param url: 远程或本地图片 URL。
        :param profile: 图片 profile 名称。
        :param priority: 调度优先级。
        :param ownerKey: 页面、状态或账号 owner 标识。
        :return: 已缓存时返回本地 file URL；未就绪时返回空字符串。
        '''
        normalized_url = self._normalize_url(url)
        if not normalized_url:
            return ''
        if not None._is_remote_url(normalized_url):
            return normalized_url
        image_profile = None(profile)
        local_path = self._cache_file_path(normalized_url, image_profile)
        has_cached = local_path.exists()
        if has_cached:
            pass
        is_expired = self._is_expired(local_path, image_profile)
        if not has_cached and is_expired:
            with self._lock:
                self._cache_hits += 1
                self(None, None, None)
            with None:
                if not None:
                    pass
            return self._file_url(local_path)
        with self._lock:
            self._cache_misses += 1
            self(None, None, None)
        with None:
            if not None:
                pass
        self._schedule_fetch(normalized_url, image_profile, priority, ownerKey)
        if has_cached:
            return self._file_url(local_path)

    
    def thumbnailPath(self = None, url = None, profile = None):
        '''
        查询当前已缓存的缩略图路径，不触发下载。

        :param url: 远程或本地图片 URL。
        :param profile: 图片 profile 名称。
        :return: 本地 file URL；未命中时返回空字符串。
        '''
        normalized_url = self._normalize_url(url)
        if not normalized_url:
            return ''
        if not None._is_remote_url(normalized_url):
            return normalized_url
        image_profile = None(profile)
        local_path = self._cache_file_path(normalized_url, image_profile)
        if not local_path.exists():
            return ''
        return None._file_url(local_path)

    
    def cancelOwner(self = None, ownerKey = None):
        '''
        取消指定 owner 的未开始订阅，并让旧 generation 的在途结果失效。

        :param ownerKey: owner 标识。
        :return: None。
        '''
        if not ownerKey:
            pass
        normalized_owner = str('').strip()
        if not normalized_owner:
            return None
        with None._lock:
            self._owner_generations[normalized_owner] = self._owner_generation_locked(normalized_owner) + 1
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def clearFailure(self = None, url = None, profile = None):
        '''
        清除失败退避记录。

        :param url: 指定 URL，空字符串表示不限 URL。
        :param profile: 指定 profile，空字符串表示不限 profile。
        :return: None。
        '''
        normalized_url = self._normalize_url(url)
        if not profile:
            pass
        normalized_profile = str('').strip()
        with self._lock:
            if not normalized_url and normalized_profile:
                self._failure_expire_at.clear()
            None(None, None, None)
            return None
            keys = (lambda .0 = None: [ key for key in .0 if key[1] == normalized_url ])(self._failure_expire_at)
            for key in keys:
                self._failure_expire_at.pop(key, None)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def stats(self = None):
        '''
        返回服务调试统计。

        :param: 无。
        :return: 统计字典。
        '''
        with self._lock:
            service_stats = {
                'pending': len(self._pending_keys),
                'cacheHit': self._cache_hits,
                'cacheMiss': self._cache_misses,
                'cacheFail': self._cache_failures,
                'failureBackoffHit': self._failure_backoff_hits }
            None(None, None, None)
        with None:
            if not None:
                pass
        service_stats['scheduler'] = self._scheduler.stats()
        return service_stats

    
    def _schedule_fetch(self, url = None, profile = None, priority = None, ownerKey = {
        'url': str,
        'profile': LPImageProfile,
        'priority': str,
        'ownerKey': str,
        'return': None }):
        '''
        安排指定图片的下载和缩略图生成任务。

        :param url: 远端图片 URL。
        :param profile: 图片 profile。
        :param priority: 调度优先级。
        :param ownerKey: owner 标识。
        :return: None。
        '''
        if not ownerKey:
            pass
        owner = str('').strip()
        with self._lock:
            self._purge_expired_failures_locked()
            request_key = self._request_key(url, profile.name)
            failure_expire_at = float(self._failure_expire_at.get(request_key, 0))
            if failure_expire_at > time.time():
                self._failure_backoff_hits += 1
            None(None, None, None)
            return None
            owner_generation = self._owner_generation_locked(owner) if owner else 0
            owner_map = self._pending_owners.setdefault(request_key, { })
            owner_map[owner] = owner_generation
            if request_key in self._pending_keys:
                should_schedule = False
                should_promote_download = self._pending_phases.get(request_key, '') == 'download'
            else:
                self._pending_keys.add(request_key)
                self._pending_phases[request_key] = 'download'
                should_schedule = True
                should_promote_download = False
            None(None, None, None)
        with None:
            if not None:
                pass
        job_key = self._job_key(url, profile.name)
        if not should_schedule:
            if not should_promote_download:
                return None
            None(None, (lambda targetUrl = None: self._download_raw_image(targetUrl)), None, priority, **('jobKey', 'task', 'callback', 'priority'))
            return None
        None(None, None, (lambda result = None, targetUrl = None, targetProfile = None, taskPriority = None: self._handle_download_finished(targetUrl, targetProfile, result, taskPriority)), priority, **('jobKey', 'task', 'callback', 'priority'))

    
    def _download_raw_image(self = None, url = None):
        '''
        下载远端原始图片字节。

        :param url: 远端图片 URL。
        :return: 原始图片字节。
        '''
        response = None
        status_code = 0
    # WARNING: Decompyle incomplete

    
    def _handle_download_finished(self, url = None, profile = None, result = None, priority = {
        'url': str,
        'profile': LPImageProfile,
        'result': Any,
        'priority': str,
        'return': None }):
        '''
        处理下载完成，并成功时提交解码任务。

        :param url: 远端图片 URL。
        :param profile: 图片 profile。
        :param result: 下载结果。
        :param priority: 调度优先级。
        :return: None。
        '''
        if isinstance(result, Exception):
            self._mark_failure(url, profile.name, result)
            return None
        raw_data = result if None(result, (bytes, bytearray)) else b''
        if not raw_data:
            self._mark_failure(url, profile.name, ValueError('empty_image_bytes'))
            return None
        with None._lock:
            self._pending_phases[self._request_key(url, profile.name)] = 'decode'
            None(None, None, None)
        with None:
            if not None:
                pass
        None(None, None, (lambda decodeResult = None, targetUrl = None, targetProfile = None: self._handle_decode_finished(targetUrl, targetProfile.name, decodeResult)), priority, **('jobKey', 'task', 'callback', 'priority'))

    
    def _decode_and_store_thumbnail(self = None, url = None, profile = None, rawData = {
        'url': str,
        'profile': LPImageProfile,
        'rawData': bytes,
        'return': str }):
        '''
        解码原图并写入指定 profile 的缩略图缓存。

        :param url: 远端图片 URL。
        :param profile: 图片 profile。
        :param rawData: 原始图片字节。
        :return: 本地 file URL。
        '''
        image = QImage()
        if not image.loadFromData(rawData):
            raise ValueError('image_load_failed')
        if profile.saveOriginal:
            original_path = self._original_cache_file_path(url, profile.name)
            original_temp_path = Path(f'''{original_path}.tmp''')
            with open(original_temp_path, 'wb') as original_file:
                original_file.write(rawData)
                None(None, None, None)
            with None:
                if not None:
                    pass
            original_temp_path.replace(original_path)
        safe_image = image.convertToFormat(QImage.Format.Format_ARGB32)
        thumbnail_image = safe_image.scaled(profile.size, profile.size, profile.aspectMode, Qt.TransformationMode.SmoothTransformation)
        local_path = self._cache_file_path(url, profile)
        temp_path = Path(f'''{local_path}.tmp''')
        if not thumbnail_image.save(str(temp_path), 'PNG'):
            raise ValueError('image_save_failed')
        temp_path.replace(local_path)
        return self._file_url(local_path)

    
    def _handle_decode_finished(self = None, url = None, profile = None, result = {
        'url': str,
        'profile': str,
        'result': Any,
        'return': None }):
        '''
        处理缩略图生成结束。

        :param url: 远端图片 URL。
        :param profile: 图片 profile 名称。
        :param result: 解码结果。
        :return: None。
        '''
        if isinstance(result, Exception):
            self._mark_failure(url, profile, result)
            return None
        if not result:
            pass
        thumbnail_path = None('').strip()
        if not thumbnail_path:
            self._mark_failure(url, profile, ValueError('empty_thumbnail_path'))
            return None
        request_key = None._request_key(url, profile)
        with self._lock:
            self._pending_keys.discard(request_key)
            self._pending_phases.pop(request_key, None)
            owner_map = self._pending_owners.pop(request_key, { })
            has_valid_owner = self._has_valid_owner_locked(owner_map)
            None(None, None, None)
        with None:
            if not None:
                pass
        if not has_valid_owner:
            return None
        None.thumbnailReady.emit(url, thumbnail_path, profile)

    
    def _mark_failure(self = None, url = None, profile = None, error = {
        'url': str,
        'profile': str,
        'error': Exception,
        'return': None }):
        '''
        记录失败退避并发出失败信号。

        :param url: 远端图片 URL。
        :param profile: 图片 profile 名称。
        :param error: 异常对象。
        :return: None。
        '''
        request_key = self._request_key(url, profile)
        with self._lock:
            self._failure_expire_at[request_key] = time.time() + self.FAILURE_RETRY_SECONDS
            self._pending_keys.discard(request_key)
            self._pending_phases.pop(request_key, None)
            owner_map = self._pending_owners.pop(request_key, { })
            has_valid_owner = self._has_valid_owner_locked(owner_map)
            self._cache_failures += 1
            self(None, None, None)
        with None:
            if not None:
                pass
        logger.debug(f'''[GlobalImageService] thumbnail failed profile={profile} url={url}, error={error}''')
        if has_valid_owner:
            self.thumbnailFailed.emit(url, profile, error)

    
    def _cache_file_path(self = None, url = None, profile = None):
        '''
        计算缩略图缓存路径。

        :param url: 远端图片 URL。
        :param profile: 图片 profile。
        :return: 缓存文件路径。
        '''
        cache_id = hashlib.md5(self._normalize_url(url).encode('utf-8')).hexdigest()
        if profile.useSharedUrlCacheLayout:
            return self._cache_dir / f'''{cache_id}_{profile.size}'''
        return None._cache_dir / f'''{profile.name}_{cache_id}_{profile.size}.png'''

    
    def _original_cache_file_path(self = None, url = None, profile = None):
        '''
        计算原图缓存路径。

        :param url: 远端图片 URL。
        :param profile: 图片 profile 名称。
        :return: 原图缓存文件路径。
        '''
        cache_id = hashlib.md5(self._normalize_url(url).encode('utf-8')).hexdigest()
        image_profile = imageProfile(profile)
        if image_profile.useSharedUrlCacheLayout:
            return self._cache_dir / cache_id
        return None._cache_dir / f'''{profile}_{cache_id}_original'''

    
    def _is_expired(self = None, localPath = None, profile = None):
        '''
        判断本地缓存是否过期。

        :param localPath: 本地缓存路径。
        :param profile: 图片 profile。
        :return: 已过期返回 True。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _file_url(self = None, localPath = None):
        '''
        转换为 QML 可消费的 encoded file URL。

        :param localPath: 本地文件路径。
        :return: encoded file URL。
        '''
        return bytes(QUrl.fromLocalFile(str(localPath)).toEncoded()).decode('utf-8')

    
    def _normalize_url(self = None, url = None):
        '''
        归一化 URL 字符串。

        :param url: 原始 URL。
        :return: 去除空白后的 URL。
        '''
        if not url:
            pass
        return str('').strip()

    
    def _is_remote_url(self = None, url = None):
        '''
        判断 URL 是否为 HTTP(S) 远端地址。

        :param url: 待判断 URL。
        :return: 远端地址返回 True。
        '''
        normalized = self._normalize_url(url)
        if not normalized.startswith('http://') and normalized.startswith('https://'):
            pass
        return normalized.startswith('smb://')

    
    def _request_key(self = None, url = None, profile = None):
        '''
        构建内部请求 key。

        :param url: 远端图片 URL。
        :param profile: 图片 profile 名称。
        :return: profile 和 URL 组成的 key。
        '''
        if not profile:
            pass
        return (str('').strip(), self._normalize_url(url))

    
    def _job_key(self = None, url = None, profile = None):
        '''
        构建调度器任务 key。

        :param url: 远端图片 URL。
        :param profile: 图片 profile 名称。
        :return: 字符串任务 key。
        '''
        (profile_name, normalized_url) = self._request_key(url, profile)
        return f'''{profile_name}::{normalized_url}'''

    
    def _owner_generation_locked(self = None, ownerKey = None):
        '''
        返回 owner 当前 generation，调用方需持锁。

        :param ownerKey: owner 标识。
        :return: 当前 generation。
        '''
        if not ownerKey:
            pass
        owner = str('').strip()
        if not owner:
            return 0
        return None(self._owner_generations.get(owner, 0))

    
    def _has_valid_owner_locked(self = None, ownerMap = None):
        '''
        判断请求是否仍有有效 owner，调用方需持锁。

        :param ownerMap: owner 与请求 generation 的映射。
        :return: 有有效 owner 或 ownerless 订阅时返回 True。
        '''
        if not ownerMap:
            return True
        if None in ownerMap:
            return True
        for owner, generation in None.items():
            if self._owner_generation_locked(owner) == int(generation):
                return True
            return False

    
    def _purge_expired_failures_locked(self = None):
        '''
        清理已过期失败退避记录，调用方需持锁。

        :param: 无。
        :return: None。
        '''
        now = time.time()
        expired_keys = (lambda .0 = None: [ key for key, expire_at in .0 if expire_at <= now ])(self._failure_expire_at.items())
        for key in expired_keys:
            self._failure_expire_at.pop(key, None)

    
    def _extract_status_code(self = None, error = None, default = None):
        '''
        从请求异常中提取响应码。

        :param error: 异常对象。
        :param default: 默认响应码。
        :return: 响应码。
        '''
        response = getattr(error, 'response', None)
        if response is None:
            if not default:
                pass
            return int(0)
        if not getattr(response, 'status_code', default):
            pass
        :
            response = getattr(error, 'response', None)
            if response is None:
                if not default:
                    pass
                return int(0)
            if not getattr(response, 'status_code', default):
                pass
            
            return int(0)
        return int(0)
    # WARNING: Decompyle incomplete

    __classcell__ = None

