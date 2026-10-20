# Source Generated with Decompyle++
# File: LPUpnpAsyncDataModel.pyc (Python 3.9)

'''
@Time ： 2025/2/14 18:21
@Auth ： Chris
@File ：LPUpnpAsyncDataModel.py
@Desc:
'''
import threading
from PyQt6.QtCore import pyqtSignal
import LPGlobalUI
from LPClientFramework.LPDevice import LPDevice
from LPClientFramework.LPUtility import logger
from requests import Timeout
from LPClientFramework.util.aes import AESCipher

class LPUpnpAsyncDataModel:
    
    def __init__(self):
        pass

    
    def getData(self, worker, device = None, cmd = None, param = None, callback = {
        'device': LPDevice }, *args):
        pass
    # WARNING: Decompyle incomplete

    
    def worker(self, device = None, cmd = None, param = None, callback = {
        'device': LPDevice }, *args):
        response = device.upnpPost(cmd, param)
    # WARNING: Decompyle incomplete

    
    def getUserInfo(self, device, source, callback, *args):
        pass
    # WARNING: Decompyle incomplete

    
    def palyWithSearchUrl(self, device, xml, callback, *args):
        pass
    # WARNING: Decompyle incomplete

    
    def userLoginByCode(self, device, source, code, callback, *args):
        key = device.uuid[:16] if device.uuid else ''
        encryptedCode = AESCipher.encrypt2(key, code)
    # WARNING: Decompyle incomplete


