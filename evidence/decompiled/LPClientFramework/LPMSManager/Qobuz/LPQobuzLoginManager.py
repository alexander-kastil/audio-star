# Source Generated with Decompyle++
# File: LPQobuzLoginManager.pyc (Python 3.9)

'''
@Time ： 2025/7/21 16:51
@Auth ： Chris
@File ：LPQobuzLoginManager.py
@Desc:
'''
import json
import os
import webbrowser
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.page.LPMSUnsupportedPage import LPMSUnsupportedPage
from LPCommonWidgets.page.UI.LPMSUnsupportedPage_ui import Ui_MSUnsupportedWidget

class LPQobuzLoginManager(QObject):
    unsupportedSignal = pyqtSignal()
    getUserInfoFinishSignal = pyqtSignal()
    updateAccountSignal = pyqtSignal()
    updateAccountEndSignal = pyqtSignal()
    showLoginPageSignal = pyqtSignal()
    closeLoginPageSignal = pyqtSignal()
    popAllSourcePageSignal = pyqtSignal(bool)
    clearCacheSignal = pyqtSignal()
    initAccountAboutSignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        LPUtility.addNotificationObserver('OAuthCodeChanged', self.onOAuthExCodeReceived)
        LPUtility.addNotificationObserver('accountChangedForSource', self.onAccountChanged)
        LPUtility.addNotificationObserver('DeviceChanged', self.onDeviceChanged)
        self.updateAccountSignal.connect(self.updateAccount)
        self.source = LPPlayListSource.Qobuz.value
        self.account = None
        self.upnpModel = LPUpnpAsyncDataModel()
        self.redirectUrl = 'https://www.qobuz.com/signin/oauth2?client_id=155398957&redirect_uri=https://auth.wiimhome.com/qobuz/wiimhome&response_type=code&state=pc'
        self.loginPage = None
        self.showLoginPageSignal.connect(self.showLoginPage)
        self.closeLoginPageSignal.connect(self.closeLoginPage)
        self.updateAccountEndSignal.connect(self.updateAccountEnd)
        self.popAllSourcePageSignal.connect(self.popAllSourcePage)
        self.unsupportedSignal.connect(self.showUnsupportedPage)
        self.clearCacheSignal.connect(self.clearCache)
        self.tokenProvider = None

    
    def getAccount(self, device):
        self.account = device.deviceStreamServiceManager.accountForSource(self.source)
        return self.account

    
    def getUserInfo(self, device):
        
        def callback(response = None, *args):
            pass
        # WARNING: Decompyle incomplete

        self.upnpModel.getUserInfo(device, self.source, callback, **('callback',))

    
    def onOAuthExCodeReceived(self, params):
        
        def callback(response):
            logger.debug('qobuz ExchangeCodeReceiveCallback ==== end auth')

        logger.debug('qobuz onOAuthExCodeReceived ==== ')
        device = params.get('device', None)
        notify = params.get('notify', None)
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None.get('source', None) != self.source:
            return None
        code = None.get('exchange_code', None)
        if code:
            self.upnpModel.userLoginByCode(LPGlobalUI.currentDevice, self.source, code, callback, **('callback',))

    
    def onAccountChanged(self, params):
        device = params.get('device', None)
        notify = params.get('notify', None)
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None.get('source', None) != self.source:
            return None
        None.debug('qobuz accountChanged ====')
        self.updateAccountSignal.emit()

    
    def updateAccount(self):
        '''按当前设备账号刷新 Qobuz 登录状态，未登录时进入登录页。'''
        self.account = self.getAccount(LPGlobalUI.currentDevice)
        if self.account and self.account.userId:
            logger.debug('qobuz updateAccount ==== account')
            self.tokenProvider.setAccount(self.account)
            self.closeLoginPageSignal.emit()
            self.initAccountAboutSignal.emit()
            self.updateAccountEndSignal.emit()
        else:
            logger.debug('qobuz updateAccount ==== not account')
            self.getUserInfo(LPGlobalUI.currentDevice)

    updateAccount = pyqtSlot()(updateAccount)
    
    def updateAccountEnd(self):
        LPQobuzViewController = LPQobuzViewController
        import HOME.StreamService.Qobuz.Browse.LPQobuzViewController
        Ui_qobuzWidget = Ui_qobuzWidget
        import HOME.StreamService.Qobuz.Browse.UI.LPQobuzViewController_ui
        LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.QobuzViewControllerUI, Ui_qobuzWidget, LPQobuzViewController), 'qobuz')

    updateAccountEnd = pyqtSlot()(updateAccountEnd)
    
    def showLoginPage(self):
        LPQobuzLoginViewController = LPQobuzLoginViewController
        import HOME.StreamService.Qobuz.Login.LPQobuzLoginViewController
        Ui_qobuzLoginWidget = Ui_qobuzLoginWidget
        import HOME.StreamService.Qobuz.Login.UI.LPQobuzLoginViewController_ui
        self.loginPage = LPGlobalUI.loadUI(LPUIPath.QobuzLoginViewControllerUI, Ui_qobuzLoginWidget, LPQobuzLoginViewController)
        LPGlobalUI.navigationManager.push(self.loginPage, 'qobuz login')
        logger.debug('qobuz showLoginPage ==== ')

    
    def closeLoginPage(self):
        if self.loginPage:
            LPGlobalUI.rootStackedWidget.removeWidget(self.loginPage)
            logger.debug('qobuz closeLoginPage ==== ')

    
    def beginBrowserLogin(self):
        webbrowser.open(self.redirectUrl)
        logger.debug('qobuz beginBrowserLogin ==== ')

    
    def tryPushQobuz(self):
        self.updateAccountSignal.emit()

    
    def onDeviceChanged(self, params):
        topWidget = LPGlobalUI.getTopWidget()
        if hasattr(topWidget, 'source') or topWidget.source != self.source:
            return None
        None.debug(f'''onDeviceChanged -- in top widget --> {topWidget}''')
        currentDevice = LPGlobalUI.currentDevice
        newDevice = params.get('device', None)
        if currentDevice.uuid != newDevice.uuid:
            return None
        if None.source not in newDevice.deviceStreamServiceManager.streamServiceCapability.keys():
            self.account = None
            self.unsupportedSignal.emit()
            self.popAllSourcePageSignal.emit(True)
            logger.debug('onDeviceChanged [unsupported] pop all')
            return None
        oldAccount = None.account
        newAccount = newDevice.deviceStreamServiceManager.accountForSource(self.source)
        if not newAccount:
            logger.debug('onDeviceChanged get no newAccount, try push qobuz')
            self.account = None
            self.getUserInfoForDeviceChanged(newDevice, oldAccount)
        elif not oldAccount:
            if newAccount.userId:
                self.popAllSourcePageSignal.emit(False)
                logger.debug('onDeviceChanged [not oldAccount & newAccount.userId] pop all')
                logger.debug('onDeviceChanged [not oldAccount & newAccount.userId] try push qobuz')
                self.tryPushQobuz()
                return None
        if newAccount.userId == oldAccount.userId:
            logger.debug('onDeviceChanged [newAccount.userId == oldAccount.userId] return')
            return None
        None.popAllSourcePageSignal.emit(False)
        logger.debug(f'''onDeviceChanged ==== tryPushQobuz because  newAccount.userId--{newAccount.userId} != oldAccount.userId--{oldAccount.userId} pop all''')
        self.tryPushQobuz()

    
    def getUserInfoForDeviceChanged(self, device, oldAccount):
        
        def callback(response = None, *args):
            pass
        # WARNING: Decompyle incomplete

        self.upnpModel.getUserInfo(device, self.source, callback, **('callback',))

    
    def popAllSourcePage(self, excludeTop):
        LPGlobalUI.navigationManager.popAll(self.source, excludeTop)

    popAllSourcePage = pyqtSlot(bool)(popAllSourcePage)
    
    def logout(self):
        if not getattr(self.account, 'userId', ''):
            pass
        userId = str('').strip()
        self.account = None
        LPGlobalUI.currentDevice.deviceStreamServiceManager.logoutAccountForSource(self.source)
        self.showLoginPageSignal.emit()
        self.popAllSourcePageSignal.emit(True)
    # WARNING: Decompyle incomplete

    
    def showUnsupportedPage(self):
        unsupportedPage = LPGlobalUI.loadUI(LPUIPath.MSUnsupportedPageUI, Ui_MSUnsupportedWidget, LPMSUnsupportedPage, self.source)
        LPGlobalUI.navigationManager.push(unsupportedPage, 'qobuz unsupported')
        logger.debug('qobuz showUnsupportedPage ==== ')

    
    def clearCache(self):
        cacheDir = LPUtility.cacheDir / 'Qobuz'
    # WARNING: Decompyle incomplete

    __classcell__ = None

