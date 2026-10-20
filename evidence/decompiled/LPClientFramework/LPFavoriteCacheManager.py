# Source Generated with Decompyle++
# File: LPFavoriteCacheManager.pyc (Python 3.9)

'''
账号级收藏状态本地缓存。
'''
import json
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework.LPUtility import cacheDir, logger
WIIMRADIO_LOCAL_USER_ID = 'local'
_FAVORITE_TYPE_KEY_MAP = {
    'track': 'tracks',
    'tracks': 'tracks',
    'song': 'tracks',
    'songs': 'tracks',
    'album': 'albums',
    'albums': 'albums',
    'artist': 'artists',
    'artists': 'artists',
    'playlist': 'playlists',
    'playlists': 'playlists',
    'video': 'videos',
    'videos': 'videos',
    'station': 'stations',
    'stations': 'stations' }
_EMPTY_IDS: Dict[(str, List[str])] = {
    'artists': [],
    'albums': [],
    'tracks': [],
    'playlists': [],
    'videos': [],
    'stations': [] }
_ITEM_ID_KEYS: Dict[(str, tuple)] = {
    'stations': ('stationId', 'stationID', 'StationID', 'id'),
    'tracks': ('id', 'trackId', 'itemId'),
    'albums': ('id', 'albumId', 'itemId'),
    'artists': ('id', 'artistId', 'itemId'),
    'playlists': ('id', 'playlistId', 'itemId'),
    'videos': ('id', 'videoId', 'itemId') }

def _normalizeFavoriteType(itemType = None):
    '''
    把条目类型归一化为缓存类型 key。

    :param itemType: 原始条目类型。
    :return: 缓存类型 key；未知类型返回 None。
    '''
    if not itemType:
        return None
    return None.get(str(itemType).strip().lower())


def _normalizeIds(ids = None):
