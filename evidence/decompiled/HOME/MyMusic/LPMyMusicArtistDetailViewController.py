# Source Generated with Decompyle++
# File: LPMyMusicArtistDetailViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
import threading
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.MyMusic import LPMyMusicAlbumDetailViewController
from HOME.MyMusic.LPMyMusicAlbumDetailViewController_ui import Ui_mymusicAlbumDetailViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from HOME.MyMusic.LPTrackImageLoadHelper import LPTrackImageLoadHelper
from LPClientFramework import LPUtility, LPBeetsWrapper, LPStreamServiceManager
from LPCommonWidgets.Label.LPElideLabel import LPElideLabel
from LPCommonWidgets.widget_utils import replaceWidgetInPlace
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, ItemCard_Title, ItemCard_Subtitle, MyMusic_ArtistAbout
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger

class LPMyMusicAlbumsListModel(QtCore.QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        super(LPMyMusicAlbumsListModel, self).__init__(parent)
        self._data = data

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            albumDict = self._data[row]
            return albumDict

    __classcell__ = None


class LPMyMusicAlbumDelegate(QStyledItemDelegate):
    mouseClicked = QtCore.pyqtSignal(object, object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QtCore.QSize(190, 265)
        return result

    
    def editorEvent(self = None, event = None, model = None, option = None, index = None):
        cellRect = option.rect
        playIconRect = QtCore.QRect(cellRect.x() + 115, cellRect.y() + 120, 50, 50)
        if event.type() == QEvent.Type.MouseButtonPress:
            if playIconRect.contains(event.pos()):
                self.mouseClicked.emit(index, 'play')
            else:
                self.mouseClicked.emit(index, 'enter')
        return super().editorEvent(event, model, option, index)

    
    def paint(self, painter, option, index):
        data = index.data()
        if data is None:
            return None
        cellRect = None.rect
        superListView = option.styleObject
        brush = QtGui.QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        if option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        else:
            brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        coverRect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22, 155, 155)
        pixmap = LPUtility.coverImageForLocalPath(data['path'])
        if pixmap is None:
            pixmap = QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon = QtGui.QIcon()
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
        playIconRect = QtCore.QRect(cellRect.x() + 115, cellRect.y() + 120, 50, 50)
        if option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(QtGui.QColor(0, 0, 0, 20))
            path = QtGui.QPainterPath()
            path.addRect(coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
            painter.fillPath(path, brush)
            pixmap = QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/play.png'))
            icon = QtGui.QIcon()
            icon.addPixmap(pixmap)
            if superListView.lastCursorPos and playIconRect.contains(superListView.lastCursorPos):
                icon.paint(painter, playIconRect.x() - 1, playIconRect.y() - 1, playIconRect.width() + 2, playIconRect.height() + 2)
            else:
                icon.paint(painter, playIconRect.x(), playIconRect.y(), playIconRect.width(), playIconRect.height())
        title = data['album']
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10, 155, 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        metrics = QtGui.QFontMetrics(font)
        title = QtGui.QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop, title)
        artist = data['artist']
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10 + 25, 155, 50)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        textLayout = QtGui.QTextLayout(artist, font)
        height = 0
        lineWidth = rect.width()
        textLayout.beginLayout()
        metrics = QtGui.QFontMetrics(font)
        leading = metrics.leading()
        height = -leading
        line = textLayout.createLine()
        if not line.isValid():
            pass
        else:
            line.setLineWidth(lineWidth)
            height += leading
            line.setPosition(QtCore.QPointF(0, height))
            height += line.height()
        textLayout.endLayout()
        if textLayout.lineCount() >= 3:
            line1 = textLayout.lineAt(0)
            line2 = textLayout.lineAt(1)
            line3 = textLayout.lineAt(2)
            lineText = artist[line2.textStart():line2.textStart() + line2.textLength()] + artist[line3.textStart():line3.textStart() + line3.textLength()]
            lineText = metrics.elidedText(lineText, Qt.TextElideMode.ElideRight, rect.width())
            artist = artist[0:line1.textLength()] + lineText
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.TextFlag.TextWordWrap, artist)
        if superListView.lastCursorPos:
            if not cellRect.contains(superListView.lastCursorPos) and playIconRect.contains(superListView.lastCursorPos):
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.ArrowCursor))

    __classcell__ = None


class ProxyStyle(QProxyStyle):
    '''表头排序样式代理：隐藏第一列排序箭头。'''
    
    def drawControl(self = None, ctl = None, opt = None, qp = None, widget = None):
        '''
        自定义绘制表头控件，屏蔽指定列排序图标。

        参数:
            ctl (QStyle.ControlElement): 当前绘制的控件类型。
            opt (QStyleOption): 当前样式选项。
            qp (QPainter): 当前绘制器。
            widget (QWidget | None): 当前目标控件。
        返回:
            无
        '''
        if ctl == QStyle.ControlElement.CE_HeaderSection and opt.orientation == QtCore.Qt.Orientation.Horizontal and opt.section == widget.parent().property('hideSortIndicatorColumn'):
            opt.sortIndicator = QStyleOptionHeader.SortIndicator.None_
        super().drawControl(ctl, opt, qp, widget)

    __classcell__ = None

filterArray = []

class LPMyMusicTracksTableModel(QtCore.QAbstractTableModel):
    '''歌手详情曲目表格模型：负责曲目展示和可见区优先封面加载。'''
    
    def __init__(self = None, playList = None, artistDict = None, parent = None):
        '''
        初始化歌手详情曲目表格模型。

        参数:
            playList (object): 当前歌手曲目播放列表。
            artistDict (dict): 当前歌手信息字典。
            parent (QObject | None): Qt 父对象。
        返回:
            无
        '''
        super(LPMyMusicTracksTableModel, self).__init__(parent)
        self.artistDict = artistDict
        self.playList = playList
        self._data = playList.list
        self.trackImageLoadHelper = LPTrackImageLoadHelper(self._imageUrlForRow, self.rowCount, LPUtility, self, **('parent',))
        self.trackImageLoadHelper.rowImageReadySignal.connect(self._handleRowImageReady)

    
    def headerData(self = None, section = None, orientation = None, role = None):
        '''
        返回表头文案。

        参数:
            section (int): 表头索引。
            orientation (Qt.Orientation): 表头方向。
            role (Qt.ItemDataRole): 数据角色。
        返回:
            object: 表头展示文本或基类返回值。
        '''
        labels = []
        for item in filterArray:
            labels.append(item['title'])
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return labels[section]
        return None().headerData(section, orientation, role)

    
    def rowCount(self, parent = (None,)):
        '''
        返回模型行数。

        参数:
            parent (QModelIndex | None): 父级索引。
        返回:
            int: 当前行数。
        '''
        return len(self._data)

    
    def columnCount(self, parent = (None,)):
        '''
        返回模型列数。

        参数:
            parent (QModelIndex | None): 父级索引。
        返回:
            int: 当前列数。
        '''
        if self.rowCount() > 0:
            return 4

    
    def data(self, index, role = (QtCore.Qt.ItemDataRole.DisplayRole,)):
