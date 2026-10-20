# Source Generated with Decompyle++
# File: LPPagedTreeModel.pyc (Python 3.9)

'''
@Time ： 2026/1/4 15:31
@Auth ： Chris
@File ：LPPagedTreeModel.py
@Desc:
'''
from functools import partial
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QCoreApplication, pyqtSignal, QTimer
from LPClientFramework.CacheLog import logger
Model_Column = 3

class LPHomeShareTreeNode:
    
    def __init__(self, directoryObj, displayText, parent = (None, '', None)):
        self.directory = directoryObj
        self.displayText = displayText
        self.parent = parent
        self.offset = 0
        self.requestOffset = 0
        self.pageSize = 500
        self.loadedChildren = 0
        self.totalChildren = 0
        self.loading = False
        self.threshold = 50
        self.lastViewedRow = 0
        self.artist = directoryObj.artist if directoryObj else None
        self.album = directoryObj.album if directoryObj else None
        self.genre = None
        self.duration = None
        self.children = []

    
    def reset(self):
        self.children.clear()
        self.offset = 0
        self.requestOffset = 0
        self.loadedChildren = 0
        self.totalChildren = 0
        self.loading = False
        self.lastViewedRow = 0

    
    def childCount(self):
        '''
        返回已加载的子节点数量
        '''
        return len(self.children)

    
    def row(self):
        '''
        返回自己在父节点 children 中的行号
        '''
        pass
    # WARNING: Decompyle incomplete



class LPPagedTreeModel(QAbstractItemModel):
    insertSignal = pyqtSignal(object, object, object)
    
    def __init__(self = None):
        super().__init__()
        self._rootNode = LPHomeShareTreeNode()
        self.insertSignal.connect(self.appendChildren)
        self.a = 0

    
    def columnCount(self, parent = (QModelIndex(),)):
        return Model_Column

    
    def rowCount(self, parent = (QModelIndex(),)):
        node = self._rootNode if not parent.isValid() else parent.internalPointer()
        logger.debug(f'''node.loadedChildren: {node.loadedChildren}''')
        return len(node.children)

    
    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return None._rootNode

    
    def indexFromNode(self, node, column = (0,)):
        if node is None or node.parent is None:
            return QModelIndex()
        parentNode = None.parent
        row = parentNode.children.index(node)
        return self.createIndex(row, column, node)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
