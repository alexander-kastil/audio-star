# Source Generated with Decompyle++
# File: LPTidalDataProvider.pyc (Python 3.9)

'''
TIDAL API 数据提供层。
'''
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import hashlib
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import requests_cache
from PyQt6.QtCore import QObject, QStandardPaths, pyqtSignal
from HOME.StreamService.Tidal.config.LPTidalImageConfig import LPTidalImageSize, buildTidalImageUrl, tidalImageSizeForItemField, tidalNormalizeImageSize
logger = logging.getLogger('linkplay')

class LPTidalDataProvider(QObject):
    '''封装 TIDAL 请求会话、URL 组装和 JSON 响应解析。'''
    DEFAULT_BASE_URL = 'https://api.tidal.com'
    MAX_RESPONSE_CACHE_ENTRIES = 200
    MAX_OPTIONAL_NOT_FOUND_CACHE_ENTRIES = 200
    OPTIONAL_NOT_FOUND_CACHE_SECONDS = 600
    FAILURE_POLICY_REQUIRED = 'required'
    FAILURE_POLICY_OPTIONAL_CONTENT = 'optional_content'
    FAILURE_POLICY_CAPABILITY_PROBE = 'capability_probe'
    INVALID_RESOURCE_IDS = frozenset({
        'artisttoptracks',
        'none',
        'undefined',
        'null',
        '0'})
    MAX_MIX_META_ENTRIES = 500
    _mix_meta_by_id: Dict[(str, Dict[(str, str)])] = { }
    _mix_meta_lock = threading.Lock()
    AGGREGATE_REQUEST_MAX_WORKERS = 5
    _aggregate_request_slots = threading.BoundedSemaphore(AGGREGATE_REQUEST_MAX_WORKERS)
    requestFailed = pyqtSignal(str, object)
    GENRE_IMAGE_FALLBACK: Dict[(str, str)] = {
        'hiphop': '658519e4-8aea-41a8-86f9-e3fbfb31a630',
        'funk': 'b100bf56-2285-48ad-a608-386a7254fe8c',
        'country': 'abc8250d-3fbe-4acc-a69d-29fcd0eb46be',
        'pop': '0239132d-99be-41f4-929d-e27280f7bff1',
        'latin': 'ddb3306e-c787-4468-a791-8efbe746aa8a',
        'dance': '05fd0839-86f1-4517-a211-b9c20f17bfa2',
        'electronic': 'e388fbee-3506-4000-ac4c-c4853f857d0a',
        'rock': '674f6c6c-24db-4baf-8cc9-abcda685f2a3',
        'americana': '7f53e08b-9e07-4813-99cb-237388122847',
        'reggae': '81a066ce-11f9-4685-a739-24dd9be85e5f',
        'classical': 'aad3c1fd-655a-43fa-8c9d-aab439340395',
        'world': 'b0208879-eb06-4669-a5fb-cf1009b46a11',
        'metal': 'd251e1ed-fef2-45a9-98d9-e8d5745f9bdd',
        'blues': 'a20b6923-0b2c-4651-b9ef-f88372355a74',
        'jazz': '04fb4597-c712-49ad-9b71-a5aefbe1d894',
        'film': 'd73a5448-0a5e-4606-9f3e-113d93eaaf05',
        'gospel': '3cce1ba2-2530-4384-8c51-dfdf81868a9d',
        'comedy': '7cf188f8-93df-4119-b624-47dfb4d70e51',
        'kids': '8ee3c6ed-7342-430d-8e5d-20dc72d6ac77',
        'retro': '8173edc1-ca03-4f22-8706-c8800848d331' }
    
    def __init__(self = None, baseUrl = None, parent = None):
        '''
        初始化数据提供层。

        :param baseUrl: TIDAL API 基础地址。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        if not baseUrl:
            pass
        self._base_url = str(self.DEFAULT_BASE_URL).rstrip('/')
        cache_path_dir = self._tidalCacheRoot()
        cache_path_dir.mkdir(True, True, **('parents', 'exist_ok'))
        cache_path = str(cache_path_dir / 'tidal_request_cache')
        self._session = requests_cache.CachedSession(cache_path, 3000, **('cache_name', 'expire_after'))
        self._response_cache = OrderedDict()
        self._response_cache_lock = threading.RLock()
        self._optional_not_found_cache = OrderedDict()
        self._optional_not_found_cache_lock = threading.RLock()
        self._genre_image_map = None

    
    def setBaseUrl(self = None, baseUrl = None):
        '''
        更新 API 基础地址。

        :param baseUrl: TIDAL API 基础地址。
        :return: None。
        '''
        if not baseUrl:
            pass
        self._base_url = str('').rstrip('/')

    
    def isValidResourceId(cls = None, itemId = None):
        '''
        判断条目 ID 是否可安全拼入 TIDAL 资源路径。

        :param itemId: 待校验的资源 ID。
        :return: 非空且非已知占位值返回 True。
        '''
        if not itemId:
            pass
        normalized = str('').strip().lower()
        if normalized:
            pass
        return bool(normalized not in cls.INVALID_RESOURCE_IDS)

    isValidResourceId = None(isValidResourceId)
    
    def hasInvalidResourceIdentifier(cls = None, path = None):
        '''
        判断 API 路径中的资源 ID 是否为已知占位值。

        :param path: TIDAL API 相对路径。
        :return: 含无效 album/artist/playlist/mix/video ID 返回 True。
        '''
        if not path:
            pass
        segments = (lambda .0: [ segment for segment in .0 if segment ])(urlsplit(str('')).path.split('/'))
        for index, segment in enumerate(segments[:-1]):
            if not segment.lower() in frozenset({'albums', 'artists', 'videos', 'playlists', 'mixes'}) and cls.isValidResourceId(segments[index + 1]):
                return True
            return False

    hasInvalidResourceIdentifier = None(hasInvalidResourceIdentifier)
    
    def clearCaches(self = None):
        '''
        清空 HTTP 磁盘缓存和内存 ETag 缓存，登出时调用。

        清空 requests_cache 的磁盘响应缓存和内存层 ETag 缓存，
        避免上一个账号的 API 响应在登出后继续命中。

        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _registerMixMeta(self, itemId, title = None, subtitle = None, imageUrl = None, imagePath = {
        'itemId': str,
        'title': str,
        'subtitle': str,
        'imageUrl': str,
        'imagePath': str,
        'return': None }):
        '''
        登记归一化 mix 卡片的元数据供详情与播放队列复用。

        :param itemId: mix ID。
        :param title: mix 标题。
        :param subtitle: mix 副标题。
        :param imageUrl: mix 封面 URL。
        :param imagePath: mix 本地封面路径。
        :return: None。
        '''
        if not itemId:
            pass
        mix_id = str('').strip()
        if not mix_id:
            return None
        if not title:
            pass
        if not subtitle:
            pass
        if not imageUrl:
            pass
        if not imagePath:
            pass
        meta = {
            'title': None(''),
            'subtitle': str(''),
            'imageUrl': str(''),
            'imagePath': str('') }
        with self._mix_meta_lock:
            self._mix_meta_by_id[mix_id] = meta
            if len(self._mix_meta_by_id) > self.MAX_MIX_META_ENTRIES:
                self._mix_meta_by_id.pop(next(iter(self._mix_meta_by_id)))
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _mixMetaForId(self = None, mixId = None):
        '''
        读取 mix 元数据注册表中指定 mix 的元数据。

        :param mixId: mix ID。
        :return: 元数据字典；未登记时返回空字典。
        '''
        if not mixId:
            pass
        mix_id = str('').strip()
        if not mix_id:
            return { }
        with None._mix_meta_lock:
            meta = self._mix_meta_by_id.get(mix_id)
            if isinstance(meta, dict):
                pass
            None(None, None, None)
            return dict(meta)
            with None:
                if not None:
                    pass

    
    def _genreImageMapFromResponse(self = None, genresResponse = None):
