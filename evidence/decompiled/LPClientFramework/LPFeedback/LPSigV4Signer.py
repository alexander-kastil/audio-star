# Source Generated with Decompyle++
# File: LPSigV4Signer.pyc (Python 3.9)

'''
AWS Signature Version 4 签名工具。

用途：feedback 日志上传到 S3 时，用 STS 下发的临时凭证
（AccessKeyId / SecretAccessKey / SessionToken）对一次 HTTP 请求做 SigV4 签名，
返回可直接附加到请求上的头集合。

设计要点：
- 仅依赖 Python 标准库（hashlib / hmac / datetime / urllib），不引入 boto3，
  避免给桌面打包增加约 60MB+ 体积。
- 纯函数式、无副作用，便于单元测试。
- 参考实现：AWS Signature Version 4 官方参考。
'''
import datetime
import hashlib
import hmac
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qsl, quote

class LPSigV4Signer:
    '''AWS SigV4 签名器，提供静态签名方法。'''
    
    def _sha256Hex(data = None):
        '''
        计算 bytes 的 SHA-256 十六进制摘要。

        参数:
            data (bytes): 原始字节，可为 None / 空。
        返回:
            str: 小写十六进制摘要。
        '''
        if not data:
            pass
        return hashlib.sha256(b'').hexdigest()

    _sha256Hex = None(_sha256Hex)
    
    def _hmacSha256(key = None, msg = None):
        '''
        HMAC-SHA256。

        参数:
            key (bytes): HMAC 密钥字节。
            msg (str): 待签名消息（UTF-8 编码）。
        返回:
            bytes: HMAC 摘要字节。
        '''
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    _hmacSha256 = None(_hmacSha256)
    
    def _canonicalUri(path = None):
        """
        规范化 URI：对路径做 URI 编码，保留 '/'。

        参数:
            path (str): URL 路径部分。
        返回:
            str: 规范化后的路径，至少为 '/'。
        """
        if not path:
            return '/'
        if not None.startswith('/'):
            path = '/' + path
        return quote(path, '/', **('safe',))

    _canonicalUri = None(_canonicalUri)
    
    def _canonicalQuery(query = None):
        """
        规范化查询串：按 key 字典序排列，key/value 均 URI 编码。

        参数:
            query (str): URL 查询串（不含 '?'）。
        返回:
            str: 规范化后的 'k=v&k=v' 串。
        """
        if not query:
            return ''
        pairs = None(parse_qsl(query, True, **('keep_blank_values',)), (lambda kv: kv[0]), **('key',))
        encoded = (lambda .0: for k, v in .0:
(quote(k, '-_.~', **('safe',)), quote(v, '-_.~', **('safe',))))(pairs)
        return '&'.join((lambda .0: for k, v in .0:
'%s=%s' % (k, v))(encoded))

    _canonicalQuery = None(_canonicalQuery)
    
    def sign(*, method, url, body, accessKey, secretKey, region, service, sessionToken, extraHeaders):
