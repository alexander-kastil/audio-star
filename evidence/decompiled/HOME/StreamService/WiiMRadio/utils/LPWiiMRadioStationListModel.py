# Source Generated with Decompyle++
# File: LPWiiMRadioStationListModel.pyc (Python 3.9)

'''
WiiMRadio station 增量列表模型。
'''
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt, pyqtSlot
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioRequestScheduler import LPWiiMRadioRequestScheduler
from HOME.StreamService.WiiMRadio.utils.LPWiiMRadioThumbnailService import LPWiiMRadioThumbnailService
from LPClientFramework.LPUtility import logger

class LPWiiMRadioStationListModel(QAbstractListModel):
    MAX_ITEMS = 500
    PRELOAD_BEFORE = 4
    PRELOAD_AFTER = 8
    STATION_ID_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    NAME_ROLE = STATION_ID_ROLE + 1
    FAVICON_ROLE = STATION_ID_ROLE + 2
    STREAM_URL_ROLE = STATION_ID_ROLE + 3
    FAVICON_THUMB_PATH_ROLE = STATION_ID_ROLE + 4
    CITY_ROLE = STATION_ID_ROLE + 5
    REGION_ROLE = STATION_ID_ROLE + 6
    COUNTRY_ROLE = STATION_ID_ROLE + 7
    COUNTRY_CODE_ROLE = STATION_ID_ROLE + 8
    GENRES_ROLE = STATION_ID_ROLE + 9
    
    def __init__(self = None, parent = None):
        '''
        初始化 station 列表模型。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._items = []
        logger.debug(f'''LPWiiMRadioStationListModel _items {len(self._items)}''')
        self._station_ids = set()
        self._thumbnail_service = LPWiiMRadioThumbnailService.instance()
        self._thumbnail_service.thumbnailReady.connect(self._onThumbnailReady)
        self._visible_first_index = -1
        self._visible_last_index = -1

    
    def __del__(self):
        logger.debug('LPWiiMRadioStationListModel enter __del__')

    
    def rowCount(self = None, parent = None):
        '''
        返回模型当前行数。

        :param parent: 父级索引。
        :return: 当前条目数量。
        '''
        if parent.isValid():
            return 0
        return None(self._items)

    
    def data(self = None, index = None, role = None):
        '''
        根据索引与 role 返回模型数据。

        :param index: 目标索引。
        :param role: Qt role 值。
        :return: role 对应的数据值。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._items):
            return None
        item = None._items[row]
        if role == self.STATION_ID_ROLE:
            return item.get('stationId', '')
        if None == self.NAME_ROLE:
            return item.get('name', '')
        if None == self.FAVICON_ROLE:
            return item.get('favicon', '')
        if None == self.STREAM_URL_ROLE:
            return item.get('streamUrl', '')
        if None == self.FAVICON_THUMB_PATH_ROLE:
            return item.get('faviconThumbPath', '')
        if None == self.CITY_ROLE:
            return item.get('city', '')
        if None == self.REGION_ROLE:
            return item.get('region', '')
        if None == self.COUNTRY_ROLE:
            return item.get('country', '')
        if None == self.COUNTRY_CODE_ROLE:
            return item.get('countryCode', '')
        if None == self.GENRES_ROLE:
            return item.get('genres', '')

    
    def roleNames(self = None):
        '''
        返回模型 role 与名称映射。

        :param: 无。
        :return: role 名称字典。
        '''
        return {
            self.GENRES_ROLE: b'genres',
            self.COUNTRY_CODE_ROLE: b'countryCode',
            self.COUNTRY_ROLE: b'country',
            self.REGION_ROLE: b'region',
            self.CITY_ROLE: b'city',
            self.FAVICON_THUMB_PATH_ROLE: b'faviconThumbPath',
            self.STREAM_URL_ROLE: b'streamUrl',
            self.FAVICON_ROLE: b'favicon',
            self.NAME_ROLE: b'name',
            self.STATION_ID_ROLE: b'stationId' }

    
    def cleanup(self = None):
        '''
        页面不可见时断开 thumbnailReady 信号，并清除可见区范围，避免继续调度图片任务。

        :param: 无。
        :return: None。
        '''
        self.clearVisibleRange()
    # WARNING: Decompyle incomplete

    
    def reconnect(self = None):
        '''
        重新连接 thumbnailReady 信号，供页面重新可见时调用。
        先断后连防止重复注册。

        :param: 无。
        :return: None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def updateVisibleRange(self = None, firstIndex = None, lastIndex = pyqtSlot(int, int)):
        '''
        更新当前可见区索引范围，并按“可见区 + 预取窗口”调度缩略图。

        :param firstIndex: 当前首个可见索引。
        :param lastIndex: 当前最后一个可见索引。
        :return: None。
        '''
        count = len(self._items)
        if count <= 0:
            self._visible_first_index = -1
            self._visible_last_index = -1
            return None
        first = None(0, int(firstIndex))
        last = min(count - 1, int(lastIndex))
        if last < first:
            self._visible_first_index = -1
            self._visible_last_index = -1
            return None
        if None == self._visible_first_index and last == self._visible_last_index:
            return None
        self._visible_first_index = None
        self._visible_last_index = last
        self._schedule_visible_range_thumbnails()

    updateVisibleRange = None(updateVisibleRange)
    
    def clearVisibleRange(self = None):
        '''
        清空当前可见区范围，停止后续基于 viewport 的预取调度。

        :param: 无。
        :return: None。
        '''
        self._visible_first_index = -1
        self._visible_last_index = -1

    clearVisibleRange = None(clearVisibleRange)
    
    def clear(self = None):
        '''
        清空模型数据。

        :param: 无。
        :return: None。
        '''
        if not self._items:
            return None
        None.beginResetModel()
        self._items = []
        self._station_ids.clear()
        self._visible_first_index = -1
        self._visible_last_index = -1
        self.endResetModel()

    
    def resetItems(self = None, items = None, maxItems = None):
        '''
        重置模型数据，并按 stationId 去重。

        :param items: 输入条目列表。
        :param maxItems: 最大条目上限，<=0 表示不限制。
        :return: 重置后条目数。
        '''
        effective_max = self.MAX_ITEMS if maxItems <= 0 else min(maxItems, self.MAX_ITEMS)
        normalized = self._normalize_items(items, effective_max, **('maxItems',))
        self.beginResetModel()
        self._items = normalized
        self._station_ids = (lambda .0: pass# WARNING: Decompyle incomplete
)(self._items)
        self.endResetModel()
        self._schedule_visible_range_thumbnails()
        return len(self._items)

    
    def isFull(self = None):
        '''
        返回当前模型是否已达到最大条目上限。

        :param: 无。
        :return: 达到 MAX_ITEMS 时返回 True，否则返回 False。
        '''
        return len(self._items) >= self.MAX_ITEMS

    
    def appendItems(self = None, items = None, maxItems = None):
