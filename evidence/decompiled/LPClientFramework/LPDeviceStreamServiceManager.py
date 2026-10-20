# Source Generated with Decompyle++
# File: LPDeviceStreamServiceManager.pyc (Python 3.9)

'''
@Time ： 2025/1/3 9:36
@Auth ： Chris
@File ：LPDeviceAccountManager.py
@Desc:
'''
import json
from importlib import import_module
from queue import Queue, Empty
from threading import Thread
from typing import Type
import LPGlobalUI
from LPClientFramework.LPConfig.LPAppFeatureConfig import isWiiMRadioEnabled
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPAccount, LPPlayListSource
from LPClientFramework.LPPlayList.LPRadioParadise2PlayList import LPRadioParadise2Account
from LPClientFramework.LPStreamServiceManager import LPStreamService, supportContents as defaultSupportContents
from LPClientFramework.LPUtility import logger
DEVICE_ACCOUNT_UNKNOWN = object()

class LPDeviceStreamServiceManager:
    '''设备流媒体服务管理器，负责注册、调用各音源的服务实例。

    内部维护一个单工作线程（_mediaInfoWorker），用于异步刷新 mediaInfo。
    工作线程从 _mediaInfoQueue 中取任务执行，队列深度始终 ≤ 1：
    新任务入队前会先清空队列，保证快速切歌时只执行最后一次请求，
    避免多线程并发导致的乱序或 UI 闪烁。
    '''
    
    def __init__(self, device):
        self.streamServiceDict = { }
        self.device = device
        self._deviceAccountState = { }
        self.streamServiceCapability = None
        self._deviceCapabilityList = []
        self._mediaInfoQueue = Queue()
        self._mediaInfoWorker = None

    
    def startMediaInfoWorker(self):
        '''启动 mediaInfo 后台工作线程。

        仅当设备 init() 成功后才调用本方法；若线程已启动则直接返回，
        避免设备信息更新等场景下重复调用 init() 导致线程被重复创建。
        '''
        if self._mediaInfoWorker is not None and self._mediaInfoWorker.is_alive():
            return None
        self._mediaInfoWorker = None(self._mediaInfoWorkerLoop, 'mediaInfoWorker', True, **('target', 'name', 'daemon'))
        self._mediaInfoWorker.start()

    
    def _mediaInfoWorkerLoop(self):
        '''工作线程主循环，持续从队列中取出最新的 mediaInfo 更新任务执行。

        队列为空时阻塞等待，不占用 CPU；取到任务后同步执行，
        执行完毕后再次进入等待。由于入队前会先清空旧任务，
        因此只会处理最新的一次切歌请求。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def pcServiceCapability():
        return LPDeviceStreamServiceManager.supportContents()

    pcServiceCapability = staticmethod(pcServiceCapability)
    
    def registerDeviceStreamService(self):
