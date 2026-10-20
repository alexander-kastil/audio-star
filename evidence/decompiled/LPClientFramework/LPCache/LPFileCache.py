# Source Generated with Decompyle++
# File: LPFileCache.pyc (Python 3.9)

'''
@Time ： 2025/5/7 13:45
@Auth ： Chris
@File ：LPFileCache.py
@Desc:
'''
import json
import threading
from enum import Enum
from LPClientFramework.LPUtility import logger

class FileCache:
    
    def __init__(self, cacheDir, fileType = ('json',)):
        self.cacheDir = cacheDir
        self.cacheDir.mkdir(True, True, **('parents', 'exist_ok'))
        self.fileType = fileType
        self._locks = { }

    
    def _getLock(self, type):
        if type not in self._locks:
            self._locks[type] = threading.RLock()
        return self._locks[type]

    
    def _getFilePath(self, type):
        return self.cacheDir / f'''{type.value}Cache.{self.fileType}'''

    
    def writeCache(self = None, type = None, data = None):
        lock = self._getLock(type)
        path = self._getFilePath(type)
        
        def _write():
            if self.fileType == 'json':
                with open(path, 'w', 'utf-8', **('encoding',)) as f:
                    json.dump(data, f, 2, **('indent',))
                    None(None, None, None)
                with None:
                    if not None:
                        pass
            else:
                raise ValueError(f'''writeCache unsupported fileType: {self.fileType}''')

        with lock:
            None(None, None, None)
            return _write()
            with None:
                if not None:
                    pass

    
    def readCache(self = None, type = None):
        lock = self._getLock(type)
        path = self._getFilePath(type)
        
        def _read():
            if not path.exists():
                self.writeCache(type, {
                    type.value: [] })
            if self.fileType == 'json':
                with open(path, 'r', 'utf-8', **('encoding',)) as f:
                    None(None, None, None)
                    return json.load(f)
                    with None:
                        if not None:
                            pass
            else:
                raise ValueError(f'''readCache unsupported fileType: {self.fileType}''')

        with lock:
            None(None, None, None)
            return _read()
            with None:
                if not None:
                    pass

    
    def updateCache(self = None, type = None, updateFunc = None, *args):
        '''
        从文件读取旧数据，使用 updateFunc(data) 生成新数据，再写入。
        '''
        lock = self._getLock(type)
    # WARNING: Decompyle incomplete


