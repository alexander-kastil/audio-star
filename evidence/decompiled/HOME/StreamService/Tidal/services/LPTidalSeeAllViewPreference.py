# Source Generated with Decompyle++
# File: LPTidalSeeAllViewPreference.pyc (Python 3.9)

'''
TIDAL See All 视图模式偏好服务。
'''
from typing import Optional
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger

class LPTidalSeeAllViewPreference:
    '''负责维护 TIDAL 所有 See All 页面共享的网格/列表视图模式偏好。'''
    PREFERENCE_KEY = 'seeAllViewMode'
    DEFAULT_MODE = 'grid'
    VALID_MODES = ('grid', 'list')
    
    def _normalizeMode(cls = None, mode = None):
        '''
        校验视图模式，非法值归一为默认值。

        :param mode: 原始视图模式。
        :return: 合法的视图模式。
        '''
        if not mode:
            pass
        value = str('').strip().lower()
        if value not in cls.VALID_MODES:
            return cls.DEFAULT_MODE

    _normalizeMode = None(_normalizeMode)
    
    def readViewMode(cls = None, userId = None):
        '''
        读取 TIDAL 所有 See All 页面共享的视图模式偏好。

        :param userId: TIDAL 用户 ID。
        :return: 已保存的合法视图模式，未保存或无效返回 None。
        '''
        if not userId:
            pass
        user_id = str('').strip()
        settings = getattr(LPUtility, 'settings', None)
        if user_id or settings is None:
            return None
        group_opened = None
    # WARNING: Decompyle incomplete

    readViewMode = None(readViewMode)
    
    def saveViewMode(cls = None, userId = None, mode = classmethod):
        '''
        保存 TIDAL 所有 See All 页面共享的视图模式偏好。

        :param userId: TIDAL 用户 ID。
        :param mode: 视图模式，`grid` 或 `list`。
        :return: 保存成功返回 True。
        '''
        if not userId:
            pass
        user_id = str('').strip()
        normalized_mode = cls._normalizeMode(mode)
        settings = getattr(LPUtility, 'settings', None)
        if user_id or settings is None:
            return False
        group_opened = None
    # WARNING: Decompyle incomplete

    saveViewMode = None(saveViewMode)

