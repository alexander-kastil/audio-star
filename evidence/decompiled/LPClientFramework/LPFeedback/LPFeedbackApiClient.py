# Source Generated with Decompyle++
# File: LPFeedbackApiClient.pyc (Python 3.9)

'''Freshdesk 工单创建和日志地址回填客户端。'''
import json
from LPClientFramework.LPEventTrack import LPAuthenticatedRequestClient
from LPClientFramework.LPFeedback.LPFeedbackConfig import FRESHDESK_API_HOST

class LPFeedbackApiClient:
    '''封装 PC Feedback 所需的 Freshdesk POST 与 PUT 调用。'''
    
    def __init__(self, appId, accessKey, secretKey, httpClient = (None,)):
        '''初始化 Freshdesk 鉴权客户端。

        参数:
            appId (str): PC Feedback 应用 ID。
            accessKey (str): Freshdesk 应用访问密钥。
            secretKey (str): Freshdesk 应用私钥。
            httpClient (LPAuthenticatedRequestClient|None): 可注入的 HTTP 客户端。
        返回:
            无。
        '''
        if not httpClient:
            pass
        self._httpClient = LPAuthenticatedRequestClient(FRESHDESK_API_HOST, appId, accessKey, secretKey, 15, **('api_host', 'app_id', 'access_key', 'secret_key', 'timeout'))

    
    def createTicket(self, request, subtype = ('Other',)):
        '''创建 Freshdesk 工单并返回工单 ID。

        参数:
            request (LPFeedbackRequest): 用户反馈请求。
            subtype (str): 固定的反馈子类型。
        返回:
            str: Freshdesk 工单 ID。
        异常:
            RuntimeError: 响应未包含工单 ID 时抛出。
        '''
        payload = {
            'email': request.email,
            'subject': request.subject,
            'description': request.description,
            'priority': 1,
            'status': 2,
            'name': '',
            'type': 'Problem',
            'custom_fields': {
                'cf_useremail': request.email,
                'cf_appid': request.appUuid,
                'cf_subtype': subtype } }
        (responseData, _) = self._httpClient.post('/tickets', payload)
        if not responseData:
            pass
        ticketData = { }
    # WARNING: Decompyle incomplete

    
    def updateTicket(self, request, ticketId, confirmationId, downloadUrl, subtype = ('Other',)):
        '''向已有工单回填日志下载地址与确认 ID。

        参数:
            request (LPFeedbackRequest): 原始反馈请求。
            ticketId (str): Freshdesk 工单 ID。
            confirmationId (str): 上传确认 ID。
            downloadUrl (str): S3 日志 ZIP 下载地址。
            subtype (str): 固定的反馈子类型。
        返回:
            None。
        '''
        payload = {
            'priority': 1,
            'status': 2,
            'type': 'Problem',
            'custom_fields': {
                'cf_useremail': request.email,
                'cf_log': downloadUrl,
                'cf_confirmationid': confirmationId,
                'cf_appid': request.appUuid,
                'cf_subtype': subtype } }
        self._httpClient.put('/tickets/%s' % ticketId, payload)


