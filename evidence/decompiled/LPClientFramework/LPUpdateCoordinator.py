# Source Generated with Decompyle++
# File: LPUpdateCoordinator.pyc (Python 3.9)

'''
更新协调模块。
该模块负责：
1. 管理 OTA 埋点会话与补账；
2. 协调 macOS Sparkle / Windows WinSparkle 更新流程；
3. 向 UI 层暴露统一的更新检查入口。
'''
import platform
import time
import uuid
import enum
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPMacSparkleUpdater import LPMacSparkleUpdater
from LPClientFramework.LPUtility import logger
from LPClientFramework.LPWinSparkleUpdater import LPWinSparkleUpdater
_HIDDEN_BETA_FEED_MAC_ARM64 = 'https://assets.wiimhome.com/appexe/beta/appcast-beta-mac-arm64.xml'
_HIDDEN_BETA_FEED_MAC_X86_64 = 'https://assets.wiimhome.com/appexe/beta/appcast-beta-mac-x86_64.xml'
_HIDDEN_BETA_FEED_WIN_X64 = 'https://assets.wiimhome.com/appexe/beta/appcast-beta-win-x86_64.xml'

class LPOTAEventName(enum.Enum):
    '''OTA 埋点事件名称枚举。'''
    CHECK_STARTED = 'ota_check_started'
    CHECK_RESULT = 'ota_check_result'
    UPDATE_STARTED = 'ota_update_started'
    DOWNLOAD_RESULT = 'ota_download_result'
    INSTALL_STARTED = 'ota_install_started'
    FINAL_RESULT = 'ota_final_result'


class LPOTAFinalResult(enum.Enum):
    '''OTA 最终结果枚举。'''
    SUCCESS = 'success'
    FAILED = 'failed'


class LPOTAFinalErrorStage(enum.Enum):
    '''OTA 最终失败阶段枚举。'''
    DOWNLOAD = 'download'
    PRE_INSTALL = 'pre_install'
    POST_RESTART_VERIFY = 'post_restart_verify'
    SESSION_RECOVERY = 'session_recovery'
    TIMEOUT = 'timeout'


class LPOTAFinalErrorCategory(enum.Enum):
    '''OTA 最终失败错误分类枚举。'''
    DOWNLOAD = 'download'
    USER_CANCELLED = 'user_cancelled'
    DOWNLOAD_LIFECYCLE = 'download_lifecycle'
    SESSION_INTERRUPTED = 'session_interrupted'
    SESSION_RECOVERY = 'session_recovery'
    POST_INSTALL_VERIFY = 'post_install_verify'
    VERSION_COMPARE = 'version_compare'
    TIMEOUT = 'timeout'


class LPOTAFinalErrorCode(enum.Enum):
    '''OTA 最终失败错误码枚举。'''
    DOWNLOAD_FAILED = 'download_failed'
    DOWNLOAD_CANCELLED = 'download_cancelled'
    DOWNLOAD_STAGE_UNKNOWN = 'download_stage_unknown'
    RESTART_BEFORE_INSTALL = 'restart_before_install'
    MISSING_ATTEMPT_ID = 'missing_attempt_id'
    SESSION_EXPIRED = 'session_expired'
    UNEXPECTED_SESSION_STATUS = 'unexpected_session_status'
    TARGET_VERSION_NOT_REACHED = 'target_version_not_reached'
    VERSION_COMPARE_INCONCLUSIVE = 'version_compare_inconclusive'
    PROCESS_TIMEOUT = 'process_timeout'


class LPOTATelemetryTracker:
    '''OTA 埋点追踪器。'''
    OTA_TIMEOUT_MS = 300000
    OTA_SESSION_RETENTION_MS = 172800000
    
    def __init__(self, macUpdater, winUpdater = (None, None)):
        '''
        初始化 OTA 埋点追踪器。

        参数:
            macUpdater (LPMacSparkleUpdater | None): macOS 更新器实例。
            winUpdater (LPWinSparkleUpdater | None): Windows 更新器实例。
        返回:
            无
        '''
        self._macUpdater = macUpdater
        self._winUpdater = winUpdater
        self._lastUpdateCheckReason = None
        self._lastUpdateCheckTriggeredAt = None
        self._lastUpdateCallbackAt = None
        self._lastUpdateCallbackKind = None
        self._lastUpdateCheckId = None

    
    def setUpdaters(self, macUpdater, winUpdater = (None, None)):
        '''
        注入更新器实例。

        参数:
            macUpdater (LPMacSparkleUpdater | None): macOS 更新器实例。
            winUpdater (LPWinSparkleUpdater | None): Windows 更新器实例。
        返回:
            无
        '''
        self._macUpdater = macUpdater
        self._winUpdater = winUpdater

    
    def getLastUpdateCheckReason(self):
        '''
        获取最近一次检查触发来源。

        参数:
            无
        返回:
            str: 最近一次检查来源，未设置时返回空字符串。
        '''
        if not self._lastUpdateCheckReason:
            pass
        return str('')

    
    def _nowMs(self):
        '''
        获取当前毫秒时间戳。

        参数:
            无
        返回:
            int: 当前毫秒时间戳。
        '''
        return int(time.time() * 1000)

    
    def _currentUpdaterEngine(self):
        '''
        获取当前平台更新引擎标识。

        参数:
            无
        返回:
            str: Darwin 返回 sparkle，Windows 返回 winsparkle，其它返回 unknown。
        '''
        current_system = platform.system()
        if current_system == 'Darwin':
            return 'sparkle'
        if None == 'Windows':
            return 'winsparkle'

    
    def _compareVersionStrings(self, leftVersion, rightVersion):
        '''
        比较两个版本号大小。

        参数:
            leftVersion (str): 左侧版本号。
            rightVersion (str): 右侧版本号。
        返回:
            int: 左侧更大返回 1，相等返回 0，更小返回 -1。
        '''
        
        def _normalize(version_text):
            parts = []
            if not version_text:
                pass
        # WARNING: Decompyle incomplete

        left_parts = _normalize(leftVersion)
        right_parts = _normalize(rightVersion)
        max_len = max(len(left_parts), len(right_parts))
        left_parts.extend([
            0] * (max_len - len(left_parts)))
        right_parts.extend([
            0] * (max_len - len(right_parts)))
        if left_parts > right_parts:
            return 1
        if None < right_parts:
            return -1

    
    def _isSessionUpgradedByVersion(self, sessionData):
        '''
        基于会话版本信息判断当前是否已完成升级。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            bool: 当前版本达到 target_version 或高于 from_version 时返回 True，否则返回 False。
        '''
        session_data = sessionData if isinstance(sessionData, dict) else { }
        if not session_data.get('from_version', ''):
            pass
        from_version = str('')
        if not session_data.get('target_version', ''):
            pass
        target_version = str('')
        if not LPUtility.appVersion:
            pass
        current_version = str('')
        if target_version and self._compareVersionStrings(current_version, target_version) >= 0:
            return True
        if None and self._compareVersionStrings(current_version, from_version) > 0:
            return True

    
    def _logOTAEvent(self, eventName, params = (None,)):
        '''
        统一上报 OTA 埋点事件。

        参数:
            eventName (str): 事件名称。
            params (dict | None): 事件扩展参数。
        返回:
            无
        '''
        if not isinstance(eventName, str) or eventName.strip():
            return None
        event_params = {
            'platform_name': None.system(),
            'updater_engine': self._currentUpdaterEngine() }
        network_type = LPUtility.fetchNetworkType()
        if network_type:
            event_params['network_type'] = str(network_type)
        if params and isinstance(params, dict):
            event_params.update(params)
        LPGlobalUI.eventTrack.logEvent(eventName, event_params)

    
    def _readOTASession(self):
        '''
        读取当前 OTA 会话。

        参数:
            无
        返回:
            dict: OTA 会话信息。
        '''
        return LPUtility.readOTASession()

    
    def _writeOTASession(self, sessionData):
        '''
        写入 OTA 会话。

        参数:
            sessionData (dict): OTA 会话信息。
        返回:
            无
        '''
        LPUtility.writeOTASession(sessionData)

    
    def _clearOTASession(self):
        '''
        清理 OTA 会话。

        参数:
            无
        返回:
            无
        '''
        LPUtility.clearOTASession()

    
    def _enumValue(self, enumOrValue):
        '''
        将枚举值或普通值统一转换为字符串。

        参数:
            enumOrValue (enum.Enum | object): 待转换值。
        返回:
            str: 统一后的字符串值。
        '''
        if isinstance(enumOrValue, enum.Enum):
            return str(enumOrValue.value)
        if not enumOrValue:
            pass
        return None('')

    
    def _safeInt(self, rawValue, defaultValue):
        '''
        安全解析整数，失败时返回默认值。

        参数:
            rawValue (object): 待解析值。
            defaultValue (int): 解析失败时返回值。
        返回:
            int: 解析后的整数值。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _resolveAttemptIdForFinalEvent(self, sessionData):
        '''
        获取最终事件使用的 attempt_id，缺失时自动生成兜底值。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            tuple[str, bool]: (attempt_id, 是否为兜底生成)。
        '''
        if not sessionData.get('attempt_id', ''):
            pass
        attempt_id = str('').strip()
        if attempt_id:
            return (attempt_id, False)
        fallback_attempt_id = f'''{uuid.uuid4().hex}'''
        logger.warning('[ota.session] missing attempt_id while finalizing, use fallback attempt_id=%s', fallback_attempt_id)
        return (fallback_attempt_id, True)

    
    def _buildOTASessionData(self, updaterEngine, triggerSource, detail, initialStatus = (None, None, 'pending')):
        '''
        构建新的 OTA 会话数据结构。

        参数:
            updaterEngine (str): 更新引擎标识。
            triggerSource (str | None): 触发来源。
            detail (dict | None): 更新详情。
            initialStatus (str): 初始状态。
        返回:
            dict: 新会话数据。
        '''
        detail_data = detail if isinstance(detail, dict) else { }
        now_ms = self._nowMs()
        if not triggerSource and self._lastUpdateCheckReason:
            pass
        trigger_source = str('manual')
        if not self._lastUpdateCheckId:
            pass
        check_id = str('')
        if not initialStatus:
            pass
        if not updaterEngine:
            pass
        if not LPUtility.appVersion:
            pass
        if not detail_data.get('latest_version', ''):
            pass
        return {
            'attempt_id': uuid.uuid4().hex,
            'status': str('pending'),
            'trigger_source': trigger_source,
            'updater_engine': str(self._currentUpdaterEngine()),
            'from_version': str(''),
            'target_version': str(''),
            'check_id': check_id,
            'confirm_started_at_ms': now_ms,
            'started_at_ms': now_ms,
            'download_started_at_ms': 0,
            'download_finished_at_ms': 0,
            'download_duration_ms': -1,
            'download_result': '',
            'download_error_category': '',
            'download_error_code': '',
            'download_error_message': '',
            'install_started_at_ms': 0,
            'timeout_deadline_ms': now_ms + self.OTA_TIMEOUT_MS,
            'timeout_reported': False,
            'last_progress_at_ms': now_ms,
            'final_event_count': 0,
            'last_final_result': '',
            'last_final_at_ms': 0,
            'reconciled_from_timeout': False,
            'confirm_source': '' }

    
    def _ensureSessionDeadline(self, sessionData):
        '''
        确保会话存在有效超时截止时间。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            dict: 更新后的会话数据。
        '''
        session_data = sessionData if isinstance(sessionData, dict) else { }
        if not session_data.get('confirm_started_at_ms'):
            pass
        confirm_started_at_ms = self._safeInt(session_data.get('started_at_ms'), self._nowMs())
        if confirm_started_at_ms <= 0:
            confirm_started_at_ms = self._nowMs()
        session_data['confirm_started_at_ms'] = confirm_started_at_ms
        timeout_deadline_ms = self._safeInt(session_data.get('timeout_deadline_ms'), 0)
        if timeout_deadline_ms <= 0:
            if self._shouldDelayWindowsManualTimeout(session_data):
                session_data['timeout_deadline_ms'] = 0
            else:
                timeout_deadline_ms = confirm_started_at_ms + self.OTA_TIMEOUT_MS
                session_data['timeout_deadline_ms'] = timeout_deadline_ms
        return dict(session_data)

    
    def _shouldDelayWindowsManualTimeout(self, sessionData):
        '''
        判断 Windows 手动更新会话是否应延后启动超时计时。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            bool: 需要延后超时计时返回 True，否则返回 False。
        '''
        if not isinstance(sessionData, dict) or sessionData:
            return False
        if not sessionData.get('updater_engine', ''):
            pass
        updater_engine = None('').strip().lower()
        if not sessionData.get('confirm_source', ''):
            pass
        confirm_source = str('').strip().lower()
        install_started_at_ms = self._safeInt(sessionData.get('install_started_at_ms'), 0)
        download_reported = bool(sessionData.get('download_reported'))
        if updater_engine == 'winsparkle' and confirm_source == 'winsparkle_manual_click' and install_started_at_ms <= 0:
            pass
        return download_reported is not True

    
    def _armOTASessionTimeout(self, sessionData, baseTimeMs = (None,)):
        '''
        以指定起点为 OTA 会话设置新的超时截止时间。

        参数:
            sessionData (dict): OTA 会话数据。
            baseTimeMs (int | None): 超时起点毫秒时间戳；为空时使用当前时间。
        返回:
            dict: 更新后的 OTA 会话数据。
        '''
        if not isinstance(sessionData, dict) or sessionData:
            return { }
        base_time_ms = None._safeInt(baseTimeMs, self._nowMs())
        if base_time_ms <= 0:
            base_time_ms = self._nowMs()
        session_data = dict(sessionData)
        session_data['timeout_deadline_ms'] = base_time_ms + self.OTA_TIMEOUT_MS
        session_data['timeout_reported'] = False
        return dict(session_data)

    
    def _touchOTASessionProgress(self, sessionData, status = (None,)):
        '''
        刷新 OTA 会话进度时间并可选更新状态。

        参数:
            sessionData (dict): OTA 会话数据。
            status (str | None): 新状态。
        返回:
            dict: 更新后的会话数据。
        '''
        if not isinstance(sessionData, dict) or sessionData:
            return { }
        session_data = None._ensureSessionDeadline(dict(sessionData))
        if isinstance(status, str) and status.strip():
            session_data['status'] = status.strip()
        session_data['last_progress_at_ms'] = self._nowMs()
        self._writeOTASession(session_data)
        return dict(session_data)

    
    def _isActiveOTASessionStatus(self, statusText):
        '''
        判断状态是否属于活动中的 OTA 会话。

        参数:
            statusText (str): 状态文本。
        返回:
            bool: 活动态返回 True，否则返回 False。
        '''
        if not statusText:
            pass
        status = str('').strip().lower()
        return status in ('pending', 'in_progress', 'downloading', 'installing', 'awaiting_post_restart_verify', 'timeout_failed_pending_reconcile')

    
    def _isWindowsManualSession(self, sessionData):
        '''
        判断 OTA 会话是否属于 Windows 手动更新链路。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            bool: 属于 Windows 手动更新会话返回 True，否则返回 False。
        '''
        if not isinstance(sessionData, dict) or sessionData:
            return False
        if not sessionData.get('updater_engine', ''):
            pass
        updater_engine = None('').strip().lower()
        if not sessionData.get('confirm_source', ''):
            pass
        confirm_source = str('').strip().lower()
        if updater_engine == 'winsparkle':
            pass
        return confirm_source == 'winsparkle_manual_click'

    
    def _canReplaceWindowsManualSession(self, sessionData):
        '''
        判断当前 Windows 手动更新会话是否允许被新的手动检查覆盖。

        参数:
            sessionData (dict): OTA 会话数据。
        返回:
            bool: 可直接替换返回 True，否则返回 False。
        '''
        if not isinstance(sessionData, dict) or sessionData:
            return False
        if not sessionData.get('updater_engine', ''):
            pass
        updater_engine = None('').strip().lower()
        if updater_engine != 'winsparkle':
            return False
        if not sessionData.get('status', ''):
            pass
        session_status = None('').strip().lower()
        download_started_at_ms = self._safeInt(sessionData.get('download_started_at_ms'), 0)
        install_started_at_ms = self._safeInt(sessionData.get('install_started_at_ms'), 0)
        if download_started_at_ms <= 0 and install_started_at_ms <= 0:
            pass
        return session_status not in ('downloading', 'installing', 'awaiting_post_restart_verify')

    
    def _buildWindowsManualOTASessionData(self, triggerSource, detail = (None, None)):
        '''
        构建 Windows 手动检查更新所需的初始 OTA 会话数据。

        参数:
            triggerSource (str | None): 触发来源。
            detail (dict | None): 更新详情。
        返回:
            dict: 新的 Windows 手动 OTA 会话数据。
        '''
        session_data = self._buildOTASessionData('winsparkle', triggerSource, detail, 'pending', **('updaterEngine', 'triggerSource', 'detail', 'initialStatus'))
        session_data['confirm_source'] = 'winsparkle_manual_click'
        session_data['timeout_deadline_ms'] = 0
        session_data['timeout_reported'] = False
        return dict(session_data)

    
    def _classifyDownloadFinalError(self, errorCategory, errorCode = ('', '')):
        '''
        根据下载错误信息映射 OTA 最终失败分类。

        参数:
            errorCategory (str): 下载错误分类。
            errorCode (str): 下载错误码。
        返回:
            tuple[LPOTAFinalErrorCategory, LPOTAFinalErrorCode]: 规范化后的分类与错误码。
        '''
        if not errorCategory:
            pass
        normalized_category = str('').strip().lower()
        if not errorCode:
            pass
        normalized_code = str('').strip().lower()
        if normalized_category == 'user_cancelled' or normalized_code == 'download_cancelled':
            return (LPOTAFinalErrorCategory.USER_CANCELLED, LPOTAFinalErrorCode.DOWNLOAD_CANCELLED)
        if None == 'download_lifecycle_unknown' or normalized_code == 'unknown_stage':
            return (LPOTAFinalErrorCategory.DOWNLOAD_LIFECYCLE, LPOTAFinalErrorCode.DOWNLOAD_STAGE_UNKNOWN)
        return (None.DOWNLOAD, LPOTAFinalErrorCode.DOWNLOAD_FAILED)

    
    def _emitOTAFinalResult(self, sessionData, result, errorStage, errorCategory, errorCode, errorMessage, extraParams = ('', '', '', '', None)):
        '''
        统一上报 ota_final_result 事件。

        参数:
            sessionData (dict): OTA 会话数据。
            result (LPOTAFinalResult | str): OTA 最终结果。
            errorStage (LPOTAFinalErrorStage | str): 失败阶段。
            errorCategory (LPOTAFinalErrorCategory | str): 失败分类。
            errorCode (LPOTAFinalErrorCode | str): 失败错误码。
            errorMessage (str): 原始错误信息。
            extraParams (dict | None): 额外补充字段。
        返回:
            dict: 已上报的最终事件参数。
        '''
        session_data = sessionData if isinstance(sessionData, dict) else { }
        now_ms = self._nowMs()
        if not session_data.get('confirm_started_at_ms'):
            pass
        confirm_started_at_ms = self._safeInt(session_data.get('started_at_ms'), now_ms)
        if confirm_started_at_ms <= 0:
            confirm_started_at_ms = now_ms
        install_started_at_ms = self._safeInt(session_data.get('install_started_at_ms'), 0)
        download_started_at_ms = self._safeInt(session_data.get('download_started_at_ms'), 0)
        download_finished_at_ms = self._safeInt(session_data.get('download_finished_at_ms'), 0)
        download_duration_ms = self._safeInt(session_data.get('download_duration_ms'), -1)
        if download_duration_ms < 0 and download_started_at_ms > 0 and download_finished_at_ms >= download_started_at_ms:
            download_duration_ms = download_finished_at_ms - download_started_at_ms
        install_duration_ms = -1
        if install_started_at_ms > 0:
            install_duration_ms = max(0, now_ms - install_started_at_ms)
        end_to_end_duration_ms = max(0, now_ms - confirm_started_at_ms)
        (attempt_id, is_recovered_attempt_id) = self._resolveAttemptIdForFinalEvent(session_data)
        if not session_data.get('from_version', ''):
            pass
        if not session_data.get('target_version', ''):
            pass
        if not LPUtility.appVersion:
            pass
        if not errorMessage:
            pass
        final_payload = {
            'attempt_id': attempt_id,
            'result': self._enumValue(result),
            'from_version': str(''),
            'target_version': str(''),
            'current_version': str(''),
            'confirm_started_at_ms': confirm_started_at_ms,
            'download_started_at_ms': download_started_at_ms,
            'download_finished_at_ms': download_finished_at_ms,
            'install_started_at_ms': install_started_at_ms,
            'download_duration_ms': download_duration_ms,
            'end_to_end_duration_ms': end_to_end_duration_ms,
            'install_duration_ms': install_duration_ms,
            'error_stage': self._enumValue(errorStage),
            'error_category': self._enumValue(errorCategory),
            'error_code': self._enumValue(errorCode),
            'error_message_raw': str('')[:100],
            'attempt_id_recovered': bool(is_recovered_attempt_id) }
        if isinstance(extraParams, dict):
            final_payload.update(extraParams)
        self._logOTAEvent(LPOTAEventName.FINAL_RESULT.value, final_payload)
        return final_payload

    
    def _emitOTAFinalFailure(self, sessionData, errorStage, errorCategory, errorCode, errorMessage, extraParams = ('', None)):
        '''
        统一上报 OTA 最终失败事件。

        参数:
            sessionData (dict): OTA 会话数据。
            errorStage (LPOTAFinalErrorStage | str): 失败阶段。
            errorCategory (LPOTAFinalErrorCategory | str): 失败分类。
            errorCode (LPOTAFinalErrorCode | str): 失败错误码。
            errorMessage (str): 原始错误信息。
            extraParams (dict | None): 额外补充字段。
        返回:
            dict: 已上报的最终失败参数。
        '''
        return self._emitOTAFinalResult(sessionData, LPOTAFinalResult.FAILED, errorStage, errorCategory, errorCode, errorMessage, extraParams, **('errorStage', 'errorCategory', 'errorCode', 'errorMessage', 'extraParams'))

    
    def _reportOTAFinalResult(self, sessionData, result, errorStage, errorCategory, errorCode, errorMessage, keepSession, nextStatus, reconciledFromTimeout = ('', '', '', '', False, 'completed', False)):
        '''
        上报 OTA 最终结果并更新会话持久化状态。

        参数:
            sessionData (dict): OTA 会话数据。
            result (LPOTAFinalResult | str): 最终结果。
            errorStage (LPOTAFinalErrorStage | str): 错误阶段。
            errorCategory (LPOTAFinalErrorCategory | str): 错误分类。
            errorCode (LPOTAFinalErrorCode | str): 错误码。
            errorMessage (str): 原始错误信息。
            keepSession (bool): 是否保留会话。
            nextStatus (str): 保留会话时写入的新状态。
            reconciledFromTimeout (bool): 是否超时后纠偏事件。
        返回:
            dict: 最终事件参数。
        '''
        session_data = dict(sessionData) if isinstance(sessionData, dict) else { }
        session_data = self._ensureSessionDeadline(session_data)
        final_event_count = self._safeInt(session_data.get('final_event_count'), 0) + 1
        session_data['final_event_count'] = final_event_count
        session_data['last_final_result'] = self._enumValue(result)
        session_data['last_final_at_ms'] = self._nowMs()
        if reconciledFromTimeout:
            session_data['reconciled_from_timeout'] = True
        final_payload = self._emitOTAFinalResult(session_data, result, errorStage, errorCategory, errorCode, errorMessage, {
            'final_event_index': final_event_count,
            'reconciled_from_timeout': bool(reconciledFromTimeout) }, **('result', 'errorStage', 'errorCategory', 'errorCode', 'errorMessage', 'extraParams'))
        if keepSession:
            if not nextStatus:
                pass
            session_data['status'] = str(session_data.get('status', ''))
            self._writeOTASession(session_data)
        else:
            self._clearOTASession()
        return final_payload

    
    def _reportOTAFinalFailure(self, sessionData, errorStage, errorCategory, errorCode, errorMessage, keepSession, nextStatus, reconciledFromTimeout = ('', False, 'completed', False)):
        '''
        上报 OTA 最终失败并更新会话持久化状态。

        参数:
            sessionData (dict): OTA 会话数据。
            errorStage (LPOTAFinalErrorStage | str): 错误阶段。
            errorCategory (LPOTAFinalErrorCategory | str): 错误分类。
            errorCode (LPOTAFinalErrorCode | str): 错误码。
            errorMessage (str): 原始错误信息。
            keepSession (bool): 是否保留会话。
            nextStatus (str): 保留会话时写入的新状态。
            reconciledFromTimeout (bool): 是否超时后纠偏事件。
        返回:
            dict: 最终事件参数。
        '''
        return self._reportOTAFinalResult(sessionData, LPOTAFinalResult.FAILED, errorStage, errorCategory, errorCode, errorMessage, keepSession, nextStatus, reconciledFromTimeout, **('errorStage', 'errorCategory', 'errorCode', 'errorMessage', 'keepSession', 'nextStatus', 'reconciledFromTimeout'))

    
    def _currentUpdaterLastCheckDetail(self):
        '''
        获取当前平台更新器最近一次检查详情。

        参数:
            无
        返回:
            dict: 最近一次检查详情；不可用时返回空字典。
        '''
        current_system = platform.system()
        if current_system == 'Darwin' and self._macUpdater is not None:
            return self._macUpdater.getLastCheckDetail()
        if None == 'Windows' and self._winUpdater is not None:
            return self._winUpdater.getLastCheckDetail()

    
    def _ensureOTAPendingSession(self, updaterEngine, triggerSource, detail, initialStatus = (None, None, 'pending')):
