# Source Generated with Decompyle++
# File: LPPickleCache.pyc (Python 3.9)

'''
@Time ： 2025/7/10 9:21
@Auth ： Chris
@File ：LPPickleCache.py
@Desc:
'''
import pickle
import threading
from pathlib import Path

class LPPickleCache:
    
    def __init__(self):
        self._locks = { }
        self._globalLock = threading.Lock()

    
    def _getLock(self = None, filePath = None):
        '''获取指定文件的锁，如果不存在则创建'''
        with self._globalLock:
            if filePath not in self._locks:
                self._locks[filePath] = threading.Lock()
            None(None, None, None)
            return self._locks[filePath]
            with None:
                if not None:
                    pass

    
    def save(self, filePath, data):
        '''线程安全地保存数据到 pickle 文件'''
        filePath = str(Path(filePath).resolve())
        lock = self._getLock(filePath)
        with lock:
            Path(filePath).parent.mkdir(True, True, **('parents', 'exist_ok'))
            with open(filePath, 'wb') as f:
                pickle.dump(data, f)
                None(None, None, None)
            with None:
                if not None:
                    pass
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def tryLoad(self, filePath, default = (None,)):
        '''尝试读取，如果文件不存在或出错，返回默认值'''
        file_path = str(Path(filePath).resolve())
        lock = self._getLock(file_path)
    # WARNING: Decompyle incomplete


