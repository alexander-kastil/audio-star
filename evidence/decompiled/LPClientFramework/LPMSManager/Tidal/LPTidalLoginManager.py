# Source Generated with Decompyle++
# File: LPTidalLoginManager.pyc (Python 3.9)

'''
TIDAL 登录管理器。
'''
import json
import sys
import threading
import time
import urllib.parse as urllib
import webbrowser
from typing import Any, Dict, Iterable, Optional
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
import LPGlobalUI
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework import LPUtility
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger
from LPClientFramework.util.aes import AESCipher

class LPTidalLoginManager(QObject):
    '''负责 TIDAL OAuth code 登录、设备账号同步、登出和订阅状态更新。'''
    _instance: Optional['LPTidalLoginManager'] = None
    USER_INFO_VERSION = '2'
    TOKEN_REFRESH_LEEWAY_SECONDS = 300
    TOKEN_REFRESH_TIMEOUT_SECONDS = 8
    loadingStateChanged = pyqtSignal()
    errorMessageChanged = pyqtSignal()
    accountStateChanged = pyqtSignal()
    loginSucceeded = pyqtSignal(dict)
    logoutSucceeded = pyqtSignal()
    showLoginPageSignal = pyqtSignal()
    showHomePageSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        '''
        初始化登录管理器。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._provider = LPTidalDataProvider(self, **('parent',))
        self._store = LPTidalStore.instance()
        self._upnpModel = LPUpnpAsyncDataModel()
        self._account = None
        self.source = LPPlayListSource.Tidal.value
        self._is_loading = False
        self._error_message = ''
        self._pending_user_info_device_uuid = ''
        self._pending_entry_device_uuid = ''
        self._pending_oauth_login_device_uuid = ''
        self._shell_page = None
        self._shell_device_uuid = ''
        self._refresh_lock = threading.RLock()
        self._refresh_condition = threading.Condition(self._refresh_lock)
        self._refreshing_device_uuid = ''
        self._registerObservers()
        self.showLoginPageSignal.connect(self.showLoginPage)
        self.showHomePageSignal.connect(self.showHomePage)
        self.syncAccountFromDevice(getattr(LPGlobalUI, 'currentDevice', None))

    
    def instance(cls = None, parent = None):
        '''
        返回登录管理器单例。

        :param parent: 可选父对象。
        :return: 登录管理器单例。
        '''
        if cls._instance is None:
            cls._instance = cls(parent)
        elif parent is not None and cls._instance.parent() is None:
            cls._instance.setParent(parent)
        return cls._instance

    instance = None(instance)
    
    def isLoading(self = None):
        '''
        返回当前是否正在执行登录或登出请求。

        :return: 正在请求返回 True。
        '''
        return self._is_loading

    isLoading = None(isLoading)
    
    def errorMessage(self = None):
        '''
        返回最近一次登录或登出的错误信息。

        :return: 错误信息。
        '''
        return self._error_message

    errorMessage = None(errorMessage)
    
    def currentUserId(self = None):
        '''
        返回当前 TIDAL 用户 ID。

        :return: 用户 ID。
        '''
        account = self._account
        if not getattr(account, 'userId', ''):
            pass
        return str('')

    currentUserId = None(currentUserId)
    
    def login(self = None, username = None, password = pyqtSlot(str, str)):
        '''
        使用用户名和密码登录 TIDAL。

        :param username: 用户名或邮箱。
        :param password: 密码。
        :return: None。
        '''
        if not username:
            pass
        normalized_username = str('').strip()
        if not password:
            pass
        normalized_password = str('')
        if not normalized_username or normalized_password:
            self._setErrorMessage('Please enter your username and password.')
            return None
        None._setLoading(True)
        self._setErrorMessage('')
        result = self._provider.loginByUsername(normalized_username, normalized_password)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._setLoading(False)
            self._setErrorMessage(self._errorMessageFromResult(result, 'Invalid email or password. Please try again.'))
            logger.warning('[TIDAL] username login failed')
            return None
        account_state = None._extractAccountState(result.get('data'))
        if not account_state.get('userId', ''):
            pass
        user_id = str('').strip()
        if not user_id:
            self._setLoading(False)
            self._setErrorMessage('Login response did not include a user ID.')
            logger.warning('[TIDAL] username login missing userId')
            return None
        None._writeAccountState(account_state, normalized_username, **('fallbackUserName',))
        self._setLoading(False)
        self.loginSucceeded.emit(dict(account_state))
    # WARNING: Decompyle incomplete

    login = None(login)
    
    def logout(self = None):
        '''
        登出当前 TIDAL 账号。
        通过设备 UPnP UserLogout 完成登出，PC 不直接调用 Tidal HTTP API。

        :return: None。
        '''
        if not self._store.accountState.get('userId', ''):
            pass
        user_id = str('').strip()
        device = getattr(LPGlobalUI, 'currentDevice', None)
    # WARNING: Decompyle incomplete

    logout = None(logout)
    
    def _performLogoutCleanup(self = None, userId = None):
        '''
        执行登出后的统一清理，主动登出和被动登出共用。

        清空 Store 全部用户业务状态、DataProvider 的 HTTP 缓存，
        并取消图片服务在途下载请求；TIDAL 没有 tokenProvider，token 随
        Store 的 accountState 一起被 setAccountState(False,...) 清空。

        :param userId: 登出前的用户 ID；为空时回退读取 store 当前值。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def clearErrorMessage(self = None):
        '''
        清空登录错误文案。

        :return: None。
        '''
        self._setErrorMessage('')

    clearErrorMessage = None(clearErrorMessage)
    
    def beginBrowserLogin(self = None):
        '''
        从设备读取 TIDAL 登录参数并打开系统浏览器登录页。

        :return: None。
        '''
        target_device = getattr(LPGlobalUI, 'currentDevice', None)
        if not target_device is None or hasattr(target_device, 'deviceStreamServiceManager'):
            self._setErrorMessage('No device is available for TIDAL login.')
            return None
    # WARNING: Decompyle incomplete

    beginBrowserLogin = None(beginBrowserLogin)
    
    def loginUrlFromUserInfo(self = None, userinfo = None):
        '''
        根据设备返回的 TIDAL 登录参数构造 Android 一致的 authorize URL。

        :param userinfo: 设备 GetUserInfo 返回的用户信息。
        :return: 可打开的登录 URL，缺参数时返回空字符串。
        '''
        if not isinstance(userinfo, dict):
            return ''
        client_id = None._decodeDeviceValue(self._firstStringValue(userinfo, 'clientId', 'client_id'))
        redirect_url = self._firstStringValue(userinfo, 'redirectUrl', 'redirectURI', 'redirect_uri')
        if not client_id or redirect_url:
            return ''
        decoded_redirect_url = None.parse.unquote(redirect_url)
        query = urllib.parse.urlencode({
            'lang': 'en',
            'response_type': 'code',
            'redirect_uri': decoded_redirect_url,
            'client_id': client_id,
            'state': 'pc',
            'restrictSignup': 'true' })
        return f'''https://login.tidal.com/authorize?{query}'''

    
    def tryPushTidal(self = None):
        '''
        尝试进入 TIDAL；设备已登录时进入首页，未登录时进入登录页。

        :return: None。
        '''
        target_device = getattr(LPGlobalUI, 'currentDevice', None)
        if not target_device is None or hasattr(target_device, 'deviceStreamServiceManager'):
            self._pending_entry_device_uuid = ''
            self.showLoginPageSignal.emit()
            return None
        if not getattr(target_device, 'uuid', ''):
            pass
        device_uuid = None('')
        self._pending_entry_device_uuid = device_uuid
        account = self.syncAccountFromDevice(target_device, False, **('fetchIfMissing',))
        if account:
            self._pending_entry_device_uuid = ''
            self.showHomePageSignal.emit()
            return None
        if not None._deviceSupportsTidal(target_device):
            self._pending_entry_device_uuid = ''
            self.showLoginPageSignal.emit()
            return None
        None._fetchAccountForEntry(target_device)

    tryPushTidal = None(tryPushTidal)
    
    def syncAccountFromDevice(self = None, device = None, fetchIfMissing = pyqtSlot(object, object, **('result',))):
        '''
        从设备读取 TIDAL 登录状态并同步到 Store。

        :param device: 设备对象，缺省时使用当前设备。
        :param fetchIfMissing: 本地未缓存账号时是否主动向设备拉取。
        :return: 当前账号对象或 None。
        '''
        target_device = device if device is not None else getattr(LPGlobalUI, 'currentDevice', None)
        if not target_device is None or hasattr(target_device, 'deviceStreamServiceManager'):
            logger.debug('[TIDAL][LoginState] syncAccountFromDevice no device fetchIfMissing=%s', fetchIfMissing)
            self._account = None
            self._store.setAccountState(False, '', '', { })
            return None
        account = None.deviceStreamServiceManager.accountForSource(self.source)
        if not getattr(target_device, 'uuid', ''):
            pass
        logger.debug('[TIDAL][LoginState] syncAccountFromDevice device=%s fetchIfMissing=%s has_account=%s userId=%s has_token=%s has_session=%s store_before_logged_in=%s', str(''), fetchIfMissing, account is not None, str('') if account is not None else '', bool(str('').strip()) if account is not None else False, bool(str('').strip()) if account is not None else False, bool(self._store.accountState.get('isLoggedIn', False)))
        if self._isAccountLoggedIn(account):
            self._account = account
            self._writeAccountState(self._account_to_state(account))
            if not getattr(target_device, 'uuid', ''):
                pass
            if not getattr(account, 'userId', ''):
                pass
            logger.debug('[TIDAL][LoginState] syncAccountFromDevice accepted account device=%s userId=%s', str(''), str(''))
            return account
        self._account = None
        self._store.setAccountState(False, '', '', { })
        if not getattr(target_device, 'uuid', ''):
            pass
        logger.debug('[TIDAL][LoginState] syncAccountFromDevice cleared store device=%s fetchIfMissing=%s', str(''), fetchIfMissing)
        if fetchIfMissing:
            self.fetchAccountFromDevice(target_device)

    syncAccountFromDevice = None(syncAccountFromDevice)
    
    def fetchAccountFromDevice(self = None, device = None):
        '''
        主动从设备读取 TIDAL 用户信息并注册到设备音源服务。

        :param device: 设备对象，缺省时使用当前设备。
        :return: None。
        '''
        target_device = device if device is not None else getattr(LPGlobalUI, 'currentDevice', None)
        if not target_device is None or hasattr(target_device, 'deviceStreamServiceManager'):
            return None
        if not None._deviceSupportsTidal(target_device):
            return None
        if not getattr(target_device, 'uuid', ''):
            pass
        device_uuid = None('')
        if device_uuid and self._pending_user_info_device_uuid == device_uuid:
            logger.debug('[TIDAL][LoginState] fetchAccountFromDevice skip pending device=%s', device_uuid)
            return None
        self._pending_user_info_device_uuid = None
        logger.debug('[TIDAL][LoginState] fetchAccountFromDevice request device=%s version=%s', device_uuid, self.USER_INFO_VERSION)
        
        def callback(response = None, callback_device = None):
            '''
            处理设备 GetUserInfo 返回并同步登录态。

            :param response: 设备返回结果。
            :param callback_device: 发起请求的设备。
            :return: None。
            '''
            if not getattr(callback_device, 'uuid', ''):
                pass
            callback_uuid = str('')
            if self._pending_user_info_device_uuid == callback_uuid:
                self._pending_user_info_device_uuid = ''
            current_device = getattr(LPGlobalUI, 'currentDevice', None)
            if current_device is not None:
                if not getattr(current_device, 'uuid', ''):
                    pass
                if callback_uuid != str(''):
                    return None
                userinfo = None._userInfoFromResponse(response)
            user_payload = userinfo.get('user', { }) if isinstance(userinfo, dict) else { }
            logger.debug('[TIDAL][LoginState] fetchAccountFromDevice response device=%s status=%s keys=%s user_keys=%s userId=%s has_token=%s has_session=%s', callback_uuid, response.get('status_code', 0) if isinstance(response, dict) else 0, sorted(userinfo.keys()) if isinstance(userinfo, dict) else [], sorted(user_payload.keys()) if isinstance(user_payload, dict) else [], self._userIdFromUserInfo(userinfo), bool(self._tokenFromUserInfo(userinfo)), bool(self._firstStringValue(userinfo, 'sessionId', 'session_id', 'sid')))
            if not self._isUserInfoLoggedIn(userinfo):
                self._account = None
                self._store.setAccountState(False, '', '', { })
                logger.debug('[TIDAL][LoginState] fetchAccountFromDevice cleared store because response is not logged in device=%s', callback_uuid)
                self.accountStateChanged.emit()
                return None
            None.deviceStreamServiceManager.registerAccountForSource(self.source, userinfo)
            self.syncAccountFromDevice(callback_device, False, **('fetchIfMissing',))

        self._upnpModel.getUserInfo(target_device, self.source, callback, target_device)

    
    def ensureFreshToken(self = None, force = None):
        '''
        确保当前 TIDAL token 仍在安全有效期内，必要时从设备同步新账号信息。

        :param force: 是否忽略过期时间并强制同步。
        :return: 有可用登录 token 返回 True。
        '''
        target_device = getattr(LPGlobalUI, 'currentDevice', None)
        if not target_device is None or hasattr(target_device, 'deviceStreamServiceManager'):
            return False
        if not None._deviceSupportsTidal(target_device):
            return False
        if not None and self._shouldRefreshToken():
            if not self._store.accountState.get('token', ''):
                pass
            return bool(str('').strip())
        return None._fetchAccountFromDeviceBlocking(target_device, '401_retry' if force else 'scheduled', **('reason',))

    
    def _fetchAccountForEntry(self = None, device = None):
        '''
        为侧边栏入口读取设备 TIDAL 账号，并根据结果进入首页或登录页。

        :param device: 当前设备对象。
        :return: None。
        '''
        
        def callback(response = None, callback_device = None):
