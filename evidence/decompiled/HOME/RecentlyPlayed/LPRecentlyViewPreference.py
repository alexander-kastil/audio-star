# Source Generated with Decompyle++
# File: LPRecentlyViewPreference.pyc (Python 3.9)

'''
Recently Played 视图模式偏好服务。
'''
from typing import Optional
from LPClientFramework import LPUtility
from LPClientFramework.LPUtility import logger

class LPRecentlyViewPreference:
    '''负责维护 Recently Played 页面共享的卡片/列表视图模式偏好。'''
    PREFERENCE_GROUP = 'RecentlyPlayed'
    PREFERENCE_KEY = 'recentlyViewMode'
    DEFAULT_MODE = 'card'
    VALID_MODES = ('card', 'list')
    
    def _normalizeMode(cls = None, mode = None):
        '''
        校验视图模式，非法值归一为默认卡片模式。

        :param mode: 原始视图模式。
        :return: 合法的视图模式。
        '''
        if not mode:
            pass
        value = str('').strip().lower()
        if value not in cls.VALID_MODES:
            return cls.DEFAULT_MODE

    _normalizeMode = None(_normalizeMode)
    
    def readViewMode(cls = None):
        '''
        读取 Recently Played 页面共享的视图模式偏好。

        :return: 已保存的合法视图模式，未保存或无效返回 None。
        '''
        settings = getattr(LPUtility, 'settings', None)
        if settings is None:
            return None
        group_opened = None
    # WARNING: Decompyle incomplete

    readViewMode = None(readViewMode)
    
    def saveViewMode(cls = None, mode = None):
        '''
        保存 Recently Played 页面共享的视图模式偏好。

        :param mode: 视图模式，`card` 或 `list`。
        :return: 保存成功返回 True。
        '''
        normalized_mode = cls._normalizeMode(mode)
        settings = getattr(LPUtility, 'settings', None)
        if settings is None:
            return False
        group_opened = None
    # WARNING: Decompyle incomplete

    saveViewMode = None(saveViewMode)

