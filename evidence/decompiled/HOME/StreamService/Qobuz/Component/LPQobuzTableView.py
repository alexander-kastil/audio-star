# Source Generated with Decompyle++
# File: LPQobuzTableView.pyc (Python 3.9)

'''
@Time ： 2025/7/1 11:38
@Auth ： Chris
@File ：LPQobuzTableView.py
@Desc:
'''
import queue
import threading
import time
from PyQt6.QtCore import QAbstractTableModel, Qt, QCoreApplication, QRect, pyqtSignal, QModelIndex
from PyQt6.QtGui import QMovie, QIcon, QPixmap, QFont, QPainter, QColor, QFontMetrics
from PyQt6.QtWidgets import QStyle, QAbstractItemView, QToolTip
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger
TABLE_COLUMNS = 6

class LPQobuzTracksTableWithCoverModel(QAbstractTableModel):
    
    def __init__(self = None, playList = None, parent = None):
        super().__init__(parent)
        self.playList = playList
        self._data = playList.list
        self.trackImageQueue = queue.Queue()
        self.fetchImageThread = None

    
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
