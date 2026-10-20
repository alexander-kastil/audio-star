# Source Generated with Decompyle++
# File: LPTidalStore.pyc (Python 3.9)

'''
TIDAL 统一状态管理。
'''
import json
import time
import weakref
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from PyQt6.QtCore import QAbstractListModel, QModelIndex, QObject, QSortFilterProxyModel, Qt, pyqtProperty, pyqtSignal, pyqtSlot
from HOME.StreamService.Tidal.services.LPTidalImageService import LPTidalImageService
from HOME.StreamService.Tidal.models.LPTidalListModel import LPTidalListModel
logger = logging.getLogger('linkplay')

class LPTidalSectionListModel(QAbstractListModel):
    '''首页区块列表模型，承载 section 元数据与其对应内容模型。'''
    SECTION_KEY_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    TITLE_ROLE = SECTION_KEY_ROLE + 1
    ITEMS_ROLE = SECTION_KEY_ROLE + 2
    IS_LOADING_ROLE = SECTION_KEY_ROLE + 3
    IS_CATEGORY_ROLE = SECTION_KEY_ROLE + 4
    SEE_ALL_ENABLED_ROLE = SECTION_KEY_ROLE + 5
    ITEM_MODE_ROLE = SECTION_KEY_ROLE + 6
    
    def __init__(self = None, parent = None):
        '''
        初始化首页区块模型。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._sections = []

    
    def rowCount(self = None, parent = None):
        '''
        返回区块数量。

        :param parent: 父级索引。
        :return: 区块数量。
        '''
        if parent.isValid():
            return 0
        return None(self._sections)

    
    def data(self = None, index = None, role = None):
        '''
        返回指定区块字段。

        :param index: 模型索引。
        :param role: Qt 角色值。
        :return: 字段值。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._sections):
            return None
        section = None._sections[row]
        if role == self.SECTION_KEY_ROLE:
            return section.get('sectionKey', '')
        if None == self.TITLE_ROLE:
            return section.get('title', '')
        if None == self.ITEMS_ROLE:
            return section.get('items', None)
        if None == self.IS_LOADING_ROLE:
            return bool(section.get('isLoading', False))
        if None == self.IS_CATEGORY_ROLE:
            return bool(section.get('isCategory', False))
        if None == self.SEE_ALL_ENABLED_ROLE:
            return bool(section.get('seeAllEnabled', True))
        if None == self.ITEM_MODE_ROLE:
            return section.get('itemMode', '')

    
    def roleNames(self = None):
        '''
        返回 QML 角色映射。

        :return: 角色名称字典。
        '''
        return {
            self.ITEM_MODE_ROLE: b'itemMode',
            self.SEE_ALL_ENABLED_ROLE: b'seeAllEnabled',
            self.IS_CATEGORY_ROLE: b'isCategory',
            self.IS_LOADING_ROLE: b'isLoading',
            self.ITEMS_ROLE: b'items',
            self.TITLE_ROLE: b'title',
            self.SECTION_KEY_ROLE: b'sectionKey' }

    
    def clear(self = None):
        '''
        清空所有区块。

        :return: None。
        '''
        if not self._sections:
            return None
        None.beginResetModel()
        self._sections = []
        self.endResetModel()

    
    def setSections(self = None, sections = None):
        '''
        用新的区块列表替换当前内容。

        :param sections: 区块字典序列。
        :return: None。
        '''
        new_sections = (lambda .0: [ dict(section) for section in .0 if isinstance(section, dict) ])(sections)
        self.beginResetModel()
        self._sections = new_sections
        self.endResetModel()

    
    def upsertSection(self = None, section = None):
        '''
        按 sectionKey 插入或更新区块。

        :param section: 区块字典。
        :return: None。
        '''
        if not isinstance(section, dict):
            return None
        if not section.get('sectionKey', ''):
            pass
        section_key = None('').strip()
        if not section_key:
            return None
        for row, current in None(self._sections):
            if not current.get('sectionKey', ''):
                pass
            if str('').strip() == section_key:
                current.update(section)
                model_index = self.index(row, 0)
                self.dataChanged.emit(model_index, model_index, list(self.roleNames().keys()))
                return None
            start_row = len(self._sections)
            self.beginInsertRows(QModelIndex(), start_row, start_row)
            self._sections.append(dict(section))
            self.endInsertRows()
            return None

    
    def sectionForKey(self = None, sectionKey = None):
        '''
        按 sectionKey 返回区块副本。

        :param sectionKey: 区块标识。
        :return: 区块字典或 None。
        '''
        if not sectionKey:
            pass
        needle = str('').strip()
        if not needle:
            return None
        for section in None._sections:
            if not section.get('sectionKey', ''):
                pass
            if str('').strip() == needle:
                return dict(section)
            return None

    
    def sectionKeys(self = None):
        '''
        返回当前所有区块标识。

        :return: 区块标识列表。
        '''
        return (lambda .0: [ str('').strip() for section in .0 if section.get('sectionKey', '') ])(self._sections)

    
    def itemsModelForSection(self = None, sectionKey = None):
        '''
        返回指定区块的条目模型。

        :param sectionKey: 区块标识。
        :return: 条目模型或 None。
        '''
        if not sectionKey:
            pass
        needle = str('').strip()
        if not needle:
            return None
        for section in None._sections:
            if not section.get('sectionKey', ''):
                pass
            if str('').strip() != needle:
                continue
            items = section.get('items')
            return items if isinstance(items, LPTidalListModel) else None
            return None

    
    def itemForSection(self = None, sectionKey = None, itemId = None):
        '''
        按区块和条目 ID 返回条目副本。

        :param sectionKey: 区块标识。
        :param itemId: 条目 ID。
        :return: 条目字典或 None。
        '''
        section = self.sectionForKey(sectionKey)
        if not section:
            return None
        items = None.get('items')
        if not isinstance(items, LPTidalListModel):
            return None
        return None.itemAt(items.findIndexById(itemId))

    __classcell__ = None


class _TidalBaseState(QObject):
    '''页面状态基类，提供生命周期和回收控制。'''
    VISIBLE_THUMBNAIL_WINDOW_LIMIT = 40
    VISIBLE_THUMBNAIL_PRELOAD_BEFORE = 2
    VISIBLE_THUMBNAIL_PRELOAD_AFTER = 4
    
    def __init__(self = None, cacheKey = None, parent = None):
        '''
        初始化状态基类。

        :param cacheKey: 状态缓存键。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        if not cacheKey:
            pass
        self.cacheKey = str('').strip()
        self._created_ms = self._now_ms()
        self._last_access_ms = self._created_ms
        self._active_count = 0
        self._disposed = False
        self._parent_ref = weakref.ref(parent) if parent is not None else None
        self._image_service = LPTidalImageService.instance()
    # WARNING: Decompyle incomplete

    
    def lastAccessMs(self = None):
        '''
        返回最近访问时间戳。

        :return: 毫秒时间戳。
        '''
        return self._last_access_ms

    lastAccessMs = None(lastAccessMs)
    
    def activeRefCount(self = None):
        '''
        返回当前活跃引用数。

        :return: 活跃引用数。
        '''
        return self._active_count

    activeRefCount = None(activeRefCount)
    
    def touch(self = None):
        '''
   