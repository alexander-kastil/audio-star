# Source Generated with Decompyle++
# File: LPTokenProvider.pyc (Python 3.9)

'''
@Time ： 2025/7/25 19:21
@Auth ： Chris
@File ：LPTokenProvider.py
@Desc:
'''
import threading

class LPTokenProvider:
    
    def __init__(self):
        self._account = None
        self._refreshing = False
        self._refreshCond = threading.Condition()

    
    def setAccount(self, account):
        self._account = account

    
    def getToken(self):
        if self._account:
            return self._account.token

    
    def replaceToken(self, newToken):
        if self._account:
            self._account.token = newToken

    
    def refreshToken(self, refreshFunc):
        with self._refreshCond:
            if self._refreshing:
                if self._refreshing:
                    self._refreshCond.wait()
                None(None, None, None)
                return True
            self._refreshing = None
            None(None, None, None)
        with None:
            if not None:
                pass
        
        try:
            refreshFunc()
        finally:
            with self._refreshCond:
                self._refreshing = False
                self._refreshCond.notify_all()
                None(None, None, None)
            with None:
                if not None:
                    pass
        with self._refreshCond:
            self._refreshing = False
            self._refreshCond.notify_all()
            None(None, None, None)
        with None:
            if not None:
                pass

        return True


