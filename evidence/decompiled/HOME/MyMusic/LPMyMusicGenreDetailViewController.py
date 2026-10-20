# Source Generated with Decompyle++
# File: LPMyMusicGenreDetailViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
import LPGlobalUI
from HOME.LPSuperTableView import LPSuperTableDelegate
from HOME.MyMusic.LPMyMusicAlbumDetailViewController import LPMyMusicAlbumDetailViewController
from HOME.MyMusic.LPMyMusicAlbumDetailViewController_ui import Ui_mymusicAlbumDetailViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController import LPMyMusicArtistDetailViewController
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from HOME.MyMusic.LPTrackImageLoadHelper import LPTrackImageLoadHelper
from LPClientFramework import LPStreamServiceManager, LPUtility, LPBeetsWrapper
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
filterArray = []

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


class LPMyMusicTracksTableModel(QtCore.QAbstractTableModel):
    '''流派详情曲目表格模型：负责曲目展示和可见区优先封面加载。'''
    
    def __init__(self = None, playList = None, genreDict = None, parent = None):
        '''
        初始化流派详情曲目表格模型。

        参数:
            playList (object): 当前流派曲目播放列表。
            genreDict (dict): 当前流派信息字典。
            parent (QObject | None): Qt 父对象。
        返回:
            无
        '''
        super(LPMyMusicTracksTableModel, self).__init__(parent)
        self.genreDict = genreDict
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
            return 5

    
    def data(self, index, role = (QtCore.Qt.ItemDataRole.DisplayRole,)):
