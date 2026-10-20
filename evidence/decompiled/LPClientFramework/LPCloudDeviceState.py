# Source Generated with Decompyle++
# File: LPCloudDeviceState.pyc (Python 3.9)

'''
云端设备状态查询模块。

封装 queryDeviceStateV2 接口（对齐 iOS LPOOBECaseManager.requestCloudInfo）：
- 地址: https://cloud-api-us.linkplay.com/v1/rest/api/queryDeviceStateV2
- 鉴权: 请求需携带 accessKey/timestamp/nonce/sign/appId 签名头（与 iOS
  LPCloudRequest、PC LPAuthenticatedRequestClient 同一算法）；不带签名头的
  裸 POST 会被网关以 403（identity policy explicit deny）拒绝。
- 请求体: {"deviceUid": <24 位 hex 短 UUID>}（即 UPnP USN UUID 经
  「前四段去横线 + 末段前 4 位」变换后的结果，与 PC 端 SSDP 设备记录键同格式）
- 响应: {"result": <云端设备状态>}（顶层即 result；iOS 代码中的 status/response
  外层结构是其客户端回调时自行包装的，服务端原始响应没有该外层），
  result 含 networkInfo(wlanSsid/wlanBssid/wlanRssi/wlan0/eth0)、iotVersion、
  source、otaStatus、connectStatus 等字段。
仅用于设备发现诊断埋点，失败/超时时按降级处理返回 None，不抛异常。
'''
import hashlib
import random
import string
import time
import requests
from LPClientFramework.LPUtility import logger
QUERY_DEVICE_STATE_V2_URL = 'https://cloud-api-us.linkplay.com/v1/rest/api/queryDeviceStateV2'
_CLOUD_APP_ID = '<redacted>'
_CLOUD_ACCESS_KEY = '<redacted>'
_CLOUD_SECRET_KEY = '<redacted>'

def _signedHeaders():
    '''
    构造云端接口签名请求头（算法对齐 iOS LPCloudRequest / PC LPAuthenticatedRequestClient）。

    规则: appId = sha256(accessKey + appId) 小写；
          sign = sha256(secretKey + 按字母序拼接的参数串) 大写。

    参数:
        无。
    返回:
        dict: 含 accessKey / timestamp / nonce / sign / appId 的请求头。
    '''
    timestamp = str(int(time.time() * 1000))
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, 16, **('k',)))
    hashedAppId = hashlib.sha256((_CLOUD_ACCESS_KEY + _CLOUD_APP_ID).encode('utf-8')).hexdigest()
    plain = 'accessKey=%s&appId=%s&nonce=%s&timestamp=%s&secretKey=%s' % (_CLOUD_ACCESS_KEY, hashedAppId, nonce, timestamp, _CLOUD_SECRET_KEY)
    sign = hashlib.sha256((_CLOUD_SECRET_KEY + plain).encode('utf-8')).hexdigest().upper()
    return {
        'Content-Type': 'application/json',
        'accessKey': _CLOUD_ACCESS_KEY,
        'timestamp': timestamp,
        'nonce': nonce,
        'sign': sign,
        'appId': hashedAppId }


def queryDeviceStateV2(deviceUid, timeout = (5,)):
    '''
    查询云端设备影子状态（queryDeviceStateV2）。

    参数:
        deviceUid (str): 设备短 UUID（24 位 hex，即 PC 端 SSDP 设备记录键）。
        timeout (int): 请求超时秒数。
    返回:
        dict | None: 云端设备状态（响应顶层 result）；请求失败、超时或
        返回结构不符合预期时返回 None（调用方按降级处理，置 cloud_online=false）。
    '''
    if not deviceUid:
        return None
    response = requests.post(QUERY_DEVICE_STATE_V2_URL, {
        'deviceUid': deviceUid }, _signedHeaders(), timeout, **('json', 'headers', 'timeout'))
    if not response.ok:
        logger.warning('[cloudDeviceState] queryDeviceStateV2 http %d for %s' % (response.status_code, deviceUid[:4] + '***'))
    return None
    data = response.json()
    result = data.get('result')
    if isinstance(result, dict):
        pass
    return None
    logger.warning('[cloudDeviceState] queryDeviceStateV2 empty result for %s' % (deviceUid[:4] + '***'))
    :
        if not deviceUid:
            return None
        response = requests.post(QUERY_DEVICE_STATE_V2_URL, {
            'deviceUid': deviceUid }, _signedHeaders(), timeout, **('json', 'headers', 'timeout'))
        if not response.ok:
            logger.warning('[cloudDeviceState] queryDeviceStateV2 http %d for %s' % (response.status_code, deviceUid[:4] + '***'))
        return None
        data = response.json()
        result = data.get('result')
        if isinstance(result, dict):
            pass
        return None
        logger.warning('[cloudDeviceState] queryDeviceStateV2 empty result for %s' % (deviceUid[:4] + '***'))
        
        return None
    return None
# WARNING: Decompyle incomplete

