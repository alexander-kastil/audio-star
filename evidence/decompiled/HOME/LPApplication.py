# Source Generated with Decompyle++
# File: LPApplication.pyc (Python 3.9)

'''
@Time ： 2025/8/11 13:42
@Auth ： Chris
@File ：LPApplication.py
@Desc:
'''
import platform
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication
import LPGlobalUI
from LPClientFramework.LPUtility import logger
from LPClientFramework.util import LPUriHandler

class LPApplication(QApplication):
    _instance = None
    
    def get(cls, *args):
        pass
    # WARNING: Decompyle incomplete

    get = classmethod(get)
    
    def __init__(self = None, *args):
        pass
    # WARNING: Decompyle incomplete

    
    def event(self = None, e = None):
        if e.type() == QEvent.Type.FileOpen:
            url = e.url().toString()
            if url.startswith('wiim'):
                LPUriHandler.handlerUri(url)
            return True
        return None().event(e)

    
    def bring_to_front(self):
        NSApp = NSApp
        import AppKit
        NSApp.activateIgnoringOtherApps_(True)

    
    def quitApp(self):
        logger.info('[app] aboutToQuit -> quitApp mainWindow_exists=%s', LPGlobalUI.mainWindow is not None)
        if LPGlobalUI.mainWindow:
            LPGlobalUI.mainWindow.quitApp()

    
    def handleStateChange(self, state):
        logger.info('[app] handleStateChange state=%s', state)
        if state == Qt.ApplicationState.ApplicationActive and platform.system() == 'Darwin':
            logger.info('[app] mac handleStateChange ApplicationActive visible=%s', LPGlobalUI.mainWindow.isVisible())
            if not LPGlobalUI.mainWindow.isVisible():
                LPGlobalUI.mainWindow.showApp()

    __classcell__ = None

