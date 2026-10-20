# Source Generated with Decompyle++
# File: LPQueueViewController.pyc (Python 3.9)

from distutils.version import LooseVersion
from string import Template
import LPGlobalUI
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication, pyqtSlot, QMimeData, QModelIndex, QSize, QTimer, QPoint
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction, QPen, QColor, QPixmap, QIcon, QMovie, QCursor
from enum import Enum
import threading
import queue
import time
from HOME.LPSuperTableView import LPSuperTableDelegate
from LPClientFramework import LPUtility, LPStreamServiceManager
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT, Table_Subtitle, StackWidget_Title
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPFeature import LPFeatureCanUtils
from LPClientFramework.LPMediaInfo import LPLoopMode
from LPClientFramework.LPMenu.LPActionGroup import ACTION_QUEUE_GROUP
from LPClientFramework.LPMenu.LPContextMenuManager import ContextMenuManager
from LPClientFramework.LPQueueManager import LPQueueState
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.dialog.LPDialog import LPDialog
filterArray = []

class LPQueueTableModel(QtCore.QAbstractTableModel):
    
    def __init__(self = None, playList = None, parent = None):
        super(LPQueueTableModel, self).__init__(parent)
        self.playList = playList
        self._data = playList.list if playList else []
        self.trackImageQueue = queue.Queue()
        self.fetchImageThread = None

    
    def headerData(self = None, section = None, orientation = None, role = None):
        labels = []
        for item in filterArray:
            labels.append(item['title'])
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return labels[section]
        return None().headerData(section, orientation, role)

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def columnCount(self, parent = (None,)):
        if self.rowCount() > 0:
            return 3

    
    def data(self, index, role = (QtCore.Qt.ItemDataRole.DisplayRole,)):
