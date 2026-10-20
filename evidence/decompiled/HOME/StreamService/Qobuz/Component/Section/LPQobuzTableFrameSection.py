# Source Generated with Decompyle++
# File: LPQobuzTableFrameSection.pyc (Python 3.9)

'''
@Time ： 2025/7/14 10:53
@Auth ： Chris
@File ：LPQobuzTableFrameSection.py
@Desc:
'''
import copy
import json
import threading
from functools import partial
from string import Template
from threading import Thread, Timer
from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt, QCoreApplication, QRect, pyqtSlot, QModelIndex, QTimer, QSize, QSortFilterProxyModel
from PyQt6.QtGui import QMovie, QFont, QPixmap, QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QStyle, QListView, QTableView, QPushButton, QHeaderView, QApplication, QScrollArea
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel, LPQobuzTrackTableWithCoverDelegate
from HOME.StreamService.Qobuz.Component.Option.LPQobuzTrackMoreMenu import LPQobuzTrackMoreMenu
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzDetailBaseViewController import LPQobuzDetailBaseViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController, LPQobuzPlayMode
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteTrackSeeAllViewController import LPQobuzFavoriteTrackSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.UI.LPQobuzFavoriteTrackSeeAllViewController_ui import Ui_qobuzFTrackSeeAllWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import MyMusic_Title, MyMusic_Subtitle, Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPPlayList.LPQobuzPlayList import LPQobuzPlayItem, HeadTitle_Favorite_Tracks, HeadTitle_Purchased_Tracks
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPTableViewSkeleton import LPTableViewSkeletonTableModel, LPTableViewSkeletonDelegate

class GenreFilterProxyModel(QSortFilterProxyModel):
    
    def __init__(self = None, parent = None, row_limit = None):
        super().__init__(parent)
        self._row_limit = row_limit
        self.selectedGenreIds = set()

    
    def setSelectedGenres(self = None, genre_ids = None):
        self.selectedGenreIds = genre_ids
        self.invalidateFilter()

    
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        playItem = model.data(index, Qt.ItemDataRole.UserRole)
        if not self.selectedGenreIds:
            return True
        genre_ids = (lambda 