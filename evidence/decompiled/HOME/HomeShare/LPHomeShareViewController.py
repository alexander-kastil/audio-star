# Source Generated with Decompyle++
# File: LPHomeShareViewController.pyc (Python 3.9)

import threading
from functools import partial
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QCoreApplication, QEvent, QModelIndex
from PyQt6.QtGui import QAction
import LPGlobalUI
import urllib.parse as urllib
from PyQt6.QtGui import QStandardItem
from HOME.HomeShare.LPPagedTreeModel import LPHomeShareTreeNode, LPPagedTreeModel
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title
from LPClientFramework.LPPlayList import LPUPnPServerPlayList
from LPClientFramework.LPPlayList.LPPlayList import LPPlayItem
from LPClientFramework.LPUtility import logger
homeShareViewControllersArray = []
searchModel = LPPagedTreeModel()
commonModel = LPPagedTreeModel()
lock = threading.Lock()

def mediaServerAddMethod(serverObj):
    logger.info('mediaServerAddMethod %s: %s' % (serverObj.friendlyName, serverObj.ip))
    rootNode = commonModel.invisibleRootItem()
    item = LPHomeShareTreeNode(serverObj.directory, str(serverObj.friendlyName), rootNode, **('parent',))
    with lock:
        commonModel.appendRootNode(item)
        None(None, None, None)
    with None:
        if not None:
            pass
    for viewController in homeShareViewControllersArray:
        viewController.updateUISignal.emit()


def mediaServerRmvMethod(serverObj):
    logger.info('mediaServerRmvMethod %s' % serverObj.friendlyName)
    with lock:
        commonModel.removeFromRootNodeByIP(serverObj.ip)
        None(None, None, None)
    with None:
        if not None:
            pass
    for viewController in homeShareViewControllersArray:
        viewController.updateUISignal.emit()


def removeAll():
    commonModel.resetModel()
    searchModel.resetModel()
    for viewController in homeShareViewControllersArray:
        viewController.updateUISignal.emit()


class LPHomeShareTreeItem(QStandardItem):
    
    def __init__(self = None, directoryObj = None, text = None):
        super().__init__()
        self.directory = directoryObj
        if len(text) > 0:
            self.setText(text)
        else:
            self.setText(self.directory.title)
        self.artist = None
        self.album = None
        self.genre = None
        self.duration = None

    __classcell__ = None


class LPHomeShareViewController(QWidget):
    updateUISignal = pyqtSignal()
    searchUISignal = pyqtSignal()
    
    def __init__(self = None, serverListGetMethod = None):
        super(LPHomeShareViewController, self).__init__()
        self.serverListGetMethod = serverListGetMethod
        self.lastSearchWord = ''
        self.searching = False
        self.showState = 'common'
        self.commonExpanedCacheArray = []

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.searchField.returnPressed.connect(self.searchFieldEnter)
        self.searchField.textChanged.connect(self.searchFieldChanged)
        self.searchFieldClearAction = QAction('clear', self)
        self.searchFieldClearAction.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('search_close.png')))
        self.searchField.addAction(self.searchFieldClearAction, QLineEdit.ActionPosition.TrailingPosition)
        None((lambda : self.searchField.clear()))
        self.searchFieldClearAction.setVisible(False)
        self.musicTreeView.setModel(commonModel)
        self.musicTreeView.doubleClicked.connect(self.treeViewDoubleClick)
        self.musicTreeView.clicked.connect(self.treeViewSingleClick)
        self.musicTreeView.expanded.connect(self.onExpanded)
        self.musicTreeView.header().setStretchLastSection(True)
        self.musicTreeView.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.musicTreeView.header().setMinimumSectionSize(200)
        self.musicTreeView.setColumnWidth(0, 400)
        self.musicTreeView.setColumnWidth(1, 200)
        self.musicTreeView.setColumnWidth(2, 200)
        self.musicTreeView.expanded.connect(self.onExpanded)
        self.musicTreeView.setStyleSheet('\n                QTreeView::item {color: white; selection-color: white;}\nQTreeView::item:selected{\nselection-color: white;\nbackground-color: %s;\n}\nQTreeView::item:hover{background: %s; color: white}\nQTreeView{selection-background-color: transparent; border: none;}\nQHeaderView::section {\nbackground-color: transparent;\ncolor: white;\n}\nQTreeView::item{\n    height:30px;\n}\n\nQScrollBar {\n        border: 0px;\n        background-color: %s;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle {\n        background: rgb(82,82,82);\n        min-height: 30px;\n\tborder-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: none;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: none;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        background: %s;\n}\n        QTreeView::branch:has-children:!has-siblings:closed,\nQTreeView::branch:closed:has-children:has-siblings {\n        border-image: none;\n        image: url("%s");\n}\n\nQTreeView::branch:open:has-children:!has-siblings,\nQTreeView::branch:open:has-children:has-siblings  {\n        border-image: none;\n        image: url("%s");\n}' % (LPGlobalUI.THEME_BACKGROUND_COLOR.name(), LPGlobalUI.THEME_ITEM_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_BACKGROUND_COLOR.name(), LPGlobalUI.imagePath('treeclose.png'), LPGlobalUI.imagePath('treeexpand.png')))
        self.updateUISignal.connect(self.refreshPage)
        self.searchUISignal.connect(self.refreshAfterSearch)
        self.homeShareSearchLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        movie = QtGui.QMovie(LPGlobalUI.imagePath('lib/search-homeshare.gif'))
        self.homeShareSearchLabel.setMovie(movie)
        movie.start()
        stylesheetTemplate = Template('\n                QLabel#label {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n                LPLineEdit {\n                    background-color: rgb(31, 31, 31); \n                    color: white; \n                    padding: 5px; \n                    border-radius: 5px; \n                    qproperty-placeholderColor: rgba(255, 255, 255, 89);\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))

    
    def refreshPage(self):
        serverList = self.serverListGetMethod()
        if len(serverList) == 0:
            self.stackedWidget.setCurrentIndex(0)
            self.searchField.hide()
        else:
            self.stackedWidget.setCurrentIndex(1)
            self.searchField.show()

    
    def viewWillAppear(self):
        if self not in homeShareViewControllersArray:
            homeShareViewControllersArray.append(self)
        self.updateUISignal.emit()

    
    def viewWillDisappear(self):
        if self in homeShareViewControllersArray:
            homeShareViewControllersArray.remove(self)

    
    def changeEvent(self = None, event = None):
        if event.type() == QEvent.Type.LanguageChange:
            pass
        return super(LPHomeShareViewController, self).changeEvent(event)

    
    def refreshAfterSearch(self):
        for row in range(searchModel.rowCount()):
            self.musicTreeView.expand(searchModel.index(row, 0))

    
    def treeViewSingleClick(self, index):
        logger.debug('treeViewSingleClick')
        if index.row() == -1 or index.column() == -1:
            return None
        selectTreeItem = None.musicTreeView.model().nodeFromIndex(index)
        musicTreeItem = self.musicTreeView.model().nodeFromIndex(index.siblingAtColumn(0))
        contentDirectoryObj = musicTreeItem.directory
        if contentDirectoryObj.isFetching:
            return None
        if None.isContainer:
            self.musicTreeView.setExpanded(index.siblingAtColumn(0), not self.musicTreeView.isExpanded(index.siblingAtColumn(0)))

    
    def onExpanded(self = None, index = None):
        node = index.internalPointer()
        if node.totalChildren == 0 or node.requestOffset == 0 or node.requestOffset < node.totalChildren:
            cb = partial(self.browseCallback, index, node)
            commonModel.browse(index, cb)

    
    def browseCallback(self, index, node, response, subItems):
        if response.get('error', None) is not None:
            node.loading = False
            LPGlobalUI.toast.showToast(QCoreApplication.translate('HomeShare', 'Resource request failed: %s') % response.get('error'), self)
            return None
        if None(subItems) == 0:
            node.loading = False
            LPGlobalUI.toast.showToast(QCoreApplication.translate('HomeShare', 'This content is empty'), self)
            return None
        node.totalChildren = None(response.get('total', '0'))
        node.requestOffset += int(response.get('returned', '0'))
        if not node.directory.title:
            pass
        logger.debug(f'''[browseCallback] node:{node.displayText} total:{response.get('total', '0')} returned:{response.get('returned', '0')} loaded:{node.loadedChildren}''')
        commonModel.insertSignal.emit(index, node, subItems)

    
    def searchFieldChanged(self, text):
        self.searchFieldClearAction.setVisible(len(text) > 0)
        if len(text) == 0:
            self.showState = 'common'
            self.lastSearchWord = ''
            self.musicTreeView.setModel(commonModel)
            self.restoreCommonState()
            self.updateUISignal.emit()

    
    def searchFieldEnter(self):
        
        def _responseHandler(serverObj = None, result = None):
            if not serverObj.friendlyName:
                return None
            item = None(serverObj.directory, str(serverObj.friendlyName), rootNode, **('displayText', 'parent'))
            searchModel.appendRootNode(item)
            itemIndex = searchModel.indexFromNode(item)
            searchModel.appendChildren(itemIndex, item, serverObj.searchDirectory.subItems)
            for categoryItem in item.children:
                categoryItemIndex = searchModel.indexFromNode(categoryItem)
                searchModel.appendChildren(categoryItemIndex, categoryItem, categoryItem.directory.subItems)
            self.searching = False
            self.searchUISignal.emit()

        serverList = self.serverListGetMethod()
        if len(serverList) == 0:
            return None
        if None(self.searchField.text()) == 0:
            return None
        if None.lastSearchWord == self.searchField.text():
            return None
        if None.searching:
            return None
        None.saveCommonState()
        self.searching = True
        self.lastSearchWord = self.searchField.text()
        self.showState = 'search'
        rootNode = searchModel.invisibleRootItem()
        self.musicTreeView.setModel(searchModel)
        searchModel.resetModel()
        for server in serverList:
            server.search(self.searchField.text(), _responseHandler)

    
    def treeViewDoubleClick(self, index):
        if index.row() == -1 or index.column() == -1:
            return None
        selectTreeItem = None.musicTreeView.model().nodeFromIndex(index)
        musicTreeItem = self.musicTreeView.model().nodeFromIndex(index.siblingAtColumn(0))
        contentDirectoryObj = musicTreeItem.directory
        if contentDirectoryObj.isFetching:
            return None
        if None.isContainer:
            self.musicTreeView.setExpanded(index.siblingAtColumn(0), not self.musicTreeView.isExpanded(index.siblingAtColumn(0)))
        elif contentDirectoryObj.isAudio:
            device = LPGlobalUI.currentDevice
            if not device:
                logger.error('error, no device found')
                return None
            None.info('HomeShare userclick: %s, %s' % (contentDirectoryObj.title, contentDirectoryObj.parentContentDirectory.title))
            subItems = contentDirectoryObj.parentContentDirectory.subItems
            playList = self.makePlayList(contentDirectoryObj, subItems)
            
            def playFinishMethod(result = None):
                logger.debug('%s play result: %s' % (contentDirectoryObj.title, result))
                if result is False:
                    LPGlobalUI.toast.showToast(QCoreApplication.translate('HomeShare', '"%s" play failed') % contentDirectoryObj.title, self)

            device.fastPlay(playList, playFinishMethod)

    
    def saveCommonState(self):
