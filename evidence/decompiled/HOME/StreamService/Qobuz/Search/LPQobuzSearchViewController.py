# Source Generated with Decompyle++
# File: LPQobuzSearchViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/24 15:50
@Auth ： Chris
@File ：LPQobuzSearchViewController.py
@Desc:
'''
import queue
import re
import threading
import time
from string import Template
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QAbstractTableModel, QRect, QSortFilterProxyModel, QTimer, pyqtSlot
from PyQt6.QtGui import QMovie, QIcon, QPixmap
from PyQt6.QtWidgets import QButtonGroup, QSizePolicy, QPushButton, QStyle
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchAllContentViewController import LPQobuzSearchAllContentViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchBaseViewController import LPQobuzSearchBaseViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchListContentViewController import LPQobuzSearchListContentViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchTableContentViewController import LPQobuzSearchTableContentViewController
from HOME.StreamService.Qobuz.Search.UI.LPQobuzSearchAllContentWidget_ui import Ui_searchAllContentWidget
from HOME.StreamService.Qobuz.Search.UI.LPQobuzSearchListContentWidget_ui import Ui_searchListContentWidget
from HOME.StreamService.Qobuz.Search.UI.LPQobuzSearchTableContentWidget_ui import Ui_searchTableContentWidget
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Tab_Title, Qobuz_Sub_Title, DEFAULT
from LPClientFramework.LPNetworkClient.LPNetworkClient import LPRequestCommonResult
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPHeaderType
from LPClientFramework.LPUtility import logger

class LPSearchFilterProxyModel(QSortFilterProxyModel):
    
    def __init__(self = None):
        super().__init__()
        self.type = None

    
    def setFilterPattern(self, type):
        self.type = type
        self.invalidateFilter()

    
    def filterAcceptsRow(self, source_row, source_parent):
        if not self.type:
            return True
        model = None.sourceModel()
        index = model.index(source_row, 0, source_parent)
        playItem = model.data(index, Qt.ItemDataRole.UserRole)
        type = model.getType(playItem)
        return self.type == type

    __classcell__ = None


class LPQobuzSearchTableModel(QAbstractTableModel):
    updateFavoriteSignal = pyqtSignal(object, object)
    
    def __init__(self = None, itemList = None, parent = None):
        super().__init__(parent)
        self.itemList = itemList
        self.trackImageQueue = queue.Queue()
        self.fetchImageThread = None

    
    def rowCount(self, parent = (None,)):
        return len(self.itemList)

    
    def columnCount(self, parent = (None,)):
        if self.rowCount() > 0:
            return 4

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        column = index.column()
        if row >= self.rowCount() or row < 0:
            return None
        if None >= self.columnCount() or column < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            playItem = self.itemList[row]
            if column == 0:
                image = self.getImage(playItem)
                if image and len(image) > 0:
                    pixmap = LPUtility.getCachedPixmapWithUrl(image, 45)
                    if pixmap is None:
                        
                        def _fetchImageMethod():
                            if self.trackImageQueue.empty():
                                time.sleep(1)
                                continue
                            dataDict = self.trackImageQueue.get()
                            url = dataDict.get('value', None)
                            indexObj = dataDict.get('index', None)
                            respDict = LPUtility.fetchUrlQPixmap(url, False, 45)
                            pixmap = respDict.get('image', None)
                            if pixmap:
                                self.dataChanged.emit(indexObj, indexObj)
                            self.trackImageQueue.task_done()
                            continue

                        self.trackImageQueue.put({
                            'value': image,
                            'index': index })
                        if self.fetchImageThread is None:
                            self.fetchImageThread = threading.Thread(_fetchImageMethod, True, **('target', 'daemon'))
                            self.fetchImageThread.start()
                return (playItem, image, LPGlobalUI.currentDevice.deviceStreamServiceManager.isCurrentPlayItem(LPPlayListSource.Qobuz.value, LPGlobalUI.currentDevice, playItem))
            if None == 1:
                title = self.getName(playItem)
                subTitle = []
                type = self.getType(playItem)
                if not type:
                    pass
                subTitle.append('')
                if not playItem.isArtist:
                    if not 'Chris Anna':
                        pass
                    subTitle.append('')
                return (title, playItem.parentalWarning, subTitle, LPGlobalUI.currentDevice.deviceStreamServiceManager.isCurrentPlayItem(LPPlayListSource.Qobuz.value, LPGlobalUI.currentDevice, playItem))
            if None == 2:
                return (playItem.hires,)
            if None == 3:
                
                def _formatSeconds(seconds):
                    seconds = seconds / 1000
                    seconds = seconds % 86400
                    hour = seconds // 3600
                    seconds %= 3600
                    minutes = seconds // 60
                    seconds %= 60
                    if hour != 0:
                        return '%d:%02d:%02d' % (hour, minutes, seconds)
                    return None % (minutes, seconds)

                return (playItem,)
        if role == Qt.ItemDataRole.UserRole:
            playItem = self.itemList[row]
            return playItem

    
    def getImage(self, playItem):
        if playItem.isAlbum:
            return playItem.albumImage
        if None.isArtist:
            return playItem.artistImage

    
    def getName(self, playItem):
        if playItem.isAlbum:
            return playItem.albumName
        if None.isArtist:
            return playItem.artistName

    
    def getType(self, playItem):
        if playItem.isAlbum:
            return 'Albums'
        if None.isArtist:
            return 'Artists'
        if None.isPlaylist:
            return 'Playlists'
        return None

    __classcell__ = None


class LPQobuzSearchTableDelegate(LPSuperTableDelegate):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.table_view = parent
        self.play_movie = QMovie(LPGlobalUI.imagePath('dark_playing.gif'))
        self.play_movie.start()
        self.play_movie.frameChanged.connect(self.update_view)

    
    def paint(self = None, painter = None, option = None, index = None):
        super().paint(painter, option, index)
        data = index.data()
        if data is None:
            return None
        isPlayingItem = None
        if isPlayingItem:
            painter.setPen(LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        elif option.state & QStyle.StateFlag.State_Selected:
            painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        else:
            painter.setPen(LPGlobalUI.THEME_DISABLE_COLOR)
        cellRect = option.rect
        if index.column() == 0:
            isArtist = data[0].isArtist
            icon = QIcon()
            if data[1]:
                pixmap = LPUtility.getCachedPixmapWithUrl(data[1], 45)
                if pixmap:
                    pass
                else:
                    pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
            else:
                pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
            if isArtist:
                pixmap = LPUtility.roundCornerImage(pixmap, 310)
            icon.addPixmap(pixmap)
            icon.paint(painter, cellRect.x() + 5, cellRect.y() + 8, 45, 45)
        elif index.column() == 1:
            rect = QRect(cellRect.x() + 5, cellRect.y() + 5, cellRect.width() - 12, cellRect.height() - 24)
            painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, data[0])
            if data[1]:
                parentalWarningRect = QRect(cellRect.x() + 5, cellRect.y() + 38, 12, 12)
                icon = QIcon()
                pixmap = QPixmap(LPGlobalUI.imagePath('qobuz/e_warning.png'))
                icon.addPixmap(pixmap)
                icon.paint(painter, parentalWarningRect.x(), parentalWarningRect.y(), parentalWarningRect.width(), parentalWarningRect.height())
                subtitleRect = QRect(cellRect.x() + 5 + 12 + 5, cellRect.y() + 20, cellRect.width() - 12, cellRect.height() - 12)
            else:
                subtitleRect = QRect(cellRect.x() + 5, cellRect.y() + 20, cellRect.width() - 12, cellRect.height() - 12)
            painter.drawText(subtitleRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, ' · '.join(data[2]))
        elif index.column() == 2:
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
            hi_res = data[0]
            if hi_res:
                hi_resRect = QRect(rect.x(), rect.y(), 30, 30)
                icon = QIcon()
                pixmap = QPixmap(LPGlobalUI.imagePath('qobuz/hi-res.png'))
                icon.addPixmap(pixmap)
                icon.paint(painter, hi_resRect.x(), hi_resRect.y(), hi_resRect.width(), hi_resRect.height())
            elif index.column() == 3:
                rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
                playItem = data[0]
                if playItem.isAlbum or playItem.isArtist:
                    pixmap = QPixmap(LPGlobalUI.imagePath('nav_next.png'))
                else:
                    pixmap = QPixmap(LPGlobalUI.imagePath('more.png'))
                pixRect = QRect(rect.x(), rect.y(), 30, 30)
                icon = QIcon()
                icon.addPixmap(pixmap)
                icon.paint(painter, pixRect.x(), pixRect.y(), pixRect.width(), pixRect.height())

    
    def update_view(self):
        if self.table_view:
            self.table_view.viewport().update()

    
    def cleanup_table_view(self):
        self.play_movie.stop()

    __classcell__ = None


class LPQobuzSearchViewController(LPQobuzSearchBaseViewController):
    updateContentSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.parent = parent
        self.offset = 0
        self.limit = 50
        self.summaryDict = None
        self.tagList = [
            'Top',
            'Artists',
            'Albums',
            'Tracks',
            'Playlists']
        self.tagBinding = [
            {
                'tag': 'Top',
                'headType': None },
            {
                'tag': 'Artists',
                'headType': LPHeaderType.LP_HEADER_TYPE_ARTIST },
            {
                'tag': 'Albums',
                'headType': LPHeaderType.LP_HEADER_TYPE_ALBUM },
            {
                'tag': 'Tracks',
                'headType': LPHeaderType.LP_HEADER_TYPE_SONG },
            {
                'tag': 'Playlists',
                'headType': LPHeaderType.LP_HEADER_TYPE_PLAYLIST }]
        self.currentTag = self.tagList[0]
        self.currentView = None
        self.contentViewIndexMap = { }
        self.parent.searchFieldClearAction.triggered.connect(self.onFieldClearActionTriggered)
        self.refreshTimer = QTimer()
        self.refreshTimer.setSingleShot(True)
        self.refreshTimer.timeout.connect(self._doSearch)
        self.updateContentSignal.connect(self.updateContent)

    
    def setupUi(self = None, ui = None):
