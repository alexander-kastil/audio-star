# Source Generated with Decompyle++
# File: LPTrackImageLoadHelper.pyc (Python 3.9)

import queue
import threading
from PyQt6 import QtCore
_sharedTrackImageLoaderLock = threading.Lock()
_sharedTrackImageLoader = None
_trackImageHelperRegistryLock = threading.Lock()
_trackImageHelperRegistry = { }
_nextTrackImageHelperToken = 1

def _registerTrackImageHelper(helper):
    '''
    为 helper 注册一个进程内唯一标识。

    参数:
        helper (LPTrackImageLoadHelper): 需要注册的 helper 对象。
    返回:
        int: helper 的唯一标识。
    '''
    global _nextTrackImageHelperToken
    with _trackImageHelperRegistryLock:
        helperToken = _nextTrackImageHelperToken
        _nextTrackImageHelperToken += 1
        _trackImageHelperRegistry[helperToken] = helper
        None(None, None, None)
        return helperToken
        with None:
            if not None:
                pass


def _unregisterTrackImageHelper(helperToken):
    '''
    注销指定 helper 的注册信息。

    参数:
        helperToken (int): helper 唯一标识。
    返回:
        无
    '''
    with _trackImageHelperRegistryLock:
        _trackImageHelperRegistry.pop(helperToken, None)
        None(None, None, None)
    with None:
        if not None:
            pass


def _getRegisteredTrackImageHelper(helperToken):
    '''
    获取仍处于注册状态的 helper 对象。

    参数:
        helperToken (int): helper 唯一标识。
    返回:
        LPTrackImageLoadHelper | None: 命中时返回 helper，否则返回 `None`。
    '''
    with _trackImageHelperRegistryLock:
        None(None, None, None)
        return _trackImageHelperRegistry.get(helperToken)
        with None:
            if not None:
                pass


def _getSharedTrackImageLoader():
    '''
    获取进程级共享封面后台加载器。

    参数:
        无
    返回:
        _LPSharedTrackImageLoader: 共享后台加载器实例。
    '''
    global _sharedTrackImageLoader
    with _sharedTrackImageLoaderLock:
        if _sharedTrackImageLoader is None:
            _sharedTrackImageLoader = _LPSharedTrackImageLoader()
        None(None, None, None)
        return _sharedTrackImageLoader
        with None:
            if not None:
                pass


class _LPTrackImageDispatchBridge(QtCore.QObject):
    taskFinishedSignal = QtCore.pyqtSignal(int, int, int, str)
    
    def __init__(self = None):
        '''
        初始化主线程派发桥。

        参数:
            无
        返回:
            无
        '''
        super().__init__()
        self.taskFinishedSignal.connect(self._dispatchTaskFinished, QtCore.Qt.ConnectionType.QueuedConnection)

    
    def _dispatchTaskFinished(self, helperToken, generation, row, imageUrl):
        '''
        在 Qt 主线程中把完成事件派发给仍然活跃的 helper。

        参数:
            helperToken (int): helper 唯一标识。
            generation (int): helper 当前批次号。
            row (int): 对应行号。
            imageUrl (str): 当前任务图片地址。
        返回:
            无
        '''
        helper = _getRegisteredTrackImageHelper(helperToken)
        if helper is None:
            return None
        None._handleSharedImageReady(generation, row, imageUrl)

    _dispatchTaskFinished = QtCore.pyqtSlot(int, int, int, str)(_dispatchTaskFinished)
    __classcell__ = None


class _LPSharedTrackImageLoader(object):
    
    def __init__(self):
        '''
        初始化共享封面后台加载器。

        参数:
            无
        返回:
            无
        '''
        self._dispatchBridge = _LPTrackImageDispatchBridge()
        self._taskQueue = queue.Queue()
        self._workerThread = threading.Thread(self._workerLoop, 'LPSharedTrackImageLoader', True, **('target', 'name', 'daemon'))
        self._workerThread.start()

    
    def submit(self, helperToken, generation, row, imageUrl, cacheSize, utilityModule):
        '''
        提交一个封面加载任务到共享后台队列。

        参数:
            helperToken (int): helper 唯一标识。
            generation (int): helper 当前批次号。
            row (int): 对应行号。
            imageUrl (str): 当前任务图片地址。
            cacheSize (int): 封面缓存尺寸。
            utilityModule (module): `LPUtility` 模块对象。
        返回:
            无
        '''
        if not imageUrl:
            return None
        None._taskQueue.put({
            'helperToken': helperToken,
            'generation': generation,
            'row': row,
            'imageUrl': imageUrl,
            'cacheSize': cacheSize,
            'utilityModule': utilityModule })

    
    def _workerLoop(self):
        '''
        共享后台线程主循环，负责下载封面并把完成事件回投到主线程。

        参数:
            无
        返回:
            无
        '''
        task = self._taskQueue.get()
        
        try:
            helperToken = task.get('helperToken')
            generation = task.get('generation', 0)
            row = task.get('row', -1)
            imageUrl = task.get('imageUrl', '')
            utilityModule = task.get('utilityModule')
            cacheSize = task.get('cacheSize', 0)
            helper = _getRegisteredTrackImageHelper(helperToken)
            if helper is None:
                pass
        finally:
            self._taskQueue.task_done()
            continue
            if not helper._isBackgroundTaskStillValid(generation, row, imageUrl):
                pass
            self._taskQueue.task_done()
            continue
            if utilityModule.getCachedPixmapWithUrl(imageUrl, cacheSize) is None:
                respDict = utilityModule.fetchUrlQPixmap(imageUrl, False, cacheSize)
                if respDict.get('image', None) is None:
                    pass
                self._taskQueue.task_done()
                continue
            helper = _getRegisteredTrackImageHelper(helperToken)
            if helper is None:
                pass
            self._taskQueue.task_done()
            continue
            if not helper._isBackgroundTaskStillValid(generation, row, imageUrl):
                pass
            self._taskQueue.task_done()
            continue
            self._dispatchBridge.taskFinishedSignal.emit(helperToken, generation, row, imageUrl)
            self._taskQueue.task_done()
            continue
            self._taskQueue.task_done()
            continue
            return None




class LPTrackImageLoadHelper(QtCore.QObject):
    rowImageReadySignal = QtCore.pyqtSignal(int)
    
    def __init__(self = None, imageUrlProvider = None, rowCountProvider = None, utilityModule = None, cacheSize = None, prefetchRows = None, parent = None):
        '''
        初始化曲目封面加载协调器。

        参数:
            imageUrlProvider (callable): 传入行号并返回图片地址的回调。
            rowCountProvider (callable): 返回当前模型总行数的回调。
            utilityModule (module): 已完成初始化的 `LPUtility` 模块对象。
            cacheSize (int): 图片缓存尺寸。
            prefetchRows (int): 当前可见区前后预取的行数。
            parent (QObject | None): Qt 父对象。
        返回:
            无
        '''
        super().__init__(parent)
        self._imageUrlProvider = imageUrlProvider
        self._rowCountProvider = rowCountProvider
        self._utilityModule = utilityModule
        self._cacheSize = cacheSize
        self._prefetchRows = prefetchRows
        self._view = None
        self._visibleRange = (-1, -1)
        self._pendingTaskSet = set()
        self._generation = 0
        self._isShutdown = False
        self._helperToken = _registerTrackImageHelper(self)
        self._lock = threading.RLock()

    
    def attachView(self, view):
        '''
        绑定表格视图，并开始监听当前可见行变化。

        参数:
            view (QTableView): 需要监听可见区域的表格视图。
        返回:
            无
        '''
        if self._view is view:
            self.refreshVisibleRows()
            return None
        if None._view is not None:
            self._disconnectViewSignals(self._view)
        self._view = view
        if self._view is None:
            return None
        None._view.visibleRowsChanged.connect(self._onVisibleRowsChanged)
        self._view.destroyed.connect(self.shutdown)
        self.refreshVisibleRows()

    
    def refreshVisibleRows(self):
