# Source Generated with Decompyle++
# File: LPTidalCollectionSortPreference.pyc (Python 3.9)

'''
TIDAL Collection 排序偏好服务。
'''
from typing import Dict, List, Optional
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger

class LPTidalCollectionSortPreference:
    '''负责维护 TIDAL Collection 各分区排序选项和本地偏好。'''
    PREFERENCE_PREFIX = 'collectionSeeAllSort'
    DEFAULT_ORDER = 'DATE'
    DEFAULT_DIRECTION = 'DESC'
    SORT_OPTIONS_BY_SECTION: Dict[(str, List[Dict[(str, str)]])] = {
        'userPlaylists': [
            {
                'order': 'DATE',
                'direction': 'DESC',
                'label': 'Date Added' },
            {
                'order': 'NAME',
                'direction': 'ASC',
                'label': 'Name A-Z' },
            {
                'order': 'NAME',
                'direction': 'DESC',
                'label': 'Name Z-A' }],
        'favoriteArtists': [
            {
                'order': 'NAME',
                'direction': 'ASC',
                'label': 'Name A-Z' },
            {
                'order': 'NAME',
                'direction': 'DESC',
                'label': 'Name Z-A' },
            {
                'order': 'DATE',
                'direction': 'DESC',
                'label': 'Date Added' }],
        'favoriteAlbums': [
            {
                'order': 'NAME',
                'direction': 'ASC',
                'label': 'Name A-Z' },
            {
                'order': 'NAME',
                'direction': 'DESC',
                'label': 'Name Z-A' },
            {
                'order': 'DATE',
                'direction': 'DESC',
                'label': 'Date Added' },
            {
                'order': 'ARTIST',
                'direction': 'ASC',
                'label': 'Artist A-Z' },
            {
                'order': 'ARTIST',
                'direction': 'DESC',
                'label': 'Artist Z-A' },
            {
                'order': 'RELEASE_DATE',
                'direction': 'DESC',
                'label': 'Release Date' }],
        'favoriteTracks': [
            {
                'order': 'NAME',
                'direction': 'ASC',
                'label': 'Name A-Z' },
            {
                'order': 'NAME',
                'direction': 'DESC',
                'label': 'Name Z-A' },
            {
                'order': 'ARTIST',
                'direction': 'ASC',
                'label': 'Artist A-Z' },
            {
                'order': 'ARTIST',
                'direction': 'DESC',
                'label': 'Artist Z-A' },
            {
                'order': 'DATE',
                'direction': 'DESC',
                'label': 'Date Added' },
            {
                'order': 'ALBUM',
                'direction': 'ASC',
                'label': 'Album A-Z' },
            {
                'order': 'ALBUM',
                'direction': 'DESC',
                'label': 'Album Z-A' }],
        'favoriteVideos': [
            {
                'order': 'NAME',
                'direction': 'ASC',
                'label': 'Name A-Z' },
            {
                'order': 'NAME',
                'direction': 'DESC',
                'label': 'Name Z-A' },
            {
                'order': 'DATE',
                'direction': 'DESC',
                'label': 'Date Added' }] }
    
    def preferenceKey(cls = None, sectionKey = None):
        '''
        返回收藏排序偏好键。

        :param sectionKey: 收藏 section 标识。
        :return: QSettings 键名。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        return f'''{cls.PREFERENCE_PREFIX}:{section_key}'''

    preferenceKey = None(preferenceKey)
    
    def sortOptions(cls = None, sectionKey = None):
        '''
        返回指定收藏 section 支持的排序选项。

        :param sectionKey: 收藏 section 标识。
        :return: 排序选项列表。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        return (lambda .0: [ dict(option) for option in .0 ])(cls.SORT_OPTIONS_BY_SECTION.get(section_key, []))

    sortOptions = None(sortOptions)
    
    def matchedSortOption(cls = None, sectionKey = None, order = classmethod, direction = {
        'sectionKey': str,
        'order': str,
        'direction': str,
        'return': Optional[Dict[(str, str)]] }):
        '''
        校验并返回收藏 section 支持的排序选项。

        :param sectionKey: 收藏 section 标识。
        :param order: 排序字段。
        :param direction: 排序方向。
        :return: 匹配的排序选项，未匹配返回 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not order:
            pass
        normalized_order = str('').strip().upper()
        if not direction:
            pass
        normalized_direction = str('').strip().upper()
        if normalized_direction not in ('ASC', 'DESC'):
            return None
        for option in None.SORT_OPTIONS_BY_SECTION.get(section_key, []):
            if not option.get('order', ''):
                pass
            option_order = str('').strip().upper()
            if not option.get('direction', ''):
                pass
            option_direction = str('').strip().upper()
            if option_order == normalized_order and option_direction == normalized_direction:
                return {
                    'order': option_order,
                    'direction': option_direction }
            return None

    matchedSortOption = None(matchedSortOption)
    
    def defaultSort(cls = None, sectionKey = None):
        '''
        返回指定收藏 section 的默认排序。

        :param sectionKey: 收藏 section 标识。
        :return: 包含 order 和 direction 的排序字典。
        '''
        matched_default = cls.matchedSortOption(sectionKey, cls.DEFAULT_ORDER, cls.DEFAULT_DIRECTION)
        if matched_default is not None:
            return matched_default
        return {
            'order': None.DEFAULT_ORDER,
            'direction': cls.DEFAULT_DIRECTION }

    defaultSort = None(defaultSort)
    
    def readSort(cls = None, sectionKey = None, userId = classmethod):
        '''
        读取收藏 section 排序偏好。

        :param sectionKey: 收藏 section 标识。
        :param userId: TIDAL 用户 ID。
        :return: 有效排序配置，未保存或无效返回 None。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not userId:
            pass
        user_id = str('').strip()
        settings = getattr(LPUtility, 'settings', None)
        if section_key and user_id or settings is None:
            return None
        group_opened = None
    # WARNING: Decompyle incomplete

    readSort = None(readSort)
    
    def sortForSection(cls = None, sectionKey = None, userId = classmethod):
        '''
        返回指定收藏 section 应用的排序。

        :param sectionKey: 收藏 section 标识。
        :param userId: TIDAL 用户 ID。
        :return: 保存排序或默认排序。
        '''
        if not cls.readSort(sectionKey, userId):
            pass
        return cls.defaultSort(sectionKey)

    sortForSection = None(sortForSection)
    
    def sortPreferencesForUser(cls = None, userId = None):
        '''
        返回当前用户所有收藏 section 的有效排序。

        :param userId: TIDAL 用户 ID。
        :return: 以 sectionKey 为键的排序字典。
        '''
        if not userId:
            pass
        user_id = str('').strip()
        return (lambda .0 = None: pass# WARNING: Decompyle incomplete
)(cls.SORT_OPTIONS_BY_SECTION.keys())

    sortPreferencesForUser = None(sortPreferencesForUser)
    
    def saveSort(cls, sectionKey = None, userId = None, order = classmethod, direction = {
        'sectionKey': str,
        'userId': str,
        'order': str,
        'direction': str,
        'return': bool }):
        '''
        保存收藏 section 排序偏好。

        :param sectionKey: 收藏 section 标识。
        :param userId: TIDAL 用户 ID。
        :param order: 排序字段。
        :param direction: 排序方向。
        :return: 保存成功返回 True。
        '''
        if not sectionKey:
            pass
        section_key = str('').strip()
        if not userId:
            pass
        user_id = str('').strip()
        matched_sort = cls.matchedSortOption(section_key, order, direction)
        settings = getattr(LPUtility, 'settings', None)
        if section_key and user_id and matched_sort is None or settings is None:
            return False
        group_opened = None
    # WARNING: Decompyle incomplete

    saveSort = None(saveSort)

