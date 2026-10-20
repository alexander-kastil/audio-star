# Source Generated with Decompyle++
# File: LPNetworkDataModel.pyc (Python 3.9)

'''
@Time ： 2025/2/14 16:19
@Auth ： Chris
@File ：LPUpnpAsyncDataModel.py
@Desc:
'''
import threading
import requests_cache
from PyQt6.QtCore import pyqtSignal, QObject
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPUtility import logger
from requests import Timeout

class LPNetworkDataModel(QObject):
    timeoutSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        request_cache_path = LPUtility.cacheDir / 'request_cache'
        self.session = requests_cache.CachedSession(str(request_cache_path), 3600, **('expire_after',))

    
    def getData(self, worker, url, callback, *args):
        pass
    # WARNING: Decompyle incomplete

    
    def worker(self, url, callback, *args):
        response = None
    # WARNING: Decompyle incomplete

    __classcell__ = None

