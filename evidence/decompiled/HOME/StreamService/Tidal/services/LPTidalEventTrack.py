# Source Generated with Decompyle++
# File: LPTidalEventTrack.pyc (Python 3.9)

'''
TIDAL 埋点事件辅助类。

线程安全，无 Qt 依赖。
使用方式：直接 import 并调用类方法，无需实例化。

## 当前已实施的事件

| 事件名          | 触发条件                                      |
|-----------------|-----------------------------------------------|
| tidal_login     | 登录成功或失败（注意数据脱敏）                |
| tidal_api_error | 非 2xx / 非 304 的 API 响应                   |
| tidal_playback  | 播放事件（成功/失败），当前仅 TIDAL 使用      |

## 暂不实施的事件（P2 — 后续按需添加）

| 事件名                   | 说明                                 |
|--------------------------|--------------------------------------|
| tidal_page_error         | 页面加载异常，需在各页面 viewWillAppear 添加 |
| tidal_playlist_error     | 歌单操作（创建/添加/移除/排序）失败  |
| tidal_detail_load_error  | 详情页（album/artist/playlist/mix）加载失败 |
| tidal_image_load_error   | 图片下载失败（network/disk_full/permission） |
| tidal_scheduler_blocked  | 请求队列积压超过阈值                 |
'''
import hashlib
import threading
import time
from typing import Any, Dict, List, Optional

class LPTidalEventTrack:
    '''轻量级 TIDAL 埋点辅助类。全部类方法，无 Qt 依赖，线程安全。'''
    _timers: Dict[(str, float)] = { }
    _lock = threading.RLock()
    _PREFIX = 'tidal_'
    _SOURCE = 'tidal'
    
    def _desensitize_uuid(cls = None, device_uuid = None):
        '''对 device_uuid 脱敏：取前 8 位截断。'''
        if not device_uuid:
            return ''
        return None(device_uuid)[:8]

    _desensitize_uuid = None(_desensitize_uuid)
    
    def _eventCountryCode(cls = None):
        '''
        读取埋点统一使用的设备系统地区码。

        延迟导入 LPUtility，保持本模块导入期无 Qt 依赖；取值失败一律回落
        "ZZ"，埋点取地区不能影响业务主链路。

        参数:
            无。
        返回:
            str: 两位大写地区码；无法获取时返回 "ZZ"。
        '''
        pass
    # WARNING: Decompyle incomplete

    _eventCountryCode = None(_eventCountryCode)
    
    def _log(cls = None, event_suffix = None, params = classmethod):
        if not event_suffix:
            return None
        event_name = f'''{None._PREFIX}{event_suffix}'''
        safe_params = dict(params) if isinstance(params, dict) else { }
    # WARNING: Decompyle incomplete

    _log = None(_log)
    
    def _classify(cls = None, status_code = None):
        pass
    # WARNING: Decompyle incomplete

    _classify = None(_classify)
    
    def login_event(cls, success, method, error_code, error_message = None, duration_ms = None, device_uuid = classmethod, account_country_code = ('', '', None, '', '', ''), subscription_type = {
        'success': bool,
        'method': str,
        'error_code': str,
        'error_message': str,
        'duration_ms': Optional[float],
        'device_uuid': str,
        'account_country_code': str,
        'subscription_type': str,
        'return': None }):
        '''记录登录事件，成功或失败都上报。device_uuid 已脱敏。

        "country_code" 为设备系统地区码（LPUtility.eventCountryCode）；
        TIDAL 账号地区码单独放在 "tidal_account_country_code"，两者语义不同。
        '''
        params = {
            'success': success,
            'method': method,
            'error_code': error_code,
            'error_message': error_message,
            'device_uuid': cls._desensitize_uuid(device_uuid),
            'tidal_account_country_code': account_country_code,
            'country_code': cls._eventCountryCode(),
            'subscription_type': subscription_type }
        if duration_ms is not None:
            params['duration_ms'] = int(duration_ms)
        cls._log('login', params)

    login_event = None(login_event)
    
    def api_error(cls, endpoint, method, status_code = None, elapsed_ms = None, retry_count = classmethod, account_country_code = (0, 0, '', None), error = {
        'endpoint': str,
        'method': str,
        'status_code': Any,
        'elapsed_ms': int,
        'retry_count': int,
        'account_country_code': str,
        'error': Any,
        'return': None }):
        '''记录 TIDAL API 错误事件。

        "country_code" 为设备系统地区码（LPUtility.eventCountryCode）；
        TIDAL 账号地区码单独放在 "tidal_account_country_code"，两者语义不同。
        '''
        if not endpoint:
            pass
        if not method:
            pass
        if not status_code:
            pass
        if not elapsed_ms:
            pass
        if not retry_count:
            pass
        if not account_country_code:
            pass
        cls._log('api_error', {
            'endpoint': str(''),
            'method': str(''),
            'status_code': int(0),
            'error_type': cls._classify(status_code),
            'elapsed_ms': int(0),
            'retry_count': int(0),
            'tidal_account_country_code': str(''),
            'country_code': cls._eventCountryCode() })

    api_error = None(api_error)
    
    def playback_event(cls, status, source, content_type = None, error_reason = None, device_uuid = classmethod, firmware_version = ('', '', '', '', '', None), duration_ms = {
        'status': str,
        'source': str,
        'content_type': str,
        'error_reason': str,
        'device_uuid': str,
        'firmware_version': str,
        'duration_ms': Optional[float],
        'return': None }):
        '''通用播放事件（成功/失败）。当前仅 _SOURCE="tidal" 时由 TIDAL 代码调用。'''
        if not source:
            pass
        params = {
            'source': cls._SOURCE,
            'caller_source': str(''),
            'status': status,
            'content_type': content_type,
            'error_reason': error_reason,
            'device_uuid': cls._desensitize_uuid(device_uuid),
            'firmware_version': firmware_version }
        if duration_ms is not None:
            params['duration_ms'] = int(duration_ms)
        cls._log('playback', params)

    playback_event = None(playback_event)

