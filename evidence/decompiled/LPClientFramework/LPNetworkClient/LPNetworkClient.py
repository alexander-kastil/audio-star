# Source Generated with Decompyle++
# File: LPNetworkClient.pyc (Python 3.9)

'''
@Time ： 2025/7/11 11:37
@Auth ： Chris
@File ：LPNetworkClient.py
@Desc:
'''
import enum
import threading
import requests
import requests_cache
from LPClientFramework import LPUtility
from LPClientFramework.LPNetworkClient.LPTokenProvider import LPTokenProvider
from LPClientFramework.LPUtility import logger

class LPRequestErrorType(enum.Enum):
    LP_Timeout_Error = 0
    LP_4xx_Error = 1
    LP_Unknown_Error = 2


class LPRequestError:
    
    def __init__(self = None, errortype = None, message = None):
        self.errortype = errortype
        self.message = message

    
    def __repr__(self):
        return f'''<LPRequestError type={self.errortype} message={self.message}>'''



class LPRequestCommonResult:
    
    def __init__(self = None, status_code = None, data = None, error = (None, None, None)):
        self.status_code = status_code
        self.data = data
        self.error = error

    
    def is_success(self = None):
        logger.debug(f'''status_code={self.status_code}, self.error={self.error}''')
        if self.status_code is not None:
            if self.status_code <= self.status_code:
                pass
            elif self.status_code < 300:
                pass
        return self.error is None

    
    def __repr__(self):
        return f'''<LPRequestCommonResult status_code={self.status_code} error={self.error} data={self.data}>'''



class LPNetworkClient:
    '''
    单例
    '''
    _instance = None
    
    def __new__(cls = None, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    
    def __init__(self = None, tokenProvider = None, cache_name = None, expire_after = (LPUtility.cacheDir / 'network_request_cache', 3600)):
        if self._initialized:
            return None
        self.cacheName = None(cache_name)
        self.cachedSession = requests_cache.CachedSession(self.cacheName, 'memory', 3600, **('backend', 'expire_after'))
        self.session = requests.session()
        self.tokenProvider = tokenProvider
        self._refreshing_token = False
        self._refresh_cond = threading.Condition()

    
    def getToken(self):
        return self.tokenProvider.getToken()

    
    def request(self, method, url, useCache, headers, retry, timeout = (True, None, True, 10), **kwargs):
        print('[DEBUG] Entered request()')
        if headers is None:
            headers = { }
        if useCache:
            session = self.cachedSession
        else:
            session = self.session
        token = self.getToken()
        if token:
            session.headers.update({
                'Authorization': f'''Bearer {token}''' })
    # WARNING: Decompyle incomplete

    
    def get(self, url, useCache = (True,), **kwargs):
        pass
    # WARNING: Decompyle incomplete

    
    def post(self, url, **kwargs):
        pass
    # WARNING: Decompyle incomplete

    __classcell__ = None

