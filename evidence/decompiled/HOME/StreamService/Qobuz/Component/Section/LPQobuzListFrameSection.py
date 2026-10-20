# Source Generated with Decompyle++
# File: LPQobuzListFrameSection.pyc (Python 3.9)

'''
@Time ： 2025/7/11 14:02
@Auth ： Chris
@File ：LPQobuzListFrameSection.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import QModelIndex, Qt, QSortFilterProxyModel, QCoreApplication
from PyQt6.QtWidgets import QAbstractItemView
import LPGlobalUI
from HOME.StreamService.Qobuz.Component.LPQobuzListView import LPQobuzListModel, LPQobuzAlbumDelegate, LPQobuzArtistDelegate
from HOME.StreamService.Qobuz.Component.LPQobuzPlaylistListView import LPQobuzPlaylistDelegate, LPQobuzPlaylistListModel
from HOME.StreamService.Qobuz.Detail.LPQobuzAlbumDetailViewController import LPQobuzAlbumDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzArtistDetailViewController import LPQobuzArtistDetailViewController
from HOME.StreamService.Qobuz.Detail.LPQobuzPlaylistDetailViewController import LPQobuzPlaylistDetailViewController
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzAlbumDetailViewController_ui import Ui_qobuzAlbumDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzArtistDetailViewController_ui import Ui_qobuzArtistDetailViewWidget
from HOME.StreamService.Qobuz.Detail.UI.LPQobuzPlaylistDetailViewController_ui import Ui_qobuzPlaylistDetailViewWidget
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteAlbumSeeAllViewController import LPQobuzFavoriteAlbumSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoriteArtistSeeAllViewController import LPQobuzFavoriteArtistSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.LPQobuzFavoritePlaylistSeeAllViewController import LPQobuzFavoritePlaylistSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.Favorite.UI.LPQobuzFavoriteAlbumSeeAllViewController_ui import Ui_qobuzFAlbumSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.Favorite.UI.LPQobuzFavoriteArtistSeeAllViewController_ui import Ui_qobuzFArtistSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.Favorite.UI.LPQobuzFavoritePlaylistSeeAllViewController_ui import Ui_qobuzFPlaylistSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.LPQobuzAlbumSeeAllViewController import LPQobuzAlbumSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.LPQobuzPlaylistSeeAllViewController import LPQobuzPlaylistSeeAllViewController
from HOME.StreamService.Qobuz.SeeAll.UI.LPQobuzAlbumSeeAllViewController_ui import Ui_qobuzAlbumSeeAllWidget
from HOME.StreamService.Qobuz.SeeAll.UI.LPQobuzPlaylistSeeAllViewController_ui import Ui_qobuzPlaylistSeeAllWidget
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from HOME.StreamService.Qobuz.Util.LPQobuzPublicDefine import QobuzSectionTip
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import Qobuz_Sub_Title
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPListViewSkeleton import LPListViewSkeletonListModel, LPListViewSkeletonDelegateWithSize

class GenreFilterProxyModel(QSortFilterProxyModel):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
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