# Source Generated with Decompyle++
# File: LPQobuzPlaylistListView.pyc (Python 3.9)

'''
@Time ： 2025/7/23 11:20
@Auth ： Chris
@File ：LPQobuzPlaylistListView.py
@Desc:
'''
import queue
import time
from threading import Thread
from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QRectF, QRect
from PyQt6.QtGui import QBrush, QPainterPath, QIcon, QPixmap, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QToolTip
import LPGlobalUI
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle
from LPClientFramework.LPUtility import logger

class LPQobuzPlaylistListModel(QAbstractListModel):
    
    def __init__(self = None, playList = None, parent = None):
        super().__init__(parent)
        self.playList = playList
        self._data = self.playList.list
        self.coverImageQueue = queue.Queue()
        self.fetchImageThread = None
        self.imageUpdateRunning = True
        if parent:
            parent.destroyed.connect(self.cleanup)

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def flags(self = None, index = None):
        playItem = index.data(Qt.ItemDataRole.UserRole)
        defaultFlags = super().flags(index)
        streamable = playItem.streamable
        if not streamable:
            return defaultFlags & ~(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        playItem = None._data[row]
        if role == Qt.ItemDataRole.DisplayRole:
            imageUrl = playItem.trackImage
            if imageUrl and len(imageUrl) > 0:
                self.fetchPixmap(index, imageUrl, True, **('isBlurred',))
                return playItem
            imageUrlArr = None.playlistImageList
            if imageUrlArr:
                for _url in imageUrlArr:
                    self.fetchPixmap(index, _url)
            return playItem
        if None == Qt.ItemDataRole.UserRole:
            return playItem

    
    def fetchPixmap(self, index, imageUrl, isBlurred = (False,)):
        if isBlurred:
            exist = LPQobuzUtil.checkCachedBlurredPixmapWithUrl(imageUrl, 155)
        else:
            exist = LPUtility.checkCachedPixmapWithUrl(imageUrl, 155)
        if not exist:
            self.coverImageQueue.put({
                'value': imageUrl,
                'index': index,
                'isBlurred': isBlurred })
        
        def _fetchImageMethod():
            if not self.imageUpdateRunning:
                return None
            if None.coverImageQueue.empty():
                time.sleep(0.3)
                continue
            dataDict = self.coverImageQueue.get()
            url = dataDict.get('value', None)
            indexObj = dataDict.get('index', None)
            isBlurred = dataDict.get('isBlurred', False)
            if isBlurred:
                respDict = LPQobuzUtil.fetchUrlBlurredQPixmap(url, False, 155)
            else:
                respDict = LPUtility.fetchUrlQPixmap(url, False, 155)
            pixmap = respDict.get('image', None)
            if pixmap:
                self.dataChanged.emit(indexObj, indexObj)
            self.coverImageQueue.task_done()
            continue

        if self.fetchImageThread is None:
            self.fetchImageThread = Thread(_fetchImageMethod, True, **('target', 'daemon'))
            self.fetchImageThread.start()

    
    def cleanup(self):
        logger.debug('cleanup ================')
        if self.fetchImageThread:
            self.imageUpdateRunning = False

    
    def addItemList(self, playList):
        start = len(self._data)
        end = start + len(playList.list) - 1
        if playList.list:
            self.beginInsertRows(QModelIndex(), start, end)
            self._data.extend(playList.list)
            self.endInsertRows()

    __classcell__ = None


class LPQobuzPlaylistDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.listview = parent

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QSize(190, 265)
        return result

    
    def paint(self, painter, option, index):
        playItem = index.data()
        if playItem is None:
            return None
        cellRect = None.rect
        superListView = option.styleObject
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        if option.state & QStyle.StateFlag.State_Selected:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        else:
            brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QPainterPath()
        path.addRoundedRect(QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        coverRect = QRect(cellRect.x() + 17, cellRect.y() + 22, 155, 155)
        icon = QIcon()
        if playItem.trackImage:
            pixmap = LPQobuzUtil.getCachedBlurredPixmapWithUrl(playItem.trackImage, 155)
            if pixmap:
                pass
            else:
                pixmap = QPixmap(LPGlobalUI.imagePath('playlist_l.png'))
        elif playItem.playlistImageList:
            pixmap = LPQobuzUtil.getMyPlaylistCustomCoverImage(playItem.playlistImageList)
        else:
            pixmap = QPixmap(LPGlobalUI.imagePath('playlist_l.png'))
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
        title = playItem.trackName
        rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, 155, 25)
        font = QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        title_rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, cellRect.width(), 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        title = QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        subTitle = 'By ' + playItem.trackOwner
        rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 25 + 1, 155, 25)
        font = QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        subTitleRect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 25 + 1, cellRect.width(), 25)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        subTitle = QFontMetrics(font).elidedText(subTitle, Qt.TextElideMode.ElideRight, rect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(subTitleRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, subTitle)
        if superListView.lastCursorPos:
            if cellRect.contains(superListView.lastCursorPos) or superListView.cursor() != Qt.CursorShape.PointingHandCursor:
                superListView.lastCursorActionIndex = index
                superListView.setCursor(Qt.CursorShape.PointingHandCursor)
            elif superListView.cursor() != Qt.CursorShape.ArrowCursor and superListView.lastCursorActionIndex == index:
                superListView.lastCursorActionIndex = None
                superListView.setCursor(Qt.CursorShape.ArrowCursor)

    
    def helpEvent(self = None, event = None, view = None, option = None, index = None):
