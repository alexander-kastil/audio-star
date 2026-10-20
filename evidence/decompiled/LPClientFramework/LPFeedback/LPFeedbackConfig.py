# Source Generated with Decompyle++
# File: LPFeedbackConfig.pyc (Python 3.9)

'''PC Feedback 的发布配置占位定义。

真实 Freshdesk 凭证由发布负责人替换这些占位值；真实 AES 密钥不得提交到源码。
'''
FRESHDESK_API_HOST = 'https://freshdesk.linkplay.com/apiv1/freshdesk/wiim'
FRESHDESK_WEB_HOST = 'https://wiim.freshdesk.com'
FRESHDESK_APP_ID = '<redacted>'
FRESHDESK_ACCESS_KEY = '<redacted>'
FRESHDESK_SECRET_KEY = '<redacted>'
STS_ENDPOINT = 'https://api.linkplay.com/datav3/log/feedbackUpload'
STS_ORIGIN = 'pc'
STS_PROJECT = 'WiiMHome'
FEEDBACK_AES_KEY = '<redacted>'
FEEDBACK_TYPE_DEBUG = 'FeedbackDebug'
FEEDBACK_DEFAULT_RECEIVER = 'wiimlogs@linkplay.com'

def isPlaceholder(value):
    '''判断配置值是否仍是未配置的占位符。

    参数:
        value (str): 待校验的配置值。
    返回:
        bool: True 表示配置尚未被发布值替换。
    '''
    if not value:
        pass
    normalizedValue = str('').strip()
    if not normalizedValue and normalizedValue.startswith('__'):
        pass
    return normalizedValue.endswith('__')


def requireFreshdeskCredentials():
    '''返回已配置的 Freshdesk 应用凭证。

    参数:
        无。
    返回:
        tuple[str, str, str]: appId、accessKey 与 secretKey。
    异常:
        RuntimeError: 任一凭证仍为占位符时抛出。
    '''
    values = (FRESHDESK_APP_ID, FRESHDESK_ACCESS_KEY, FRESHDESK_SECRET_KEY)
    if any((lambda .0: for value in .0:
isPlaceholder(value))(values)):
        raise RuntimeError('Feedback service is not configured.')
    return values


def requireAesKey():
    '''返回已配置的 Android 兼容 AES 密钥。

    参数:
        无。
    返回:
        str: 16 字节 AES 密钥。
    异常:
        RuntimeError: 密钥缺失或长度不符合 Android 兼容要求时抛出。
    '''
    if isPlaceholder(FEEDBACK_AES_KEY):
        raise RuntimeError('Feedback log encryption is not configured.')
    if len(FEEDBACK_AES_KEY.encode('utf-8')) != 16:
        raise RuntimeError('Feedback log encryption key must be 16 bytes.')
    return FEEDBACK_AES_KEY

