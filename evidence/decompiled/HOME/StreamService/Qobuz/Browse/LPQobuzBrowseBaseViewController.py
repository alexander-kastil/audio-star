# Source Generated with Decompyle++
# File: LPQobuzBrowseBaseViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/30 16:08
@Auth ： Chris
@File ：LPQobuzBrowseBaseViewController.py
@Desc:
'''
import enum
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QRect
from PyQt6.QtWidgets import QListView, QTableView
import LPGlobalUI
from HOME.StreamService.Qobuz.LPQobuzBaseViewController import LPQobuzBaseViewController
from HOME.StreamService.Qobuz.Skeleton.LPQobuzSkeletonLibraryViewController import LPQobuzSkeletonLibraryViewController
from HOME.StreamService.Qobuz.Skeleton.UI.Browse.LPQobuzSkeletonLibrary_ui import Ui_qobuzSkeletonLibraryWidget
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.skeleton.LPListViewSkeleton import LPListViewSkeletonListModel, LPListViewSkeletonDelegateWithSize
from LPCommonWidgets.skeleton.LPTableViewSkeleton import LPTableViewSkeletonTableModel, LPTableViewSkeletonDelegate

class LPQobuzBrowseType(enum.Enum):
    DISCOVER = 'discover'
    LIBRARY = 'library'


class LPQobuzBrowseBaseViewController(LPQobuzBaseViewController):
    loadDataSignal = pyqtSignal(object, object)
    loadSectionSignal = pyqtSignal()
    updateSectionUISignal = pyqtSignal(object, object)
    loadSkeletonSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        super().__init__()
        self.offset = 0
        self.limit = 25
        self.loadDataSignal.connect(self._loadData)
        self.skeleton = None
        self.sectionBinding = None
        self.viewMap = { }
        self.updateSectionUISignal.connect(self.updateSectionUI)
        self.loadSkeletonSignal.connect(self.loadSkeleton)

    
    def updateSectionUI(self, binding, playList):
        self.endSkeleton()
        section = binding['id']
        binding['playList'] = playList
        view = self.viewMap.get(section)
        view.showContent(section, playList)

    updateSectionUI = pyqtSlot(object, object)(updateSectionUI)
    
    def hasPreData(self):
        if self.sectionBinding:
            for binding in self.sectionBinding:
                if binding['playList']:
                    return True
                return False
                return False
                return None

    
    def _loadData(self, genres, binding):
        pass

    _loadData = pyqtSlot(object, object)(_loadData)
    
    def loadSkeleton(self):
        if not self.skeleton:
            self.skeleton = LPGlobalUI.loadUI('./HOME/StreamService/Qobuz/Skeleton/UI/Browse/LPQobuzSkeletonLibrary_ui.ui', Ui_qobuzSkeletonLibraryWidget, LPQobuzSkeletonLibraryViewController, self)
        self.skeleton.showSkeleton()

    
    def endSkeleton(self):
        if self.skeleton:
            self.skeleton.hideSkeleton()

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        if self.skeleton and self.skeleton.isVisible():
            self.skeleton.adjustGeometry()

    __classcell__ = None

