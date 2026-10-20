# Source Generated with Decompyle++
# File: LPFavoriteSyncCoordinator.pyc (Python 3.9)

'''
收藏缓存生命周期同步器。
'''
import threading
import time
from typing import Dict, List, Optional, Tuple
import LPGlobalUI
from LPClientFramework.LPFavoriteCacheManager import LPFavoriteCacheManager
from LPClientFramework.LPFavoriteCacheManager import WIIMRADIO_LOCAL_USER_ID
from LPClientFramework.LPUtility import addNotificationObserver, deRegisterDeviceInfoChanged, logger, registerDeviceInfoChanged, removeNotificationObserver

class LPFavoriteSyncCoordinator:
    '''收藏缓存生命周期同步器：监听设备/账号事件并按 (source, userId) 调度拉取与清理。'''
    _instance = None
    FAVORITE_SOURCES = ('Tidal', 'Qobuz', 'WiiMRadio')
    SYNC_TTL_SECONDS = 3600
    PERIODIC_SYNC_INTERVAL_SECONDS = 3600
    RETRY_DELAYS = (30, 120, 600)
    
    def instance(cls = None):
        '''
        返回全局单例。

        :return: 全局同步器实例。
        '''
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    instance = None(instance)
    
    def __init__(self):
        '''初始化同步器内部状态。'''
        self._started = False
        self._sync_states = { }
        self._states_lock = threading.RLock()
        self._retry_timers = { }
        self._periodic_stop = None
        self._periodic_thread = None
        self._fetch_locks = (lambda .0: pass# WARNING: Decompyle incomplete
)(self.FAVORITE_SOURCES)

    
    def _stateFor(self = None, source = None, userId = None):
        '''
        返回指定账号的同步状态字典，不存在时创建。

        :param source: 音源标识。
        :param userId: 账号 ID。
        :return: 同步状态字典。
        '''
        key = (source, userId)
        with self._states_lock:
            state = self._sync_states.get(key)
            if state is None:
                state = {
                    'status': 'idle',
                    'lastSyncAt': 0,
                    'retryCount': 0,
                    'nextRetryAt': 0,
                    'lock': threading.RLock() }
                self._sync_states[key] = state
            None(None, None, None)
            return state
            with None:
                if not None:
                    pass

    
    def start(self = None):
        '''
        注册设备/账号事件监听；若已有当前设备，立即为有账号的音源发起同步。

        :return: None。
        '''
        if self._started:
            return None
        self._started = None
        addNotificationObserver('accountChangedForSource', self._onAccountChangedForSource)
        addNotificationObserver('DeviceChanged', self._onDeviceChanged)
        registerDeviceInfoChanged(self)
        self._prepareSingletons()
        device = getattr(LPGlobalUI, 'currentDevice', None)
        if device is not None:
            self.syncNowForDevice(device, True, **('force',))
        self._startPeriodicSync()

    
    def stop(self = None):
        '''
        反注册事件监听。

        :return: None。
        '''
        if not self._started:
            return None
        self._started = None
        self._stopPeriodicSync()
        removeNotificationObserver('accountChangedForSource', self._onAccountChangedForSource)
        removeNotificationObserver('DeviceChanged', self._onDeviceChanged)
        deRegisterDeviceInfoChanged(self)
        self._cancelAllRetries()

    
    def _startPeriodicSync(self = None):
        '''
        启动每小时一次的周期刷新守护线程。

        :return: None。
        '''
        if self._periodic_thread is not None and self._periodic_thread.is_alive():
            return None
        self._periodic_stop = None.Event()
        thread = threading.Thread(self._periodicLoop, 'favoriteSyncPeriodic', True, **('target', 'name', 'daemon'))
        self._periodic_thread = thread
        thread.start()

    
    def _stopPeriodicSync(self = None):
        '''
        停止周期刷新线�