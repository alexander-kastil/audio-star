# Source Generated with Decompyle++
# File: LPQobuzSearchAllContentViewController.pyc (Python 3.9)

'''
@Time ： 2025/7/3 11:17
@Auth ： Chris
@File ：LPQobuzSearchContentViewController.py
@Desc:
'''
import copy
import queue
import threading
import time
from functools import partial
from string import Template
from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt, QRect, QCoreApplication, QModelIndex, QTimer
from PyQt6.QtGui import QMovie, QIcon, QPixmap, QFont, QCursor
from PyQt6.QtWidgets import QStyle, QListView, QAbstractItemView, QPushButton, QTableView, QHeaderView
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzArtistDelegate, LPQobuzAlbumDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistListModel, LPQobuzPlaylistDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController import LPQobuzAlbumDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController import LPQobuzPlaylistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Search.LPQobuzSearchBaseViewController import LPQobuzSearchBaseViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSearchTip
from LPClientFramework import LPUtility
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT, Qobuz_Sub_Title, Qobuz_Tab_Title
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem

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
        playItem = None.itemList[row]
        isCurrentPlay = LPGlobalUI.currentDevice.deviceStreamServiceManager.isCurrentPlayItem(LPPlayListSource.Qobuz.value, LPGlobalUI.currentDevice, playItem)
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return (str(row + 1), isCurrentPlay)
            if None == 1:
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
                return (playItem, image, isCurrentPlay)
            if None == 2:
                title = self.getName(playItem)
                subTitle = []
                type = self.getType(playItem)
                if not type:
                    pass
                subTitle.append('')
                subName = self.getsubName(playItem)
                if not playItem.isArtist:
                    subTitle.append(subName)
                return (title, playItem.parentalWarning, subTitle, isCurrentPlay)
            if None == 3:
                return (playItem.hires, isCurrentPlay)
            if None == 4:
                return (playItem, isCurrentPlay)
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
        if None.isPlaylist:
            return playItem.playlistName
        return None.trackName

    
    def getsubName(self, playItem):
        if playItem.isAlbum:
            return playItem.artistName
        if None.isArtist:
            return ''
        if None.isPlaylist:
            return ''
        return None.albumName

    
    def getType(self, playItem):
        if playItem.isAlbum:
            return 'Album'
        if None.isArtist:
            return 'Artist'
        if None.isPlaylist:
            return 'Playlist'
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
            if isPlayingItem:
                play_state = LPGlobalUI.currentDevice.mediaInfo.playState
                play_ani_size = 11
                ani_rect = QRect(cellRect.x() + 12, cellRect.y() + 24, play_ani_size, play_ani_size)
                if play_state == 'PLAYING':
                    current_frame = self.play_movie.currentPixmap()
                    painter.drawPixmap(ani_rect, current_frame)
                else:
                    play_icon = QIcon()
                    pixmap = QPixmap(LPGlobalUI.imagePath('dark_pause.png'))
                    play_icon.addPixmap(pixmap)
                    play_icon.paint(painter, ani_rect.x(), ani_rect.y(), play_ani_size, play_ani_size)
            else:
                rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
                font = QFont()
                font.setUnderline(False)
                painter.setFont(font)
                painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, data[0])
        elif index.column() == 1:
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
        elif index.column() == 2:
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
        elif index.column() == 3:
            rect = QRect(cellRect.x() + 12, cellRect.y() + 12, cellRect.width() - 12, cellRect.height() - 24)
            hi_res = data[0]
            if hi_res:
                hi_resRect = QRect(rect.x(), rect.y(), 30, 30)
                icon = QIcon()
                pixmap = QPixmap(LPGlobalUI.imagePath('qobuz/hi-res.png'))
                icon.addPixmap(pixmap)
                icon.paint(painter, hi_resRect.x(), hi_resRect.y(), hi_resRect.width(), hi_resRect.height())
            elif index.column() == 4:
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


class LPQobuzSearchAllContentViewController(LPQobuzSearchBaseViewController):
    initViewSignal = pyqtSignal(object, object)
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.parent = parent
        self.setParent(parent)
        self.offset = 50
        self.limit = 50
        self.total = self.defaultTotal
        self.loading = False
        self.firstShow = True
        self.itemType = None
        self.queryText = ''
        self.initViewSignal.connect(self._initView)

    
    def setupUi(self = None, ui = None):
