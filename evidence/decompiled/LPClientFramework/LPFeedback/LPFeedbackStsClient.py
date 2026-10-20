# Source Generated with Decompyle++
# File: LPFeedbackStsClient.pyc (Python 3.9)

'''Feedback 日志上传所需 STS 临时凭证客户端。'''
import base64
import datetime
import json
import requests
from LPClientFramework.LPFeedback.LPFeedbackConfig import FEEDBACK_DEFAULT_RECEIVER, FEEDBACK_TYPE_DEBUG, FRESHDESK_WEB_HOST, STS_ENDPOINT, STS_ORIGIN, STS_PROJECT
from LPClientFramework.LPFeedback.LPFeedbackModels import LPFeedbackStsCredential
from LPClientFramework.LPFeedback.LPLkp1Signer import LPLkp1Signer

def _toBase64(text):
    '''按安卓 Base64.NO_WRAP 约定对 UTF-8 文本做标准 Base64 编码。

    参数:
        text (str): 待编码的明文。
    返回:
        str: 不含换行的 Base64 字符串。
    '''
    if not text:
        pass
    return base64.b64encode(''.encode('utf-8')).decode('ascii')


def _buildMessage(request, submission):
    '''构造 emailMetadata.message 解码前的 JSON 字符串，字段与安卓 NormalBuilder 对齐。

    参数:
        request (LPFeedbackRequest): 原始反馈请求。
        submission (LPFeedbackSubmission): 已创建工单的任务信息。
    返回:
        str: message JSON 字符串（编码前）。
    '''
    if not request.currentDeviceName:
        pass
    message = {
        'DeviceName': request.deviceName,
        'Type': request.feedbackType,
        'OSVersion': request.osVersion,
        'AppVersion': request.appVersion,
        'ConfirmationID': submission.confirmationId,
        'DownloadUri': '|downloadUrl|',
        'Current device is': '(null)' }
    if request.subject and request.email or request.description:
        message['Subject'] = request.subject
        message['Email'] = request.email
        message['Comment'] = request.description
    message['TicketLink'] = _buildTicketLink(submission.ticketId)
    message['DeviceList'] = _buildDeviceList(request.deviceList)
    return json.dumps(message, False, (',', ':'), **('ensure_ascii', 'separators'))


def _buildTicketLink(ticketId):
    '''构造 TicketLink，工单 ID 为空或 -1 时返回空字符串，与安卓 getTickLink() 一致。

    参数:
        ticketId (str): Freshdesk 工单 ID。
    返回:
        str: 工单链接或空字符串。
    '''
    if ticketId or str(ticketId) == '-1':
        return ''
    return None % (FRESHDESK_WEB_HOST, ticketId)


def _shortenUuid(rawUuid):
    '''按安卓 LPDeviceManagerUtil.UpnpUUID2UUID() 规则截取设备短 UUID。

    规则: 空返回空串；长度<=24 原样返回；以 "UUID:" 开头则去前缀与连字符取前 24 位；
    否则取前 24 位。

    参数:
        rawUuid (str): 设备原始 UUID（可能含 "uuid:"/"UUID:" 前缀）。
    返回:
        str: 短 UUID。
    '''
    if not rawUuid:
        return ''
    value = None(rawUuid)
    if len(value) <= 24:
        return value
    upper = None.upper()
    if upper.startswith('UUID:'):
        stripped = upper.replace('UUID:', '').replace('-', '')
        return stripped[:24]
    return None[:24]


def _buildDeviceList(deviceList):
    '''构造 DeviceList（Freshdesk 格式），与安卓 getDeviceListOfFreshdesk() 一致。

    格式: "[N]<name> [U]<shortUuid>,[N]<name> [U]<shortUuid>"
    安卓 [N] 取 DeviceItemUtils.getName，[U] 取 UpnpUUID2UUID 短 UUID。

    参数:
        deviceList (list[tuple]): 元素为 (设备名, 设备UUID) 的列表。
    返回:
        str: 逗号分隔的设备列表字符串。
    '''
    items = []
    for entry in deviceList:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            name = entry[0]
            rawUuid = entry[1]
        else:
            name = entry
            rawUuid = ''
        if not name:
            continue
        items.append('[N]%s [U]%s' % (name, _shortenUuid(rawUuid)))
    return ','.join(items)


def _buildEmailSubject(request):
    '''构造邮件主题（编码前），与安卓 NormalBuilder.buildSubject() 对齐。

    安卓格式（bFreshdesk=true 且非崩溃）: "Ticket # Debug log - <appName> Android <yyyy.MM.dd HH:mm> <sdkVersion>"
    PC 端走 Freshdesk 工单流程（bFreshdesk 等价为 true），平台名替换为 "PC"。

    参数:
        request (LPFeedbackRequest): 原始反馈请求。
    返回:
        str: 主题字符串（编码前）。
    '''
    timestamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
    if not STS_PROJECT:
        pass
    appName = ''.replace(' ', '')
    return 'Ticket # Debug log - %s PC %s %s' % (appName, timestamp, request.appVersion)


def _buildReceivers(feedbackType):
    '''根据反馈类型选择收件人，与安卓 LogContextUtil.getEmailAddress() 对齐。

    参数:
        feedbackType (str): 反馈类型常量。
    返回:
        str: 收件人邮箱。
    '''
    return FEEDBACK_DEFAULT_RECEIVER


def _buildEmailMetadata(request, submission):
    '''构造与安卓 EmailMetadata 对齐的 JSON 字符串。

    结构: {"message": "<base64>", "subject": "<base64>", "receivers": "<base64>"}

    参数:
        request (LPFeedbackRequest): 原始反馈请求。
        submission (LPFeedbackSubmission): 已创建工单的任务信息。
    返回:
        str: emailMetadata JSON 字符串。
    '''
    metadata = {
        'message': _toBase64(_buildMessage(request, submission)),
        'subject': _toBase64(_buildEmailSubject(request)),
        'receivers': _toBase64(_buildReceivers(request.feedbackType)) }
    return json.dumps(metadata, False, (',', ':'), **('ensure_ascii', 'separators'))


def _buildLogItem(request, submission):
    '''构造顶层 logItem（LogInfoItem 的 JSON 字符串），与安卓 GsonUtils.toJson(logInfoItem) 对齐。

    覆盖安卓 LogInfoItem 的全部序列化字段，PC 不适用的取默认值（与安卓默认值一致）。

    参数:
        request (LPFeedbackRequest): 原始反馈请求。
        submission (LPFeedbackSubmission): 已创建工单的任务信息。
    返回:
        str: logItem JSON 字符串。
    '''
    if not STS_PROJECT:
        pass
    appName = ''.replace(' ', '')
    if not request.logDirectory:
        pass
    if not submission.ticketId:
        pass
    logItem = {
        'appName': appName,
        'appNameES': '',
        'subject': request.subject,
        'email': request.email,
        'desc': request.description,
        'name': '',
        'feedback_type': request.feedbackType,
        'issueType': 'custom_feedback',
        'musicService': '',
        'comment': '',
        'project': appName,
        'zipFileName': '',
        'bOnlyCrash': False,
        'filePath': str(''),
        'custom': False,
        'ticketid': str('-1'),
        'isUserSend': True,
        'hasEmailReceivers': True,
        'deleteAfterUploaded': True,
        'actionType': 'feedback' }
    return json.dumps(logItem, False, (',', ':'), **('ensure_ascii', 'separators'))


class LPFeedbackStsClient:
    '''调用 datav3/log/feedbackUpload 并解析 S3 临时凭证。'''
    
    def __init__(self, endpoint, origin, project, session = (STS_ENDPOINT, STS_ORIGIN, STS_PROJECT, None)):
        '''初始化 STS 客户端。

        参数:
            endpoint (str): STS 接口地址。
            origin (str): 客户端来源标识。
            project (str): 项目名称。
            session (requests.Session|None): 可注入的 requests 会话。
        返回:
            无。
        '''
        self._endpoint = endpoint
        self._origin = origin
        self._project = project
        if not session:
            pass
        self._session = requests.Session()

    
    def requestCredential(self, request, submission, archivePath):
        '''请求一次 S3 上传所需的临时凭证。

        参数:
            request (LPFeedbackRequest): 原始反馈请求。
            submission (LPFeedbackSubmission): 已创建工单的任务信息。
            archivePath (str): 本地 ZIP 包路径。
        返回:
            LPFeedbackStsCredential: S3 临时凭证。
        '''
        if not request.deviceUuid:
            pass
        if not submission.ticketId:
            pass
        payload = {
            'osType': 'pc',
            'logType': 'custom_feedback',
            'uuid': 'unknow',
            'project': self._project,
            'formatVersion': '3',
            'confirmationID': submission.confirmationId,
            'ticketId': str('-1'),
            'logItem': _buildLogItem(request, submission),
            'actionType': 'feedback',
            'emailMetadata': _buildEmailMetadata(request, submission),
            'FILE_PATH': str(archivePath),
            'sdkVersion': request.appVersion }
        body = json.dumps(payload, False, (',', ':'), **('ensure_ascii', 'separators')).encode('utf-8')
        headers = LPLkp1Signer.sign('POST', self._endpoint, body, request.appUuid, self._origin, self._project, **('method', 'url', 'body', 'uuid', 'origin', 'project'))
        headers['Content-Type'] = 'application/json'
        response = self._session.post(self._endpoint, body, headers, 20, **('data', 'headers', 'timeout'))
        response.raise_for_status()
        return LPFeedbackStsCredential.fromResponse(response.json())


