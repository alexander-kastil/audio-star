# Source Generated with Decompyle++
# File: LPDeviceFileCache.pyc (Python 3.9)

'''
@Time ： 2025/12/3 17:15
@Auth ： Chris
@File ：LPDeviceFileCache.py
@Desc:
'''
import json
import threading
from enum import Enum
from LPClientFramework.LPCache.LPFileCache import FileCache
from LPClientFramework.LPUtility import logger

class LPDeviceFileCache(FileCache):
    
    def _getFilePath(self, type):
        return self.cacheDir / f'''{type.value}CacheV2.{self.fileType}'''

    
    def readCache(self = None, type = None):
        lock = self._getLock(type)
        path = self._getFilePath(type)
        
        def _read():
            if not path.exists():
                self.writeCache(type, {
                    type.value: { } })
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


