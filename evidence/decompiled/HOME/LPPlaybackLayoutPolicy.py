# Source Generated with Decompyle++
# File: LPPlaybackLayoutPolicy.pyc (Python 3.9)

'''
播放相关界面布局策略。
'''
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPQueueManager import isQueueSupportedMediaType
COMPACT_PLAYVIEW_SOURCES = {
    LPPlayListSource.WiiMRadio.value}
COMPACT_PLAYVIEW_EXCLUDED_SOURCES = {
    LPPlayListSource.Soundtrack.value}

def useCompactPlayViewLayout(device = None):
    '''
    判断当前播放信息是否使用居中封面播放页布局。

    :param device: 当前播放设备对象，需包含 mediaInfo 播放信息。
    :return: 需要进入 compact 播放页/minibar 布局时返回 True，否则返回 False。
    '''
    if device is None or device.mediaInfo is None:
        return False
    mediaInfo = None.mediaInfo
    trackSource = getattr(mediaInfo, 'trackSource', None)
    if trackSource in COMPACT_PLAYVIEW_EXCLUDED_SOURCES:
        return False
    if not None(mediaInfo.mediaType):
        return True
    if None in COMPACT_PLAYVIEW_SOURCES:
        return True

