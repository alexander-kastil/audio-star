# Source Generated with Decompyle++
# File: LPTidalListModel.pyc (Python 3.9)

'''
TIDAL 通用列表模型。
'''
from typing import Any, Dict, Iterable, List, Optional
from PyQt6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt, pyqtSlot

class LPTidalListModel(QAbstractListModel):
    '''TIDAL 通用列表模型，承载卡片、曲目、歌单等结构化条目。'''
    ITEM_ID_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    ITEM_TYPE_ROLE = ITEM_ID_ROLE + 1
    TITLE_ROLE = ITEM_ID_ROLE + 2
    SUBTITLE_ROLE = ITEM_ID_ROLE + 3
    IMAGE_URL_ROLE = ITEM_ID_ROLE + 4
    IMAGE_PATH_ROLE = ITEM_ID_ROLE + 5
    TRACK_COUNT_ROLE = ITEM_ID_ROLE + 6
    DURATION_ROLE = ITEM_ID_ROLE + 7
    IS_FAVORITE_ROLE = ITEM_ID_ROLE + 8
    ARTIST_NAME_ROLE = ITEM_ID_ROLE + 9
    ALBUM_NAME_ROLE = ITEM_ID_ROLE + 10
    YEAR_ROLE = ITEM_ID_ROLE + 11
    SECTION_KEY_ROLE = ITEM_ID_ROLE + 12
    EXTRA_ROLE = ITEM_ID_ROLE + 13
    IS_EXPLICIT_ROLE = ITEM_ID_ROLE + 14
    ARTISTS_ROLE = ITEM_ID_ROLE + 15
    ALBUM_ID_ROLE = ITEM_ID_ROLE + 16
    ARTIST_ID_ROLE = ITEM_ID_ROLE + 17
    PLAYLIST_INDEX_ROLE = ITEM_ID_ROLE + 18
    IS_USER_PLAYLIST_ROLE = ITEM_ID_ROLE + 19
    ALLOW_STREAMING_ROLE = ITEM_ID_ROLE + 20
    
    def __init__(self = None, parent = None):
        '''
        初始化通用列表模型。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._items = []

    
    def rowCount(self = None, parent = None):
        '''
        返回当前条目数。

        :param parent: 父级索引。
        :return: 条目数量。
        '''
        if parent.isValid():
            return 0
        return None(self._items)

    
    def data(self = None, index = None, role = None):
        '''
        根据索引与角色返回条目字段。

        :param index: 模型索引。
        :param role: Qt 角色值。
        :return: 对应字段值。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._items):
            return None
        item = None._items[row]
        if role == self.ITEM_ID_ROLE:
            return item.get('itemId', '')
        if None == self.ITEM_TYPE_ROLE:
            return item.get('itemType', '')
        if None == self.TITLE_ROLE:
            return item.get('title', '')
        if None == self.SUBTITLE_ROLE:
            return item.get('subtitle', '')
        if None == self.IMAGE_URL_ROLE:
            return item.get('imageUrl', '')
        if None == self.IMAGE_PATH_ROLE:
            return item.get('imagePath', '')
        if None == self.TRACK_COUNT_ROLE:
            if not item.get('trackCount', 0):
                pass
            return int(0)
        if None == self.DURATION_ROLE:
            return item.get('duration', '')
        if None == self.IS_FAVORITE_ROLE:
            return bool(item.get('isFavorite', False))
        if None == self.ARTIST_NAME_ROLE:
            return item.get('artistName', '')
        if None == self.ALBUM_NAME_ROLE:
            return item.get('albumName', '')
        if None == self.YEAR_ROLE:
            return item.get('year', '')
        if None == self.SECTION_KEY_ROLE:
            return item.get('sectionKey', '')
        if None == self.EXTRA_ROLE:
            return item
        if None == self.IS_EXPLICIT_ROLE:
            return bool(item.get('isExplicit', False))
        if None == self.ARTISTS_ROLE:
            artists = item.get('artists', [])
            if isinstance(artists, list):
                return artists
            return None
        if None == self.ALBUM_ID_ROLE:
            return item.get('albumId', '')
        if None == self.ARTIST_ID_ROLE:
            return item.get('artistId', '')
        if None == self.PLAYLIST_INDEX_ROLE:
            if 'playlistIndex' in item:
                if not item.get('playlistIndex', 0):
                    pass
                return int(0)
            extra = None.get('extra', { })
            if isinstance(extra, dict) and 'playlistIndex' in extra:
                if not extra.get('playlistIndex', 0):
                    pass
                return int(0)
            return None
        if None == self.IS_USER_PLAYLIST_ROLE:
            return bool(item.get('isUserPlaylist', False))
        if None == self.ALLOW_STREAMING_ROLE:
            return bool(item.get('allowStreaming', True))

    
    def roleNames(self = None):
        '''
        返回 QML 角色映射。

        :return: 角色名字典。
        '''
        return {
            self.ALLOW_STREAMING_ROLE: b'allowStreaming',
            self.IS_USER_PLAYLIST_ROLE: b'isUserPlaylist',
            self.PLAYLIST_INDEX_ROLE: b'playlistIndex',
            self.ARTIST_ID_ROLE: b'artistId',
            self.ALBUM_ID_ROLE: b'albumId',
            self.ARTISTS_ROLE: b'artists',
            self.IS_EXPLICIT_ROLE: b'isExplicit',
            self.EXTRA_ROLE: b'extra',
            self.SECTION_KEY_ROLE: b'sectionKey',
            self.YEAR_ROLE: b'year',
            self.ALBUM_NAME_ROLE: b'albumName',
            self.ARTIST_NAME_ROLE: b'artistName',
            self.IS_FAVORITE_ROLE: b'isFavorite',
            self.DURATION_ROLE: b'duration',
            self.TRACK_COUNT_ROLE: b'trackCount',
            self.IMAGE_PATH_ROLE: b'imagePath',
            self.IMAGE_URL_ROLE: b'imageUrl',
            self.SUBTITLE_ROLE: b'subtitle',
            self.TITLE_ROLE: b'title',
            self.ITEM_TYPE_ROLE: b'itemType',
            self.ITEM_ID_ROLE: b'itemId' }

    
    def clear(self = None):
        '''
        清空所有条目。

        :return: None。
        '''
        if not self._items:
            return None
        None.beginResetModel()
        self._items = []
        self.endResetModel()

    
    def setItems(self = None, items = None):
