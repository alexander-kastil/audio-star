# Source Generated with Decompyle++
# File: LPEventTrack.pyc (Python 3.9)

'''
@Time ： 2025/3/10 10:22
@Auth ： Chris
@File ：LPEventTrack.py
@Desc:
'''
import enum
import functools
import hashlib
import json
import os
import platform
import string
import threading
import time
import random
import uuid as uuidModule
from typing import Any, Dict, Optional, Tuple
import requests
import LPGlobalUI
from LPClientFramework.LPUtility import cacheDir, logger, pcUUID, appVersion, localeGeoContext

class LPEventsType(enum.Enum):
    FIRST_RUN = 'first_run'
    APP_OPEN = 'app_open'
    SCREEN_VIEW = 'screen_view'
    BUTTON_Click = 'button_click'
    DB_INDEX_CREATE = 'db_index_create'
    BEETS_IMPORT_RESULT = 'beets_import_result'
    NETWORK_CONTEXT_SNAPSHOT = 'network_context_snapshot'
    DEVICE_DISCOVERY_REPORT = 'device_discovery_report'
    DEVICE_DISCOVERY_FAILURE = 'device_discovery_failure'


class LPEventTrack:
    BATCH_SIZE = 10
    FLUSH_INTERVAL = 15
    MAX_RETRY_COUNT = 3
    DEBUG_DUMP_TO_LOCAL_FILE = False
    
    def __init__(self):
        self.url = 'https://api.linkplay.com/apiv1/mp/collect'
        self.headers = {
            'Content-Type': 'application/json' }
        self.sessionId = str(uuidModule.uuid4())
        self.appId = '<redacted>'
        self.appKey = '<redacted>'
        self.appSecret = '<redacted>'
        self._queue_file = cacheDir / 'event_track_queue.json'
        self._debug_dump_file = cacheDir / 'event_track_debug_dump.jsonl'
        self._queue_lock = threading.RLock()
        self._queue_condition = threading.Condition(self._queue_lock)
        self._flush_thread = None

    
    def _updateHeaders(self):
        '''
        更新事件上报请求头中的签名字段。

        参数:
            无
        返回:
            无
        '''
        accessKey = self.appKey
        timestamp = str(self._getTimestamp())
        nonce = self._getRandomString()
        hashedAppId = self._getHashAppId()
        signKey = self._getSignKey(hashedAppId, self.appKey, self.appSecret, nonce, timestamp)
        self.headers.update({
            'accessKey': accessKey,
            'timestamp': timestamp,
            'nonce': nonce,
            'sign': signKey,
            'appId': hashedAppId })

    
    def _getTimestamp(self):
        '''
        获取毫秒级时间戳。

        参数:
            无
        返回:
            int: 当前毫秒时间戳。
        '''
        return int(time.time() * 1000)

    
    def _getRandomString(self, length = (16,)):
        '''
        生成随机字符串。

        参数:
            length (int): 目标字符串长度。
        返回:
            str: 生成后的随机字符串。
        '''
        return ''.join(random.choices(string.ascii_letters + string.digits, length, **('k',)))

    
    def _sha256Hash(self, inputStr, upper = (False,)):
        '''
        对输入字符串做 SHA-256 摘要。

        参数:
            inputStr (str): 待摘要的原始字符串。
            upper (bool): 是否返回大写十六进制字符串。
        返回:
            str: SHA-256 摘要结果。
        '''
        result = hashlib.sha256(inputStr.encode('utf-8')).hexdigest()
        if upper:
            return result.upper()
        return None.lower()

    
    def _getHashAppId(self):
        '''
        生成哈希后的 appId。

        参数:
            无
        返回:
            str: 哈希后的 appId。
        '''
        tmpStr = self.appKey + self.appId
        return self._sha256Hash(tmpStr)

    
    def _getSignKey(self, appId, accessKey, secretKey, nonce, timestamp):
        '''
        生成请求签名。

        参数:
            appId (str): 哈希后的 appId。
            accessKey (str): 应用 access key。
            secretKey (str): 应用 secret key。
            nonce (str): 随机串。
            timestamp (str): 毫秒时间戳字符串。
        返回:
            str | None: 生成成功返回签名，参数不完整时返回 None。
        '''
        if not all([
            appId,
            accessKey,
            secretKey,
            nonce,
            timestamp]):
            return None
        tmpStr = f'''{accessKey}&appId={appId}&nonce={nonce}&timestamp={timestamp}&secretKey={secretKey}'''
        tmpStr = secretKey + tmpStr
        return self._sha256Hash(tmpStr, True)

    
    def _defaultEventParams(self, clientId, eventName):
        '''
        构建事件上报默认参数。

        参数:
            clientId (str): 客户端唯一标识。
            eventName (str): 事件名称
        返回:
            dict: 默认事件参数字典。
        '''
        params = {
            'app_ver': appVersion,
            'client_id': clientId,
            'app_session_id': self.sessionId,
            'system': platform.system() }
        if eventName == LPEventsType.APP_OPEN.value:
            locale_context = localeGeoContext()
            params.update({
                'country_code': locale_context.get('country_code', 'ZZ'),
                'language_code': locale_context.get('language_code', 'und'),
                'script_code': locale_context.get('script_code', ''),
                'locale_name': locale_context.get('locale_name', ''),
                'timezone': locale_context.get('timezone', '') })
        return params

    
    def logEvent(self = None, eventName = None, params = None):
        '''将事件写入本地缓存队列，达到阈值时唤醒批量推送。'''
        if not eventName:
            return None
        client_id = None()
        parameters = self._defaultEventParams(client_id, eventName)
        if params and isinstance(params, dict):
            parameters.update(params)
        event_record = {
            'name': eventName,
            'params': parameters,
            'retry_count': 0,
            'created_at': time.time() }
        self._append_event(client_id, event_record)
        self._ensure_flush_worker()

    
    def _append_event(self, client_id, event_record):
        '''线程安全地追加事件到本地队列文件。'''
        with self._queue_lock:
            queue_data = self._read_queue_locked()
            queue_data['client_id'] = client_id
            queue_data['pending_events'].append(event_record)
            self._write_queue_locked(queue_data)
            if len(queue_data['pending_events']) >= self.BATCH_SIZE:
                self._queue_condition.notify()
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _read_queue_locked(self):
        '''在持有锁的情况下读取队列文件，损坏时返回空队列。'''
        pass
    # WARNING: Decompyle incomplete

    
    def _write_queue_locked(self, queue_data):
        '''在持有锁的情况下原子写入队列文件（先写临时文件再替换）。'''
        tmp_path = str(self._queue_file) + '.tmp'
    # WARNING: Decompyle incomplete

    
    def _ensure_flush_worker(self):
        '''确保后台 flush 线程已启动（延迟启动，避免模块导入时创建线程）。'''
        with self._queue_lock:
            if self._flush_thread is not None and self._flush_thread.is_alive():
                pass
            None(None, None, None)
            return None
            self._flush_thread = threading.Thread(self._flush_worker, True, **('target', 'daemon'))
            self._flush_thread.start()
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _flush_worker(self):
        '''后台线程：队列达到 BATCH_SIZE 立即发送，否则定时检查。'''
        with self._queue_lock:
            queue_data = self._read_queue_locked()
            event_count = len(queue_data.get('pending_events', []))
            if event_count >= self.BATCH_SIZE:
                self._do_flush_locked()
            None(None, None, None)
            continue
            self._queue_condition.wait(self.FLUSH_