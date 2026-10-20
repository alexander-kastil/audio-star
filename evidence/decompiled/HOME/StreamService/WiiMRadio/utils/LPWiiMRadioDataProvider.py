# Source Generated with Decompyle++
# File: LPWiiMRadioDataProvider.pyc (Python 3.9)

'''
WiiMRadio 异步数据提供层。
'''
import copy
import json
import statistics
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
import requests
import requests_cache
from LPClientFramework.LPEventTrack import LPAuthenticatedRequestClient
from LPClientFramework.LPUtility import logger, cacheDir, eventCountryCode
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioRequestScheduler import LPWiiMRadioRequestScheduler
_WIIM_RADIO_API_HOST = 'https://cloud-api.linkplay.com/prod/'
_WIIM_RADIO_LOCATION_API_HOST = 'https://api.linkplay.com'
_WIIM_RADIO_APP_ID = '<redacted>'
_WIIM_RADIO_ACCESS_KEY = '<redacted>'
_WIIM_RADIO_SECRET_KEY = '<redacted>'
_WIIM_RADIO_STATION_LIST_ENDPOINT = '/radio/station/list'
_WIIM_RADIO_LOCATION_ENDPOINT = '/apiv1/tool/location'
_EVENT_STATION_LIST_ERROR = 'ss_wiimradio_station_list'
_EVENT_AREA_NUM = 'ss_wiimradio_area_num'
_EVENT_STATION_LIST_TIME_COST = 'ss_wiimradio_station_list_time_cost'
_EVENT_TOOL_LOCATION_ERROR = 'ss_wiimradio_tool_location'
_STATION_LIST_TIME_COST_BATCH_SIZE = 10

class _LPWiiMRadioEventAnalytics:
    
    def __init__(self = None):
        '''
        初始化 WiiMRadio 埋点辅助器。

        :param: 无。
        :return: None。
        '''
        self._lock = threading.Lock()
        self._station_time_cost_records = []

    
    def trackStationListResult(self = None, requestPayload = None, result = None, durationMs = {
        'requestPayload': Dict[(str, Any)],
        'result': Dict[(str, Any)],
        'durationMs': int,
        'return': None }):
        '''
        按结果统一处理 station/list 的错误、地区数量与耗时统计埋点。

        :param requestPayload: 原始请求体。
        :param result: 归一化请求结果。
        :param durationMs: 当前请求耗时，单位毫秒。
        :return: None。
        '''
        safe_payload = requestPayload if isinstance(requestPayload, dict) else { }
        safe_result = result if isinstance(result, dict) else { }
        if not bool(safe_result.get('success')):
            self._logEvent(_EVENT_STATION_LIST_ERROR, self._buildStationListErrorParams(safe_payload, safe_result))
            return None
        if None._isAreaRequest(safe_payload):
            self._logEvent(_EVENT_AREA_NUM, self._buildAreaNumParams(safe_payload, safe_result))
        self._trackStationListTimeCost(safe_payload, durationMs)

    
    def trackLocationResult(self = None, result = None):
        '''
        处理 location 接口失败埋点。

        :param result: 归一化后的 location 结果。
        :return: None。
        '''
        safe_result = result if isinstance(result, dict) else { }
        if bool(safe_result.get('success')):
            return None
        None._logEvent(_EVENT_TOOL_LOCATION_ERROR, {
            'parameters': '',
            'errorCode': self._readErrorCode(safe_result),
            'errorDesc': self._readErrorDesc(safe_result) })

    
    def _buildStationListErrorParams(self = None, requestPayload = None, result = None):
        '''
        构造 station/list 失败埋点参数。

        :param requestPayload: 原始请求体。
        :param result: 归一化后的请求结果。
        :return: 埋点参数字典。
        '''
        return {
            'parameters': self._serializePayload(requestPayload),
            'errorCode': self._readErrorCode(result),
            'errorDesc': self._readErrorDesc(result) }

    
    def _buildAreaNumParams(self = None, requestPayload = None, result = None):
        '''
        构造地区电台数量埋点参数。

        :param requestPayload: 原始请求体。
        :param result: 归一化后的请求结果。
        :return: 埋点参数字典。
        '''
        items = result.get('items', [])
        normalized_items = items if isinstance(items, list) else []
        return {
            'countryCode': self._normalizeCountryCode(requestPayload.get('countryCode')),
            'subCountryCode': self._normalizeSubcountryCode(requestPayload.get('subcountryCode')),
            'number': len(normalized_items),
            'pageSize': self._safeInt(result.get('pageSize'), self._safeInt(requestPayload.get('pageSize'), 0)),
            'pageNo': self._safeInt(result.get('pageNo'), self._safeInt(requestPayload.get('pageNo'), 1)) }

    
    def _trackStationListTimeCost(self = None, requestPayload = None, durationMs = None):
        '''
        累积 station/list 成功请求耗时，并在满 10 条时上报统计埋点。

        :param requestPayload: 原始请求体。
        :param durationMs: 当前请求耗时，单位毫秒。
        :return: None。
        '''
        safe_duration = max(self._safeInt(durationMs, 0), 0)
        record = {
            'durationMs': safe_duration,
            'parameters': self._serializePayload(requestPayload) }
        batch_records = []
        with self._lock:
            self._station_time_cost_records.append(record)
            if len(self._station_time_cost_records) < _STATION_LIST_TIME_COST_BATCH_SIZE:
                pass
            None(None, None, None)
            return None
            batch_records = list(self._station_time_cost_records[:_STATION_LIST_TIME_COST_BATCH_SIZE])
            self._station_time_cost_records = self._station_time_cost_records[_STATION_LIST_TIME_COST_BATCH_SIZE:]
            None(None, None, None)
        with None:
            if not None:
                pass
        self._logEvent(_EVENT_STATION_LIST_TIME_COST, self._buildTimeCostParams(batch_records))

    
    def _buildTimeCostParams(self = None, records = None):
        '''
        根据一批请求耗时记录构造耗时统计埋点参数。

        :param records: 请求耗时记录列表。
        :return: 埋点参数字典。
        '''
        durations = (lambda .0 = None: [ max(self._safeInt(item.get('durationMs'), 0), 0) for item in .0 if isinstance(item, dict) ])(records)
        if not durations:
            return {
                'minTime': 0,
                'maxTime': 0,
                'medianTime': 0,
                'maxTimeParameters': '',
                'totalCount': str(_STATION_LIST_TIME_COST_BATCH_SIZE) }
        max_record = None(None, (lambda row = None: self._safeInt(row.get('durationMs'), 0)), **('key',))
        if not max_record.get('parameters', ''):
            pass
        return {
            'minTime': min(durations),
            'maxTime': max(durations),
            'medianTime': int(round(statistics.median(durations))),
            'maxTimeParameters': str(''),
            'totalCount': str(_STATION_LIST_TIME_COST_BATCH_SIZE) }

    
    def _logEvent(self = None, eventName = None, params = None):
        '''
        通过全局埋点发送器异步发送事件。

        本方法是 WiiMRadio 四个云 API 事件的唯一出口，统一补充设备系统
        地区码 "country_code"（与请求体里来自 /location 接口的 camelCase
        "countryCode" 语义不同，后者表示实际请求地区，保持原样）。

        :param eventName: 埋点事件名。
        :param params: 业务参数字典。
        :return: None。
        '''
        if not eventName:
            return None
        import LPGlobalUI
        eventParams = dict(params) if isinstance(params, dict) else { }
    # WARNING: Decompyle incomplete

    
    def _filterNonEmptyEntries(self = None, payload = None):
        '''
        过滤字典中值为空的键，避免上报参数超过长度限制。

        判定为空的值：None、空字符串、空列表、空字典；数字 0 等有效值予以保留。

        :param payload: 原始字典。
        :return: 仅包含非空值的新字典；非字典入参原样返回。
        '''
        if not isinstance(payload, dict):
            return payload
        result = None
        for key, value in payload.items():
            if value is None:
                continue
            if isinstance(value, str) and value == '':
                continue
            if isinstance(value, (list, dict)) and len(value) == 0:
                continue
            result[key] = value
        return result

    
    def _serializePayload(self = None, payload = None):
        '''
        将请求体稳定序列化为 JSON 字符串。

        为避免上报参数超过 100 字符长度限制，序列化前会剔除值为空的键
        （None / 空字符串 / 空集合），该处理同时作用于 station/list 失败埋点的
        parameters 与耗时统计埋点的 maxTimeParameters 字段。

        :param payload: 原始请求体。
        :return: 过滤空值键后稳定序列化的字符串；过滤后为空则返回空字符串。
        '''
        if not isinstance(payload, (dict, list)) or payload:
            return ''
        filtered = self._filterNonEmptyEntries(payload) if None(payload, dict) else payload
        if not filtered:
            return ''
        :
            if not isinstance(payload, (dict, list)) or payload:
                return ''
            filtered = self._filterNonEmptyEntries(payload) if None(payload, dict) else payload
            if not filtered:
                return ''
            
            return json.dumps(filtered, False, True, (',', ':'), **('ensure_ascii', 'sort_keys', 'separators'))
        return json.dumps(filtered, False, True, (',', ':'), **('ensure_ascii', 'sort_keys', 'separators'))
    # WARNING: Decompyle incomplete

    
    def _isAreaRequest(self = None, requestPayload = None):
        '''
        判断当前 station/list 请求是否带地区维度。

        :param requestPayload: 原始请求体。
        :return: 带 `countryCode` 或 `subcountryCode` 返回 True。
        '''
        if not isinstance(requestPayload, dict):
            return False
        if not self._normalizeCountryCode(requestPayload.get('countryCode')):
            pass
        return None(self._normalizeSubcountryCode(requestPayload.get('subcountryCode')))

    
    def _normalizeCountryCode(self = None, countryCode = None):
        '''
        将国家代码归一化为两位大写字符串。

        :param countryCode: 原始国家代码。
        :return: 合法国家代码；无效时返回空字符串。
        '''
        if not countryCode:
            pass
        normalized = str('').strip().upper()
        if len(normalized) == 2:
            return normalized

    
    def _normalizeSubcountryCode(self = None, subcountryCode = None):
        '''
        将子地区代码归一化为去空白后的字符串。

        :param subcountryCode: 原始子地区代码。
        :return: 归一化后的子地区代码。
        '''
        if not subcountryCode:
            pass
        return str('').strip()

    
    def _readErrorCode(self = None, result = None):
        '''
        从归一化结果中读取错误码。

        :param result: 归一化后的请求结果。
        :return: 错误码整数；不存在时返回 0。
        '''
        if not isinstance(result, dict):
            return 0
        return None._safeInt(result.get('errorCode'), 0)

    
    def _readErrorDesc(self = None, result = None):
        '''
        从归一化结果中读取错误描述，并按前 100 个字符截断。

        :param result: 归一化后的请求结果。
        :return: 截断至 100 字符以内的错误描述字符串。
        '''
        if not isinstance(result, dict):
            return ''
        if not result.get('errorDesc', ''):
            pass
        error_desc = None('').strip()
        if not error_desc:
            if not result.get('error', ''):
                pass
            error_desc = str('').strip()
        return error_desc[:100]

    
    def _safeInt(self = None, value = None, default = None):
        '''
        将任意值安全转换为整数。

        :param value: 待转换的值。
        :param default: 转换失败时的默认值。
        :return: 整数结果。
        '''
        pass
    # WARNING: Decompyle incomplete


_wiimRadioEventAnalytics = _LPWiiMRadioEventAnalytics()

class LPWiiMRadioDataProvider(QObject):
    ERROR_KIND_NONE = 'none'
    ERROR_KIND_HTTP_4XX = 'http_4xx'
    ERROR_KIND_TIMEOUT = 'timeout'
    ERROR_KIND_NETWORK = 'network'
    ERROR_KIND_BUSINESS = 'business'
    ERROR_KIND_UNKNOWN = 'unknown'
    _responseReady = pyqtSignal(object)
    _shared_lock = threading.Lock()
    _shared_session = None
    _shared_station_client = None
    _shared_location_client = None
    
    def __init__(self = None, timeout = None, parent = None):
        '''
        初始化数据提供器。

        :param timeout: HTTP 请求超时秒数。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._ensure_shared_clients(timeout)
        self._client = self.__class__._shared_station_client
        self._location_client = self.__class__._shared_location_client
        self._scheduler = LPWiiMRadioRequestScheduler.instance()
        self._callbacks = { }
        self._lock = threading.Lock()
        self._event_analytics = _wiimRadioEventAnalytics
        self._responseReady.connect(self._dispatch_response)

    
    def _ensure_shared_clients(cls = None, timeout = None):
        '''
        懒初始化全局共享的缓存 Session 与鉴权客户端。

        :param timeout: HTTP 请求超时秒数。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    _ensure_shared_clients = None(_ensure_shared_clients)
    
    def fetchStations(self = None, payload = None, callback = None, context = (None, LPWiiMRadioRequestScheduler.PRIORITY_BACKGROUND), priority = {
        'payload': Dict[(str, Any)],
        'callback': Callable[([
            Dict[(str, Any)]], None)],
        'context': Optional[Dict[(str, Any)]],
        'priority': str,
        'return': str }):
        '''
        异步请求电台列表。

        :param payload: `station/list` 接口请求体。
        :param callback: 主线程回调函数，入参为归一化结果字典。
        :param context: 回调透传上下文。
        :param priority: 调度优先级。
        :return: 当前请求的唯一标识。
        '''
        request_token = uuid.uuid4().hex
        safe_payload = copy.deepcopy(payload) if isinstance(payload, dict) else { }
        safe_context = copy.deepcopy(context) if isinstance(context, dict) else { }
        with self._lock:
            self._callbacks[request_token] = callback
            None(None, None, None)
        with None:
            if not None:
                pass
        request_key = self._build_station_request_key(safe_payload)
        
        def _deliver(result = None, requestToken = None, responseContext = None):
            '''
            将调度器结果转发为当前 DataProvider 的统一响应格式。

            :param result: 调度器返回结果。
            :param requestToken: 请求唯一标识。
            :param responseContext: 透传上下文。
            :return: None。
            '''
            normalized_result = result if isinstance(result, dict) else self._build_empty_result(safe_payload, 0, str(result), 0, str(result), **('status_code', 'error', 'error_code', 'error_desc'))
            payload_result = copy.deepcopy(normalized_result)
            payload_result['requestToken'] = requestToken
            payload_result['context'] = copy.deepcopy(responseContext)
            self._responseReady.emit(payload_result)

        None(None, (lambda safeRequestPayload = None: self._request_station_list(safeRequestPayload)), _deliver, priority, **('jobKey', 'task', 'callback', 'priority'))
        return request_token

    
    def fetchGlobalSearchStations(self, keyword, callback = None, context = None, pageNo = None, pageSize = (None, 1, 6, LPWiiMRadioRequestScheduler.PRIORITY_VISIBLE), priority = {
        'keyword': str,
        'callback': Callable[([
            Dict[(str, Any)]], None)],
        'context': Optional[Dict[(str, Any)]],
        'pageNo': int,
        'pageSize': int,
        'priority': str,
        'return': str }):
        '''
        异步请求 WiiMRadio 首页全局搜索结果。

        :param keyword: 搜索关键字，仅映射到接口的 name 字段。
        :param callback: 主线程回调函数，入参为归一化结果字典。
        :param context: 回调透传上下文。
        :param pageNo: 目标页码。
        :param pageSize: 每页返回条数。
        :param priority: 调度优先级。
        :return: 当前请求的唯一标识。
        '''
        payload = self._build_global_search_payload(keyword, pageNo, pageSize)
        return self.fetchStations(payload, callback, context, priority, **('callback', 'context', 'priority'))

    
    def fetchLocationCountryCode(self = None, callback = None, context = None, priority = (None, LPWiiMRadioRequestScheduler.PRIORITY_VISIBLE)):
        '''
        异步请求 location API 获取国家代码。

        :param callback: 主线程回调函数，入参为归一化结果字典。
        :param context: 回调透传上下文。
        :param priority: 调度优先级。
        :return: 当前请求的唯一标识。
        '''
        request_token = uuid.uuid4().hex
        safe_context = copy.deepcopy(context) if isinstance(context, dict) else { }
        with self._lock:
            self._callbacks[request_token] = callback
            None(None, None, None)
        with None:
            if not None:
                pass
        
        def _deliver(result = None, requestToken = None, responseContext = None):
            '''
            将 location 结果转发为统一响应格式。

            :param result: 调度器返回结果。
            :param requestToken: 请求唯一标识。
            :param responseContext: 透传上下文。
            :return: None。
            '''
            normalized_result = result if isinstance(result, dict) else self._build_empty_location_result(0, str(result), 0, str(result), **('status_code', 'error', 'error_code', 'error_desc'))
            payload_result = copy.deepcopy(normalized_result)
            payload_result['requestToken'] = requestToken
            payload_result['context'] = copy.deepcopy(responseContext)
            self._responseReady.emit(payload_result)

        self._scheduler.submitApiTask(self._build_location_request_key(), self._request_location_country_code, _deliver, priority, **('jobKey', 'task', 'callback', 'priority'))
        return request_token

    
    def _build_global_search_payload(self = None, keyword = None, pageNo = None, pageSize = {
        'keyword': str,
        'pageNo': int,
        'pageSize': int,
        'return': Dict[(str, Any)] }):
        '''
        构建首页全局搜索请求体。

        :param keyword: 搜索关键字。
        :param pageNo: 页码。
        :param pageSize: 每页数量。
        :return: `station/list` 接口请求体。
        '''
        if not keyword:
            pass
        normalized_keyword = str('').strip()
        if not normalized_keyword:
            pass
        return {
            'isDistinct': 1,
            'stationId': None,
            'name': None,
            'customName': None,
            'language': None,
            'languageCodes': None,
            'country': '',
            'countryCode': '',
            'categories': '',
            'customTags': [],
            'tags': None,
            'pageNo': self._safe_int(pageNo, 1),
            'pageSize': self._safe_int(pageSize, 6),
            'orderByStr': 'clickCount',
            'sortStr': '' }

    
    def _build_station_request_key(self = None, payload = None):
        '''
        为 `station/list` 请求构建可去重的稳定缓存键。

        :param payload: 请求体字典。
        :return: 稳定请求键。
        '''
        safe_payload = payload if isinstance(payload, dict) else { }
    # WARNING: Decompyle incomplete

    
    def _build_location_request_key(self = None):
        '''
        返回 location 请求的固定去重键。

        :param: 无。
        :return: location 请求键。
        '''
        return 'location_country_code'

    
    def _dispatch_response(self = None, result = None):
        '''
        在主线程中分发请求结果。

        :param result: 归一化后的请求结果。
        :return: None。
        '''
        if not result.get('requestToken', ''):
            pass
        request_token = str('')
        callback = None
        with self._lock:
            callback = self._callbacks.pop(request_token, None)
            None(None, None, None)
        with None:
            if not None:
                pass
        if callback:
            callback(result)

    
    def _request_station_list(self = None, payload = None):
        '''
        执行 `station/list` 请求并归一化响应结构。

        :param payload: 接口请求体。
        :return: 统一格式的分页结果。
        '''
        start_time = time.perf_counter()
        request_url = self._build_station_list_url()
        status_code = 0
    # WARNING: Decompyle incomplete

    
    def _build_station_list_url(self = None):
        '''
        构造 `station/list` 请求完整 URL。

        :param: 无。
        :return: 接口完整 URL。
        '''
        return f'''{_WIIM_RADIO_API_HOST.rstrip('/')}{_WIIM_RADIO_STATION_LIST_ENDPOINT}'''

    
    def _request_location_country_code(self = None):
        '''
        执行 location API 请求并归一化国家代码响应。

        :param: 无。
        :return: 统一格式的国家代码结果。
        '''
        start_time = time.perf_counter()
    # WARNING: Decompyle incomplete

    
    def _normalize_result(self = None, responsePayload = None, requestPayload = None, statusCode = {
        'responsePayload': Dict[(str, Any)],
        'requestPayload': Dict[(str, Any)],
        'statusCode': int,
        'return': Dict[(str, Any)] }):
        '''
        将接口响应转换为统一分页结构。

        :param responsePayload: 原始接口响应。
        :param requestPayload: 原始请求体。
        :param statusCode: HTTP 状态码。
        :return: 归一化后的分页结果。
        '''
        if not isinstance(responsePayload, dict):
            return self._build_empty_result(requestPayload, statusCode, 'invalid_response', 0, 'invalid_response', self.ERROR_KIND_UNKNOWN, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        business_code = None._extract_response_business_code(responsePayload)
        if business_code is not None and business_code != 0:
            message = self._extract_response_message(responsePayload)
            error = self._build_business_error_text(business_code, message)
            if not responsePayload.get('requestId', ''):
                pass
            return self._build_empty_result(requestPayload, statusCode, error, statusCode, message, self.ERROR_KIND_BUSINESS, str(''), **('status_code', 'error', 'error_code', 'error_desc', 'error_kind', 'request_id'))
        raw_items = None.get('resultList', [])
        items = []
        for raw_item in raw_items if isinstance(raw_items, list) else []:
            item = self._normalize_station_item(raw_item)
            if item:
                items.append(item)
                continue
                page_no = self._safe_int(responsePayload.get('pageNo'), self._safe_int(requestPayload.get('pageNo'), 1), **('default',))
                if not len(items):
                    pass
        page_size = self._safe_int(responsePayload.get('pageSize'), self._safe_int(requestPayload.get('pageSize'), 0), **('default',))
        total_pages = self._safe_int(responsePayload.get('totalPages'), 0, **('default',))
        total_rows = self._safe_int(responsePayload.get('totalRows'), 0, **('default',))
        if total_pages > 0:
            pass
        return {
            'items': items,
            'pageNo': page_no,
            'pageSize': page_size,
            'totalPages': total_pages,
            'totalRows': total_rows,
            'hasMore': page_no < total_pages,
            'statusCode': statusCode,
            'success': True,
            'error': '',
            'errorCode': 0,
            'errorDesc': '',
            'errorKind': self.ERROR_KIND_NONE,
            'requestId': responsePayload.get('requestId', '') }

    
    def _build_empty_result(self, requestPayload, status_code, error = None, error_code = None, error_desc = None, error_kind = ('', 0, '', ERROR_KIND_UNKNOWN, ''), request_id = {
        'requestPayload': Dict[(str, Any)],
        'status_code': int,
        'error': str,
        'error_code': int,
        'error_desc': str,
        'error_kind': str,
        'request_id': str,
        'return': Dict[(str, Any)] }):
        '''
        构造空结果兜底对象。

        :param requestPayload: 原始请求体。
        :param status_code: HTTP 状态码。
        :param error: 错误描述。
        :param error_code: 业务错误码或 HTTP 错误码。
        :param error_desc: 用于埋点的错误说明。
        :param error_kind: 稳定错误类型。
        :param request_id: 请求 ID。
        :return: 统一格式的空分页结果。
        '''
        if not error_desc:
            pass
        if not error_kind:
            pass
        return {
            'items': [],
            'pageNo': self._safe_int(requestPayload.get('pageNo'), 1),
            'pageSize': self._safe_int(requestPayload.get('pageSize'), 0),
            'totalPages': 0,
            'totalRows': 0,
            'hasMore': False,
            'statusCode': status_code,
            'success': False,
            'error': error,
            'errorCode': error_code,
            'errorDesc': error,
            'errorKind': self.ERROR_KIND_UNKNOWN,
            'requestId': request_id }

    
    def _normalize_location_result(self = None, responsePayload = None, statusCode = None):
        '''
        将 location API 响应转换为统一地区代码结构。

        :param responsePayload: 原始接口响应。
        :param statusCode: HTTP 状态码。
        :return: 归一化后的地区代码结果。
        '''
        if not isinstance(responsePayload, dict):
            return self._build_empty_location_result(statusCode, 'invalid_response', 0, 'invalid_response', self.ERROR_KIND_UNKNOWN, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        business_code = None._extract_response_business_code(responsePayload)
        if business_code is None:
            return self._build_empty_location_result(statusCode, 'invalid_response', 0, 'invalid_response', self.ERROR_KIND_UNKNOWN, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        if None != 0:
            message = self._extract_response_message(responsePayload)
            error = self._build_business_error_text(business_code, message)
            return self._build_empty_location_result(statusCode, error, statusCode, message, self.ERROR_KIND_BUSINESS, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        raw_data = None.get('data', { })
        if not isinstance(raw_data, dict):
            return self._build_empty_location_result(statusCode, 'invalid_data', 0, 'invalid_data', self.ERROR_KIND_UNKNOWN, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        country_code = None._normalize_country_code(raw_data.get('countryCode', ''))
        subcountry_code = self._normalize_subcountry_code(raw_data.get('region', ''))
        logger.debug(f'''get country_code -> {country_code}''')
        if not country_code:
            return self._build_empty_location_result(statusCode, 'invalid_country_code', 0, 'invalid_country_code', self.ERROR_KIND_UNKNOWN, **('status_code', 'error', 'error_code', 'error_desc', 'error_kind'))
        if not responsePayload.get('message', ''):
            pass
        return {
            'countryCode': None,
            'subcountryCode': subcountry_code,
            'statusCode': statusCode,
            'success': True,
            'error': '',
            'errorCode': 0,
            'errorDesc': '',
            'errorKind': self.ERROR_KIND_NONE,
            'message': str('').strip() }

    
    def _build_empty_location_result(self, status_code = None, error = None, error_code = None, error_desc = ('', 0, '', ERROR_KIND_UNKNOWN), error_kind = {
        'status_code': int,
        'error': str,
        'error_code': int,
        'error_desc': str,
        'error_kind': str,
        'return': Dict[(str, Any)] }):
        '''
        构造地区代码接口的空结果兜底对象。

        :param status_code: HTTP 状态码。
        :param error: 错误描述。
        :param error_code: 业务错误码或 HTTP 错误码。
        :param error_desc: 用于埋点的错误说明。
        :param error_kind: 稳定错误类型。
        :return: 统一格式的地区代码结果。
        '''
        if not error_desc:
            pass
        if not error_kind:
            pass
        return {
            'countryCode': '',
            'subcountryCode': '',
            'statusCode': status_code,
            'success': False,
            'error': error,
            'errorCode': error_code,
            'errorDesc': error,
            'errorKind': self.ERROR_KIND_UNKNOWN,
            'message': '' }

    
    def _classify_status_error(self = None, statusCode = None):
        '''
        根据 HTTP 状态码转换为页面可识别的错误类型。

        :param statusCode: HTTP 状态码。
        :return: 稳定错误类型字符串。
        '''
        safe_status_code = self._safe_int(statusCode, 0)
        if safe_status_code < safe_status_code or safe_status_code < 500:
            pass
        else:
            400
        return self.ERROR_KIND_HTTP_4XX
        return self.ERROR_KIND_UNKNOWN

    
    def _extract_response_business_code(self = None, responsePayload = None):
        '''
        从原始响应中提取业务错误码。

        :param responsePayload: 原始接口响应。
        :return: 可解析的业务码；字段缺失或不可解析时返回 None。
        '''
        if isinstance(responsePayload, dict) or 'code' not in responsePayload:
            return None
        :
            if isinstance(responsePayload, dict) or 'code' not in responsePayload:
                return None
            
            return int(responsePayload.get('code'))
        return int(responsePayload.get('code'))
    # WARNING: Decompyle incomplete

    
    def _extract_response_message(self = None, responsePayload = None):
        '''
        从原始响应中提取错误说明文本。

        :param responsePayload: 原始接口响应。
        :return: message 字段的字符串结果。
        '''
        if not isinstance(responsePayload, dict):
            return ''
        if not responsePayload.get('message', ''):
            pass
        return None('').strip()

    
    def _build_business_error_text(self = None, businessCode = None, message = None):
        '''
        组装业务错误描述文本。

        :param businessCode: 业务错误码。
        :param message: 后端 message。
        :return: 拼接后的错误文本。
        '''
        error = f'''business_error:{businessCode}'''
        if message:
            return f'''{error}:{message}'''

    
    def _extract_exception_error_info(self = None, exc = None):
        '''
        从请求异常对象中提取 HTTP 状态码与响应 message。

        :param exc: 请求异常对象。
        :return: 包含 `statusCode` 与 `message` 的字典。
        '''
        response = getattr(exc, 'response', None)
        if response is None:
            return {
                'statusCode': 0,
                'message': '' }
        response_payload = None._parse_response_json(response)
        return {
            'statusCode': self._safe_int(getattr(response, 'status_code', 0), 0),
            'message': self._extract_response_message(response_payload) }

    
    def _parse_response_json(self = None, response = None):
        '''
        安全解析响应对象中的 JSON 文本。

        :param response: requests 响应对象。
        :return: 解析成功时返回字典，否则返回空字典。
        '''
        if response is None:
            return { }
    # WARNING: Decompyle incomplete

    
    def _normalize_station_item(self = None, rawItem = None):
        '''
        将单个电台条目转换为 UI 可消费结构。

        :param rawItem: 原始电台条目字典。
        :return: 归一化后的电台条目；无有效 ID 时返回 None。
        '''
        if not isinstance(rawItem, dict):
            return None
        if not rawItem.get('StationID', ''):
            pass
        station_id = None('').strip()
        if not station_id:
            return None
        if not rawItem.get('Name', rawItem.get('customName', '')):
            pass
        name = None('').strip()
        if not rawItem.get('Favicon', ''):
            pass
        favicon = str('').strip()
        if not rawItem.get('StreamUrl', rawItem.get('Url', rawItem.get('URL', ''))):
            pass
        stream_url = str('').strip()
        if not rawItem.get('City', rawItem.get('city', '')):
            pass
        city = str('').strip()
        if not rawItem.get('Subcountry', rawItem.get('subcountry', rawItem.get('Region', rawItem.get('region', '')))):
            pass
        region = str('').strip()
        if not rawItem.get('Country', rawItem.get('country', '')):
            pass
        country = str('').strip()
        country_code = self._normalize_country_code(rawItem.get('CountryCode', rawItem.get('countryCode', '')))
        if not rawItem.get('Genres', rawItem.get('genres', '')):
            pass
        genres = str('').strip()
        return {
            'stationId': station_id,
            'name': name,
            'favicon': favicon,
            'streamUrl': stream_url,
            'city': city,
            'region': region,
            'country': country,
            'countryCode': country_code,
            'genres': genres }

    
    def _normalize_country_code(self = None, countryCode = None):
        '''
        将任意国家代码归一化为两位大写字符串。

        :param countryCode: 原始国家代码。
        :return: 合法国家代码；无效时返回空字符串。
        '''
        if not countryCode:
            pass
        normalized = str('').strip().upper()
        if len(normalized) == 2:
            return normalized

    
    def _normalize_subcountry_code(self = None, subcountryCode = None):
        '''
        将任意子地区代码归一化为接口可接受的字符串。

        :param subcountryCode: 原始子地区代码。
        :return: 去除首尾空白后的子地区代码；无效时返回空字符串。
        '''
        if not subcountryCode:
            pass
        return str('').strip()

    
    def _safe_int(self = None, value = None, default = None):
        '''
        将任意值安全转换为整数。

        :param value: 待转换的值。
        :param default: 转换失败时的默认值。
        :return: 整数结果。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _calculate_elapsed_ms(self = None, startTime = None):
        '''
        计算从起始时刻到当前的耗时毫秒数。

        :param startTime: `time.perf_counter()` 的起始值。
        :return: 四舍五入后的毫秒整数。
        '''
        return max(int(round((time.perf_counter() - float(startTime)) * 1000)), 0)

    __classcell__ = None

