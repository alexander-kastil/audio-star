# Source Generated with Decompyle++
# File: LPFeedbackManager.pyc (Python 3.9)

'''PC Feedback 单向提交流程编排器。'''
import secrets
import shutil
import threading
import time
import uuid
from dataclasses import replace
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework.LPFeedback.LPFeedbackApiClient import LPFeedbackApiClient
from LPClientFramework.LPFeedback.LPFeedbackConfig import requireAesKey, requireFreshdeskCredentials
from LPClientFramework.LPFeedback.LPFeedbackEventTrack import LPFeedbackErrorCode, LPFeedbackEventTrack
from LPClientFramework.LPFeedback.LPFeedbackJsonStore import LPFeedbackJsonStore
from LPClientFramework.LPFeedback.LPFirmwareLogCollector import LPFirmwareLogCollector
from LPClientFramework.LPFeedback.LPFeedbackLogPackager import LPFeedbackLogPackager, LPFeedbackWorkDirectoryError
from LPClientFramework.LPFeedback.LPFeedbackModels import LPFeedbackSubmission
from LPClientFramework.LPFeedback.LPFeedbackS3Uploader import LPFeedbackS3Uploader
from LPClientFramework.LPFeedback.LPFeedbackStsClient import LPFeedbackStsClient
from LPClientFramework.LPUtility import logger, userDataDir

class LPFeedbackSession:
    '''单次反馈提交的会话状态容器。

    每次 submit() 都会创建独立实例，用于隔离超时标记、埋点计数器、超时计时器
    与固件日志目录，使多次提交（含上一次超时解锁后仍在后台运行的那次）之间
    互不影响。
    '''
    
    def __init__(self, submissionId, timeoutSeconds):
        '''初始化一次提交的会话状态。

        参数:
            submissionId (str): 本地提交 ID。
            timeoutSeconds (float): 前台等待超时秒数。
        返回:
            无。
        '''
        self.submissionId = submissionId
        self.timeoutSeconds = timeoutSeconds
        self.timeoutEmitted = False
        self.finished = threading.Event()
        self.retryCount = 0
        self.count3001 = 0
        self.count3002 = 0
        self.s3UploadElapsedMs = 0
        self.startedAt = time.time()
        self.timeoutTimer = None
        self.firmwareDirectory = None



class LPFeedbackManager(QObject):
    '''执行每次提交的工单创建、日志上传和工单回填，不保存或恢复上传队列。

    每次 submit() 都作为一次独立过程执行：不检查是否已有提交在进行，
    新提交持有自己的会话状态与后台线程，与未完成的旧提交互不影响。
    '''
    FEEDBACK_TIMEOUT_SECONDS = 15
    MAX_ATTEMPTS = 3
    submissionCompleted = pyqtSignal()
    submissionFailed = pyqtSignal(str)
    uploadFailed = pyqtSignal(str)
    STAGE_ERROR_CODES = {
        'creating_ticket': LPFeedbackErrorCode.CREATE_TICKET,
        'requesting_sts': LPFeedbackErrorCode.UPLOAD_API,
        'uploading_s3': LPFeedbackErrorCode.UPLOAD_S3,
        'updating_ticket': LPFeedbackErrorCode.UPDATE_TICKET,
        'packing_logs': LPFeedbackErrorCode.PACK_LOGS }
    
    def __init__(self = None, parent = None, jsonStore = None, apiClient = None, stsClient = None, s3Uploader = None, packagerFactory = None, deviceListProvider = None, timeoutSeconds = ((None, None, None, None, None, None, None, None),)):
        '''初始化任务编排器及可替换的基础设施依赖。

        参数:
            parent (QObject|None): Qt 父对象。
            jsonStore (LPFeedbackJsonStore|None): 可注入的状态文件存储。
            apiClient (LPFeedbackApiClient|None): 可注入的 Freshdesk 客户端。
            stsClient (LPFeedbackStsClient|None): 可注入的 STS 客户端。
            s3Uploader (LPFeedbackS3Uploader|None): 可注入的 S3 上传器。
            packagerFactory (callable|None): 接收 AES 密钥并返回打包器的工厂。
            deviceListProvider (callable|None): 返回当前已发现 LPDevice 列表的函数。
            timeoutSeconds (int|None): 前台等待超时秒数，超时后强制按成功解锁 UI；缺省 15s。
        返回:
            无。
        '''
        super().__init__(parent)
        feedbackRoot = Path(userDataDir) / 'Feedback'
        if not jsonStore:
            pass
        self._jsonStore = LPFeedbackJsonStore(feedbackRoot / 'state')
        self._apiClient = apiClient
        if not stsClient:
            pass
        self._stsClient = LPFeedbackStsClient()
        if not s3Uploader:
            pass
        self._s3Uploader = LPFeedbackS3Uploader()
        if not packagerFactory:
            pass
        
        self._packagerFactory = lambda aesKey = None: LPFeedbackLogPackager(feedbackRoot / 'work', aesKey)
        self._deviceListProvider = deviceListProvider
        self._timeoutSeconds = self.FEEDBACK_TIMEOUT_SECONDS if timeoutSeconds is None else timeoutSeconds
        self._threads = []
        self._sessionLock = threading.RLock()
        self._sessions = { }

    
    def submit(self, request):
        '''在后台启动一次反馈发送任务，每次调用都是独立的提交过程。

        不检查是否已有提交在进行：新提交创建自己的会话状态、超时计时器与后台
        线程，与尚未完成的旧提交互不影响（旧提交若已超时解锁 UI，其后台结果
        只写日志与埋点，不再向前台发信号）。

        参数:
            request (LPFeedbackRequest): 已完成 UI 校验的反馈请求。
        返回:
            str: 本次发送的本地提交 ID。
        '''
        submissionId = uuid.uuid4().hex
        session = self._beginSession(submissionId)
        if self._hasOtherActiveSession(submissionId):
            logger.info('[Feedback] submit while another submission is still active, run as a new independent submission.')
        session.timeoutTimer = threading.Timer(self._timeoutSeconds, self._onSubmissionTimeout, (submissionId,), **('args',))
        session.timeoutTimer.daemon = True
        session.timeoutTimer.start()
        thread = threading.Thread(self._runSubmission, (submissionId, request), True, 'LPFeedback-%s' % submissionId[:8], **('target', 'args', 'daemon', 'name'))
        self._threads.append(thread)
        thread.start()
        return submissionId

    
    def _beginSession(self, submissionId):
        '''登记并返回一次提交的独立会话状态（已登记时复用原会话）。

        参数:
            submissionId (str): 本地提交 ID。
        返回:
            LPFeedbackSession: 该提交的会话状态。
        '''
        with self._sessionLock:
            session = self._sessions.get(submissionId)
            if session is None:
                session = LPFeedbackSession(submissionId, self._timeoutSeconds)
                self._sessions[submissionId] = session
            None(None, None, None)
            return session
            with None:
                if not None:
                    pass

    
    def _hasOtherActiveSession(self, submissionId):
        '''判断当前是否还有其他提交正在进行。

        参数:
            submissionId (str): 本次提交 ID。
        返回:
            bool: 存在其他进行中的提交时为 True。
        '''
        with self._sessionLock:
            None(None, None, None)
            return None((lambda .0 = None: for key in .0:
key != submissionId)(self._sessions))
            with None:
                if not None:
                    pass

    
    def _endSession(self, session):
        '''结束一次提交会话，并返回前台是否已因超时解锁过 UI。

        在同一把会话锁内完成「解除登记 + 标记结束 + 读取超时标记」，与超时
        计时线程的判定互斥，因此 ``submissionCompleted`` 对每次提交恰好发射一次。

        参数:
            session (LPFeedbackSession): 待结束的会话状态。
        返回:
            bool: 该会话是否已因超时向前台解锁过 UI。
        '''
        with self._sessionLock:
            self._sessions.pop(session.submissionId, None)
            session.finished.set()
            timeoutEmitted = session.timeoutEmitted
            None(None, None, None)
        with None:
            if not None:
                pass
        if session.timeoutTimer is not None:
            session.timeoutTimer.cancel()
        return timeoutEmitted

    
    def _runSubmission(self, submissionId, request):
        '''执行创建工单、上传 ZIP 与回填工单的完整后台流程。

        参数:
            submissionId (str): 本地提交 ID。
            request (LPFeedbackRequest): 原始反馈请求。
        返回:
            None。
        '''
        session = self._beginSession(submissionId)
        request = self._convertLongSubject(request)
        confirmationId = format(secrets.randbelow(65535) + 1, 'x')
        submission = LPFeedbackSubmission(submissionId, confirmationId, request)
        record = submission.toRecord()
        stage = 'creating_ticket'
        workPath = None
        packager = None
        ticketCreated = False
        submissionCompleted = False
        archivePath = None
        credential = None
        session.firmwareDirectory = self._firmwareLogDirectoryFor(session, request)
    # WARNING: Decompyle incomplete

    
    def _convertLongSubject(self, request):
        '''subject 超过 200 字时对齐安卓 convertLongSubject 改写请求。

        subject 改为用户邮箱，原 subject 拼接到 description 开头，
        避免工单网关因主题过长拒绝创建。

        参数:
            request (LPFeedbackRequest): 原始反馈请求。
        返回:
            LPFeedbackRequest: 转换后的请求；未超长时返回原请求。
        '''
        if request.subject or len(request.subject) <= 200:
            return request
        return None(request, request.email, '%s\n\n%s' % (request.subject, request.description), **('subject', 'description'))

    
    def _createTicketWithRetry(self, apiClient, request, session, attempts = (MAX_ATTEMPTS,)):
        '''创建工单，失败时最多重试指定次数（对齐安卓 SubmitTicketRequest）。

        参数:
            apiClient (LPFeedbackApiClient): 工单客户端。
            request (LPFeedbackRequest): 反馈请求。
            session (LPFeedbackSession): 本次提交会话，用于累计重试次数。
            attempts (int): 最大尝试次数。
        返回:
            str: 工单 ID。
        异常:
            Exception: 全部尝试失败时抛出最后一次异常。
        '''
        lastError = None
    # WARNING: Decompyle incomplete

    
    def _uploadWithRetry(self, s3Uploader, archivePath, credential, session, attempts = (MAX_ATTEMPTS,)):
        '''上传 S3，失败时最多重试指定次数（对齐安卓 MAX_RETRY_TIMES）。

        参数:
            s3Uploader (LPFeedbackS3Uploader): S3 上传器。
            archivePath (Path): ZIP 路径。
            credential (LPFeedbackStsCredential): 临时凭证。
            session (LPFeedbackSession): 本次提交会话，用于累计重试与上传耗时。
            attempts (int): 最大尝试次数。
        返回:
            None。
        异常:
            Exception: 全部尝试失败时抛出最后一次异常。
        '''
        lastError = None
    # WARNING: Decompyle incomplete

    
    def _emitExceptionEvent(self, stage, error, message, submission, session, credential, archivePath = (None, None, None)):
        '''按失败阶段上报 feedback_exception（文档码 3001/3002/3004/3005/3006/3007）。

        3006 与 3007 同属 packing_logs 阶段，按异常类型区分：工作/暂存目录创建
        失败为 3006（sub_error_code 固定 -1），其余打包或加密失败为 3007。
        sub_error_code 取下层 HTTP 状态码，非 HTTP 失败统一为 0。

        参数:
            stage (str): 失败所在阶段。
            error (BaseException): 捕获到的异常。
            message (str): 错误描述文本。
            submission (LPFeedbackSubmission): 当前提交对象，用于提取确认号。
            session (LPFeedbackSession|None): 本次提交会话，用于 3002 的上传耗时上下文。
            credential (LPFeedbackStsCredential|None): 已取得的临时凭证，用于 3002 上下文。
            archivePath (Path|str|None): 已生成的 ZIP 路径，用于 3002 的文件大小。
        返回:
            None。
        '''
        confirmId = getattr(submission, 'confirmationId', '') if submission is not None else ''
        errorCode = self.STAGE_ERROR_CODES.get(stage)
        if errorCode is None:
            return None
        if None == 'packing_logs' and isinstance(error, LPFeedbackWorkDirectoryError):
            errorCode = LPFeedbackErrorCode.LOG_DIRECTORY
        if errorCode == LPFeedbackErrorCode.LOG_DIRECTORY:
            LPFeedbackEventTrack.exception(errorCode, message, confirmId, LPFeedbackEventTrack.LOG_DIRECTORY_SUB_ERROR_CODE, **('errorDescription', 'confirmId', 'subErrorCode'))
            return None
        extraParams = None
        if errorCode == LPFeedbackErrorCode.UPLOAD_S3:
            extraParams = self._collectS3Context(session, credential, archivePath)
    # WARNING: Decompyle incomplete

    
    def _collectS3Context(self, session, credential, archivePath):
        '''构造 3002 的 S3 上下文参数，缺失字段留空。

        参数:
            session (LPFeedbackSession|None): 本次提交会话，用于取最近一次上传耗时。
            credential (LPFeedbackStsCredential|None): 已取得的临时凭证。
            archivePath (Path|str|None): 已生成的 ZIP 路径。
        返回:
            dict: s3_region / s3_bucket / s3_file_size / s3_upload_time。
        '''
        fileSize = 0
    # WARNING: Decompyle incomplete

    
    def _emitCompleteEvent(self, session, submissionCompleted, submission):
        '''上报 feedback_complete（3003），每次提交会话仅 1 条。

        result 取管道真实结果，不受前台超时解锁 UI 的影响；计数取本次会话累计值，
        因此并发提交之间不会互相污染埋点。

        参数:
            session (LPFeedbackSession): 本次提交会话状态。
            submissionCompleted (bool): 管道是否真正完成。
            submission (LPFeedbackSubmission|None): 当前提交对象。
        返回:
            None。
        '''
        if not session.startedAt:
            pass
        startedAt = time.time()
        durationMs = max(int((time.time() - startedAt) * 1000), 0)
        attachmentCount = 0
        if submission is not None:
            if not getattr(submission.request, 'attachmentPaths', None):
                pass
            attachmentCount = len([])
        LPFeedbackEventTrack.complete(submissionCompleted, getattr(submission, 'confirmationId', '') if submission is not None else '', session.retryCount, session.count3001, session.count3002, durationMs, attachmentCount, **('result', 'confirmId', 'retryCount', 'count3001', 'count3002', 'durationMs', 'attachmentCount'))

    
    def _onSubmissionTimeout(self, submissionId):
        '''指定提交超过超时秒数时强制按成功提示解锁 UI。

        对齐安卓 FEEDBACK_TIMEOUT：超时直接走成功提示，避免 UI 一直 busy；
        被超时解锁的提交在后台继续执行，最终结果只记录日志与埋点，不再向前台发信号
        （其会话标记使对应线程结束时不再重复发射信号）。

        参数:
            submissionId (str): 超时判定对应的提交 ID。
        返回:
            None。
        '''
        with self._sessionLock:
            session = self._sessions.get(submissionId)
            if session is None and session.finished.is_set() or session.timeoutEmitted:
                pass
            None(None, None, None)
            return None
            session.timeoutEmitted = True
            timeoutSeconds = session.timeoutSeconds
            None(None, None, None)
        with None:
            if not None:
                pass
        logger.warning('[Feedback] submission timeout exceeded %s seconds', timeoutSeconds)
        self.submissionCompleted.emit()

    
    def _firmwareLogDirectoryFor(self, session, request):
        '''计算本次提交专属的固件日志目录，避免并发提交互删或互相覆盖。

        目录为 ``<logDir>/firmware/<submissionId>/``：ZIP 内仍以 ``firmware/`` 为根，
        因此打包布局与服务端路由不变，而变化点只在本地落盘位置。

        参数:
            session (LPFeedbackSession): 本次提交会话。
            request (LPFeedbackRequest): 当前反馈请求。
        返回:
            Path|None: 本次提交专属固件日志目录；无日志目录时返回 None。
        '''
        if not request.logDirectory:
            return None
        return None(request.logDirectory) / 'firmware' / session.submissionId

    
    def _collectFirmwareLogs(self, request, session):
        '''在后台线程收集音箱固件日志到本次提交专属的 firmware/<submissionId>/ 子目录。

        固件日志收集失败只记录日志，不阻断工单创建后的上传流程。

        参数:
            request (LPFeedbackRequest): 当前反馈请求。
            session (LPFeedbackSession): 本次提交会话，提供专属固件日志目录。
        返回:
            None。
        '''
        firmwareDirectory = session.firmwareDirectory
        self._clearFirmwareLogDirectory(firmwareDirectory)
        startedAt = time.time()
        deviceTotal = 0
        successCount = 0
        if bool(request.logDirectory):
            pass
        logDirOk = Path(request.logDirectory).is_dir()
    # WARNING: Decompyle incomplete

    
    def _clearFirmwareLogDirectory(self, firmwareDirectory):
        '''删除指定固件日志目录，避免旧日志进入本次 ZIP。

        对齐安卓 SendDebugLogFragment.downloadLogs：每次反馈收集前清空
        LogsFirmwareDir；提交流程结束后再清空一次，保证下次提交从空目录开始。

        参数:
            firmwareDirectory (str|Path|None): 本次提交专属固件日志目录。
        返回:
            None。
        '''
        if not firmwareDirectory:
            return None
        firmwareDir = Path(firmwareDirectory)
        if firmwareDir.exists():
            shutil.rmtree(str(firmwareDir), True, **('ignore_errors',))
    # WARNING: Decompyle incomplete

    
    def _getDevices(self):
        '''通过注入的设备列表提供者获取当前已发现音箱。

        参数:
            无。
        返回:
            list: LPDevice 列表；未注入提供者或获取失败时返回空列表。
        '''
        if self._deviceListProvider is None:
            return []
        if not self._deviceListProvider():
            pass
        :
            if self._deviceListProvider is None:
                return []
            if not self._deviceListProvider():
                pass
            
            return list([])
        return list([])
    # WARNING: Decompyle incomplete

    
    def _getApiClient(self):
        '''延迟创建 Freshdesk 客户端，避免未配置时影响弹窗加载。

        参数:
            无。
        返回:
            LPFeedbackApiClient: 可用于创建和回填工单的客户端。
        '''
        if self._apiClient is None:
            (appId, accessKey, secretKey) = requireFreshdeskCredentials()
            self._apiClient = LPFeedbackApiClient(appId, accessKey, secretKey)
        return self._apiClient

    
    def _safeCreateState(self, record):
        '''尝试创建状态文件，失败时仅记录应用日志。

        参数:
            record (dict): 状态记录。
        返回:
            None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _safeUpdateState(self, record, stage, **changes):
        '''尝试更新状态文件，失败时不阻断已经创建的工单流程。

        参数:
            record (dict): 状态记录。
            stage (str): 新阶段。
            **changes: 额外状态字段。
        返回:
            None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _safeMarkFailed(self, record, stage, message):
        '''尽力写入失败诊断 JSON。

        参数:
            record (dict): 状态记录。
            stage (str): 失败阶段。
            message (str): 错误摘要。
        返回:
            None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _safeRemoveState(self, record):
        '''删除成功任务的临时状态文件。

        参数:
            record (dict): 状态记录。
        返回:
            None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _removeCurrentThread(self):
        '''移除已结束线程引用，避免长期运行时列表增长。

        参数:
            无。
        返回:
            None。
        '''
        currentThread = threading.current_thread()
    # WARNING: Decompyle incomplete

    __classcell__ = None

