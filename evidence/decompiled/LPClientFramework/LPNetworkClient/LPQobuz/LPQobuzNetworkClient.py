# Source Generated with Decompyle++
# File: LPQobuzNetworkClient.pyc (Python 3.9)

'''
@Time ： 2025/7/23 17:35
@Auth ： Chris
@File ：LPQobuzNetworkClient.py
@Desc:
'''
import json
import time
import requests
import requests_cache
from requests import RequestException
import LPGlobalUI
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPNetworkClient
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger
from LPClientFramework.util.aes import AESCipher

class LPQobuzNetworkClient(LPNetworkClient):
    
    def request(self, method, url, useCache, headers, retry, timeout = (True, None, True, 10), **kwargs):
        if headers is None:
            headers = { }
        if useCache:
            session = self.cachedSession
        else:
            session = self.session
        token = self.getToken()
        if token:
            headers.update({
                'Authorization': f'''Bearer {token}''' })
    # WARNING: Decompyle incomplete

    
    def _refresh_token(self):
        logger.debug('[LPQobuzNetworkClient] _refresh_token...')
    # WARNING: Decompyle incomplete


