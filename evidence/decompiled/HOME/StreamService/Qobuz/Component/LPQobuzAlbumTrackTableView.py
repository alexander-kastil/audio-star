# Source Generated with Decompyle++
# File: LPQobuzAlbumTrackTableView.pyc (Python 3.9)

'''
@Time ： 2025/7/22 16:58
@Auth ： Chris
@File ：LPQobuzAlbumTrackTableView.py
@Desc:
'''
from PyQt6.QtCore import QAbstractTableModel, Qt, QCoreApplication, QModelIndex, pyqtSignal, QRect
from PyQt6.QtGui import QMovie, QIcon, QFont, QPixmap, QColor, QCursor, QPainter, QFontMetrics
from PyQt6.QtWidgets import QStyle, QToolTip
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
TABLE_COLUMNS = 6

class LPQobuzAlbumTracksTableModel(QAbstractTableModel):
    
    def __init__(self = None, playList = None, parent = None):
        super().__init__(parent)
        self.playList = playList
        self._data = playList.list
        self.headerRows = set()

    
    def headerData(self = None, section = None, orientation = None, role = None):
        labels = []
        filterArray = [
            {
                'id': 'track',
                'title': '#' },
            {
                'id': 'title',
                'title': QCoreApplication.translate('AlbumDetail', 'Track') },
            {
                'id': 'artist',
                'title': QCoreApplication.translate('AlbumDetail', 'Artist') },
            {
                'id': 'length',
                'title': QCoreApplication.translate('AlbumDetail', 'Duration') },
            {
                'id': 'options',
                'title': QCoreApplication.translate('AlbumDetail', '') },
            {
                'id': 'options',
                'title': QCoreApplication.translate('AlbumDetail', '') }]
        for item in filterArray:
            labels.append(item['title'])
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return labels[section]
        return None().headerData(section, orientation, role)

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def columnCount(self, parent = (None,)):
        if self.rowCount() > 0:
            return TABLE_COLUMNS

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        column = index.column()
        if row >= self.rowCount() or row < 0:
            return None
        if None >= self.columnCount() or column < 0:
            return None
        playItem = None._data[row]
        if role == Qt.ItemDataRole.DisplayRole:
            isCurrentPlayItem = LPGlobalUI.currentDevice.deviceStreamServiceManager.isCurrentPlayItem(LPPlayListSource.Qobuz.value, LPGlobalUI.currentDevice, playItem)
            if column == 0:
                return ('%s' % (row + 1), isCurrentPlayItem)
            if None == 1:
                return (playItem.trackName, isCurrentPlayItem)
            if None == 2:
                return (playItem.trackArtist, playItem.parentalWarning, 'artist', playItem.artistId, isCurrentPlayItem)
            if None == 3:
                return (LPQobuzUtil.formatTrackDuration(playItem.trackDuration), 'duration', isCurrentPlayItem)
            if None == 4:
                return (playItem.isFavorite, 'favorite', isCurrentPlayItem)
            if None == 5:
                return (True, 'more', isCurrentPlayItem)
        if role == Qt.ItemDataRole.UserRole:
            return playItem
        if None == Qt.ItemDataRole.UserRole + 1:
            return self.playList.header.mediaCount
        if None == Qt.ItemDataRole.UserRole + 2:
            return self.getheaderRows()

    
    def removeRows(self, row, count, parent = (QModelIndex(),)):
        if row < 0 or row + count > len(self._data):
            return False
        None.beginRemoveRows(parent, row, row + count - 1)
        del self._data[row:row + count]
        self.endRemoveRows()
        return True

    
    def addItemList(self, playList):
        start = len(self._data)
        end = start + len(self._data) - 1
        if playList.list:
            self.beginInsertRows(QModelIndex(), start, end)
            self._data.extend(playList.list)
            self.endInsertRows()

    
    def getheaderRows(self):
