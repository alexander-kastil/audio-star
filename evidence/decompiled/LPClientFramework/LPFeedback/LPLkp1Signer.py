# Source Generated with Decompyle++
# File: LPLkp1Signer.pyc (Python 3.9)

'''Linkplay STS 接口使用的 LKP1-HMAC-SHA256 签名器。'''
import datetime
import hashlib
import hmac
from urllib.parse import quote_plus, urlparse

class LPLkp1Signer:
    '''按 Android LinkPlayInterceptor 规则构造 STS 请求头。'''
    
    def sign(method, url, body, uuid, origin, project, now = (None,)):
        '''为 STS JSON 请求生成 LKP1 鉴权头。

        参数:
            method (str): HTTP 方法。
            url (str): 完整 STS URL。
            body (bytes): 原始 JSON 请求体。
            uuid (str): PC 持久化 UUID。
            origin (str): 客户端来源标识。
            project (str): 项目名称。
            now (datetime|None): 可注入的 UTC 时间，用于测试。
        返回:
            dict: 包含 X-Linkplay-* 与 Authorization 的请求头。
        '''
        parsedUrl = urlparse(url)
        if not now:
            pass
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(datetime.timezone.utc, **('tzinfo',))
        timestamp = timestamp.astimezone(datetime.timezone.utc)
        linkplayDate = timestamp.strftime('%Y%m%dT%H%M%SZ')
        dateStamp = timestamp.strftime('%Y%m%d')
        projectHeader = quote_plus(str(project))
        host = parsedUrl.netloc
        if not parsedUrl.path:
            pass
        canonicalUri = '/'
        if not body:
            pass
        payloadHash = hashlib.sha256(b'').hexdigest()
        canonicalHeaders = 'host:%s\nx-linkplay-date:%s\nx-linkplay-origin:%s\nx-linkplay-project:%s\nx-linkplay-uuid:%s\n' % (host, linkplayDate, origin, projectHeader, uuid)
        signedHeaders = 'host;x-linkplay-date;x-linkplay-origin;x-linkplay-project;x-linkplay-uuid'
        canonicalRequest = '\n'.join([
            str(method).upper(),
            canonicalUri,
            '',
            canonicalHeaders,
            signedHeaders,
            payloadHash])
        credentialScope = '%s/%s/%s/linkplay_request' % (dateStamp, origin, projectHeader)
        stringToSign = '\n'.join([
            'LKP1-HMAC-SHA256',
            linkplayDate,
            credentialScope,
            hashlib.sha256(canonicalRequest.encode('utf-8')).hexdigest()])
        signingKey = LPLkp1Signer._signingKey(str(uuid), dateStamp, str(origin), projectHeader)
        signature = hmac.new(signingKey, stringToSign.encode('utf-8'), hashlib.sha256).hexdigest()
        authorization = 'LKP1-HMAC-SHA256 Credential=linkplay/%s, SignedHeaders=%s, Signature=%s' % (credentialScope, signedHeaders, signature)
        return {
            'X-Linkplay-Date': linkplayDate,
            'X-Linkplay-Uuid': str(uuid),
            'X-Linkplay-Project': projectHeader,
            'X-Linkplay-Origin': str(origin),
            'X-Linkplay-Content': payloadHash,
            'Authorization': authorization }

    sign = staticmethod(sign)
    
    def _signingKey(uuid, dateStamp, origin, project):
        '''派生 LKP1 四级 HMAC 签名密钥。

        参数:
            uuid (str): PC 持久化 UUID。
            dateStamp (str): yyyyMMdd 日期字符串。
            origin (str): 客户端来源标识。
            project (str): URL 编码后的项目名称。
        返回:
            bytes: 最终签名密钥。
        '''
        dateKey = LPLkp1Signer._hmac(('LKP1' + uuid).encode('utf-8'), dateStamp)
        originKey = LPLkp1Signer._hmac(dateKey, origin)
        projectKey = LPLkp1Signer._hmac(originKey, project)
        return LPLkp1Signer._hmac(projectKey, 'linkplay_request')

    _signingKey = staticmethod(_signingKey)
    
    def _hmac(key, message):
        '''计算一次 HMAC-SHA256 摘要。

        参数:
            key (bytes): HMAC 密钥。
            message (str): UTF-8 文本消息。
        返回:
            bytes: HMAC 摘要。
        '''
        return hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()

    _hmac = staticmethod(_hmac)

