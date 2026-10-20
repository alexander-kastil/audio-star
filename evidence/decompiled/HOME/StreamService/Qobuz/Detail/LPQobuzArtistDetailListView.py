# Source Generated with Decompyle++
# File: LPQobuzArtistDetailListView.pyc (Python 3.9)

'''
@Time ： 2025/5/29 16:27
@Auth ： Chris
@File ：LPQobuzListView.py
@Desc:
'''
from PyQt6.QtCore import QSize, Qt, QRectF, QRect
from PyQt6.QtGui import QBrush, QPainterPath, QIcon, QPixmap, QFont, QFontMetrics, QPainter, QColor
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QToolTip
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle

class LPQobuzAlbumDelegate(QStyledItemDelegate):
    
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
            pixmap = LPUtility.getCachedPixmapWithUrl(playItem.trackImage, 155)
            if pixmap:
                pass
            else:
                pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        else:
            pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
        hi_res = playItem.hires
        if playItem.trackVersion:
            if not playItem.trackName:
                pass
            title = f'''{''} ({playItem.trackVersion})'''
        elif not playItem.trackName:
            pass
        title = ''
        rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, 155, 25)
        if hi_res:
            rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, 125, 25)
        font = QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        title_rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, cellRect.width(), 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        title = QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        if hi_res:
            hi_resRect = QRect(cellRect.x() + 17 + 155 - 30, cellRect.y() + 22 + 155 + 25 + 10, 30, 30)
            icon = QIcon()
            pixmap = QPixmap(LPGlobalUI.imagePath('qobuz/hi-res.png'))
            icon.addPixmap(pixmap)
            icon.paint(painter, hi_resRect.x(), hi_resRect.y(), hi_resRect.width(), hi_resRect.height())
        if not playItem.date.split('-')[0]:
            pass
        year = ''
        artist = playItem.trackArtist
        rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 25 + 1, 155, 25)
        if hi_res:
            rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 25 + 1, 125, 25)
        font = QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        artist_rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 25 + 1, cellRect.width(), 25)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        artist = QFontMetrics(font).elidedText(artist, Qt.TextElideMode.ElideRight, rect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(artist_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, year)
        streamable = playItem.streamable
        if not streamable:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(coverRect, QColor(0, 0, 0, 160))
            painter.restore()
        if superListView.lastCursorPos:
            if cellRect.contains(superListView.lastCursorPos) or superListView.cursor() != Qt.CursorShape.PointingHandCursor:
                superListView.lastCursorActionIndex = index
                superListView.setCursor(Qt.CursorShape.PointingHandCursor)
            elif superListView.cursor() != Qt.CursorShape.ArrowCursor and superListView.lastCursorActionIndex == index:
                superListView.lastCursorActionIndex = None
                superListView.setCursor(Qt.CursorShape.ArrowCursor)

    
    def helpEvent(self = None, event = None, view = None, option = None, index = None):
