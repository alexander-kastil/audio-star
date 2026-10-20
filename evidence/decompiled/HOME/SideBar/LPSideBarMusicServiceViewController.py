# Source Generated with Decompyle++
# File: LPSideBarMusicServiceViewController.pyc (Python 3.9)

'''
@Time ： 2025/12/29 18:19
@Auth ： Chris
@File ：LPSideBarMusicServiceViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtGui import QPainter, QBrush, QPixmap, QColor, QPainterPath, QIcon, QFont
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QCoreApplication, QAbstractListModel, QSize, QRectF, QTimer, QEvent
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import Min_Text, Sub_Text
from LPClientFramework.LPDeviceStreamServiceManager import LPDeviceStreamServiceManager
from LPClientFramework.LPUtility import logger
from HOME.SideBar.LPSideBarListView import paintSideBarSelectedBackground

class LPMusicServiceListModel(QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        '''
        初始化 Music Services 列表模型。

        参数:
            data: 音源服务条目数据列表。
            parent: Qt 父对象。
        返回值:
            None。
        '''
        super().__init__(parent)
        self._data = data

    
    def rowCount(self, parent = (None,)):
        '''
        获取 Music Services 条目数量。

        参数:
            parent: Qt 模型父索引。
        返回值:
            int: 当前数据条目数量。
        '''
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        '''
        获取指定索引和角色的数据。

        参数:
            index: Qt 模型索引。
            role: Qt 数据角色。
        返回值:
            object: 当前服务条目数据；无效时返回 None。
        '''
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        item = None._data[row]
        if role == Qt.ItemDataRole.DisplayRole:
            return item

    
    def setRowAccount(self, source, showName):
        '''
        更新指定音源的账号展示名。

        参数:
            source: 音源标识。
            showName: 账号展示名。
        返回值:
            None。
        '''
        row = None((lambda .0 = None: 