# Source Generated with Decompyle++
# File: LPHibernation.pyc (Python 3.9)

'''
@Time ： 2025/3/11 16:00
@Auth ： Chris
@File ：LPNeverSleep.py
@Desc:
'''
import ctypes
import enum
import platform
from abc import ABC, abstractmethod
from LPClientFramework.LPUtility import logger

class LPHibernation(ABC):
    
    def preventSleep(self):
        pass

    preventSleep = abstractmethod(preventSleep)
    
    def keepDisplay(self):
        pass

    keepDisplay = abstractmethod(keepDisplay)
    
    def restoreState(self, eventType = ('preventSleep',)):
        pass

    restoreState = abstractmethod(restoreState)


class WinState(enum.IntEnum):
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 1
    ES_DISPLAY_REQUIRED = 2


class LPWinHibernation(LPHibernation):
    SYSTEM = 'Windows'
    
    def __init__(self = None):
        super().__init__()
        self.kernel32 = ctypes.WinDLL('kernel32.dll')

    
    def getState(self):
        currentState = self.kernel32.SetThreadExecutionState(0)
        error_code = self.kernel32.GetLastError()
        return currentState

    
    def preventSleep(self):
        result = self.kernel32.SetThreadExecutionState(WinState.ES_CONTINUOUS.value | WinState.ES_SYSTEM_REQUIRED.value)
        logger.debug('win preventSleep result: %s' % hex(result))

    
    def keepDisplay(self):
        result = self.kernel32.SetThreadExecutionState(WinState.ES_CONTINUOUS.value | WinState.ES_SYSTEM_REQUIRED.value | WinState.ES_DISPLAY_REQUIRED.value)
        logger.debug('win keepDisplay result: %s' % hex(result))

    
    def restoreState(self, eventType = ('preventSleep',)):
        result = self.kernel32.SetThreadExecutionState(WinState.ES_CONTINUOUS.value)
        logger.debug('win restoreState result: %s' % hex(result))

    __classcell__ = None


class MacState(enum.Enum):
    IOPM_ASSERTION_LEVEL_ON = 255
    IOPM_ASSERTION_LEVEL_OFF = 0


class LPMacHibernation(LPHibernation):
    SYSTEM = 'Darwin'
    
    def __init__(self = None):
        super().__init__()
        self.preventSleepAssertionID = ctypes.c_uint32(0)
        self.keepDisplayAssertionID = ctypes.c_uint32(0)
        self.preventSleepAssertionType = self._stringToCFString('PreventSystemSleep')
        self.preventSleepAssertionName = self._stringToCFString('SystemSleep')
        self.keepDisplayAssertionType = self._stringToCFString('PreventUserIdleDisplaySleep')
        self.keepDisplayAssertionName = self._stringToCFString('DisplaySleep')
        self.IOKit = self._setupIOKitFramework()

    
    def _setupIOKitFramework(self):
        framework = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/IOKit.framework/IOKit')
        framework.IOPMAssertionCreateWithName.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32)]
        framework.IOPMAssertionRelease.argtypes = [
            ctypes.c_uint32]
        return framework

    
    def _stringToCFString(self, string):
        import objc
        import CoreFoundation
        return objc.pyobjc_id(CoreFoundation.CFStringCreateWithCString(None, string.encode('utf-8'), CoreFoundation.kCFStringEncodingUTF8).nsstring())

    
    def preventSleep(self):
        logger.debug('===preventSleep===')
        ret = self.IOKit.IOPMAssertionCreateWithName(self.preventSleepAssertionType, MacState.IOPM_ASSERTION_LEVEL_ON.value, self.preventSleepAssertionName, ctypes.byref(self.preventSleepAssertionID))
        logger.debug('mac created power assertion --> preventSleep: status %s, id %s' % (ret, self.preventSleepAssertionID))

    
    def keepDisplay(self):
        logger.debug('===keepDisplay===')
        self.preventSleep()
        ret = self.IOKit.IOPMAssertionCreateWithName(self.keepDisplayAssertionType, MacState.IOPM_ASSERTION_LEVEL_ON.value, self.keepDisplayAssertionName, ctypes.byref(self.preventSleepAssertionID))
        logger.debug('mac created power assertion --> keepDisplay: status %s, id %s' % (ret, self.preventSleepAssertionID))

    
    def restoreState(self, eventType = ('preventSleep',)):
        if eventType == 'preventSleep':
            ret = self.IOKit.IOPMAssertionRelease(self.preventSleepAssertionID)
            logger.debug('mac release power assertion: status %s  eventType %s' % (ret, eventType))
        elif eventType == 'keepDisplay':
            ret1 = self.IOKit.IOPMAssertionRelease(self.preventSleepAssertionID)
            ret2 = self.IOKit.IOPMAssertionRelease(self.keepDisplayAssertionID)
            logger.debug('mac release power assertion: status ret1 %s  eventType %s' % (ret1, eventType))
            logger.debug('mac release power assertion: status ret2 %s  eventType %s' % (ret2, eventType))
        else:
            ret3 = 'invalid eventType'
            logger.debug('mac release power assertion: status %s  eventType %s' % (ret3, eventType))

    __classcell__ = None


class LPHibernationManager:
    
    def __init__(self):
        pass

    
    def instance(cls):
        system = platform.system()
    # WARNING: Decompyle incomplete

    instance = classmethod(instance)

