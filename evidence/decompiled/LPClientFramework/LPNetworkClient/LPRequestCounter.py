# Source Generated with Decompyle++
# File: LPRequestCounter.pyc (Python 3.9)

'''
@Time ： 2025/8/8 14:37
@Auth ： Chris
@File ：LPRequestCounter.py
@Desc:
'''
import threading
from PyQt6.QtCore import pyqtSignal, QObject

class LPRequestCounter(QObject):
    pageErrorSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self._pending_count = 0
        self._failed_count = 0
        self._lock = threading.Lock()

    
    def start(self, request_count):
        with self._lock:
            self._pending_count = request_count
            self._failed_count = 0
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def requestFinished(self, success):
        with self._lock:
            if not success:
                self._failed_count += 1
                if self._failed_count == self._pending_count:
                    self.pageErrorSignal.emit()
                self(None, None, None)
            else:
                with None:
                    if not None:
                        pass

    __classcell__ = None

