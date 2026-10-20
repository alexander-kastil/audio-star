# Source Generated with Decompyle++
# File: LPQobuzAddToPlaylistDialog.pyc (Python 3.9)

'''
@Time ： 2025/7/31 14:51
@Auth ： Chris
@File ：LPQobuzAddToPlaylistDialog.py
@Desc:
'''
import re
import threading
import time
from string import Template
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF, QRect, QSortFilterProxyModel, QModelIndex, QCoreApplication, pyqtSlot
from PyQt6.QtGui import QIcon, QBrush, QPainterPath, QPixmap, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QDialog, QButtonGroup, QStyledItemDelegate, QStyle, QToolTip
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPMSManager.Qobuz.LPQobuzManager import LPQobuzManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPQobuzPersonalPlaylistDelegate(QStyledItemDelegate):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.listview = parent

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QSize(265, 120)
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
        coverRect = QRect(cellRect.x() + 10, cellRect.y() + 10, 100, 100)
        icon = QIcon()
        if playItem.trackImage:
            pixmap = LPQobuzUtil.getCachedBlurredPixmapWithUrl(playItem.trackImage, 100)
            if pixmap:
                pass
            else:
                pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        elif playItem.playlistImageList:
            pixmap = LPQobuzUtil.getMyPlaylistCustomCoverImage(playItem.playlistImageList, 100)
        else:
            pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
        title = playItem.trackName
        font = QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        titleRect = QRect(cellRect.x() + 10 + 100 + 25, cellRect.y() + 25, cellRect.width() - 120 - 25, 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        title = QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, titleRect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(titleRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        subtitle = []
        tracksCount = playItem.tracksCount
        subtitle1 = f'''{tracksCount} {QCoreApplication.translate('qobuz add playlists', 'tracks')}'''
        subtitle.append(subtitle1)
        duration = playItem.trackDuration
        subtitle2 = LPQobuzUtil.formatAlbumDuration(duration)
        subtitle.append(subtitle2)
        subtitleText = ' · '.join(subtitle)
        font = QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        subTitleRect = QRect(cellRect.x() + 10 + 100 + 25, cellRect.y() + 25 + 25 + 15, cellRect.width() - 120 - 25, 25)
        painter.setPen(LPGlobalUI.THEME_DISABLE_COLOR)
        subTitle = QFontMetrics(font).elidedText(subtitleText, Qt.TextElideMode.ElideRight, subTitleRect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(subTitleRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, subTitle)

    
    def helpEvent(self = None, event = None, view = None, option = None, index = None):
