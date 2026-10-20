# Source Generated with Decompyle++
# File: LPDeviceListModel.pyc (Python 3.9)

from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex, pyqtSignal, pyqtSlot, pyqtProperty

class LPDeviceListModel(QAbstractListModel):
    ItemTypeRole = Qt.ItemDataRole.UserRole + 1
    DeviceObjRole = Qt.ItemDataRole.UserRole + 98
    DeviceWrapperRole = Qt.ItemDataRole.UserRole + 99
    countChanged = pyqtSignal()
    
    def __init__(self = None, deviceWrapperList = None, parent = None):
        super().__init__(parent)
        if not deviceWrapperList:
            pass
        self.deviceWrapperList = []

    
    def count(self):
        return len(self.deviceWrapperList)

    count = pyqtProperty(int, countChanged, **('notify',))(count)
    
    def rowCount(self, parent = (QModelIndex(),)):
        return len(self.deviceWrapperList)

    
    def data(self = None, index = None, role = None):
        if not index.isValid():
            return None
        deviceWrapper = None.deviceWrapperList[index.row()]
        if role == self.ItemTypeRole:
            return getattr(deviceWrapper, 'itemType', 'device')
        if None == self.DeviceWrapperRole:
            return deviceWrapper
        if None == self.DeviceObjRole:
            return deviceWrapper.device

    
    def roleNames(self):
        return {
            self.DeviceWrapperRole: b'deviceWrapper',
            self.DeviceObjRole: b'device',
            self.ItemTypeRole: b'itemType' }

    
    def _wrapperKey(wrapper):
        key = getattr(wrapper, 'selectionKey', None)
        if key:
            return str(key)
        return f'''{id(wrapper)}'''

    _wrapperKey = staticmethod(_wrapperKey)
    
    def _findRowByKey(self, key):
        for row, wrapper in enumerate(self.deviceWrapperList):
            if self._wrapperKey(wrapper) == key:
                return row
            return -1

    
    def containsKey(self, key):
        return self._findRowByKey(key) >= 0

    
    def insertItem(self, wrapper, row = (None,)):
        if wrapper is None:
            return False
        key = None._wrapperKey(wrapper)
        if self.containsKey(key):
            return False
        if None is None:
            row = len(self.deviceWrapperList)
        row = max(0, min(int(row), len(self.deviceWrapperList)))
        self.beginInsertRows(QModelIndex(), row, row)
        self.deviceWrapperList.insert(row, wrapper)
        self.endInsertRows()
        self.countChanged.emit()
        return True

    
    def insertItemSortedByName(self, wrapper):
        if wrapper is None:
            return False
        if not None(wrapper, 'deviceName', ''):
            pass
        target_name = ''.lower()
        row = 0
        if row < len(self.deviceWrapperList):
            if not getattr(self.deviceWrapperList[row], 'deviceName', ''):
                pass
            row_name = ''.lower()
            if target_name < row_name:
                pass
            else:
                row += 1
        return self.insertItem(wrapper, row, **('row',))

    
    def removeByKey(self, key):
        row = self._findRowByKey(key)
        if row < 0:
            return False
        None.beginRemoveRows(QModelIndex(), row, row)
        self.deviceWrapperList.pop(row)
        self.endRemoveRows()
        self.countChanged.emit()
        return True

    
    def upsertItem(self, wrapper):
        if wrapper is None:
            return False
        key = None._wrapperKey(wrapper)
        row = self._findRowByKey(key)
        if row >= 0:
            if self.deviceWrapperList[row] is not wrapper:
                self.deviceWrapperList[row] = wrapper
            idx = self.index(row, 0)
            self.dataChanged.emit(idx, idx, [
                self.ItemTypeRole,
                self.DeviceObjRole,
                self.DeviceWrapperRole])
            return False
        return None.insertItem(wrapper)

    
    def setItems(self, wrapperList):
        if not wrapperList:
            pass
        new_list = list([])
        old_list = self.deviceWrapperList
        old_keys = (lambda .0 = None: [ self._wrapperKey(item) for item in .0 ])(old_list)
        new_keys = (lambda .0 = None: [ self._wrapperKey(item) for item in .0 ])(new_list)
        if old_keys == new_keys:
            return None
        if None(set(old_keys)) != len(old_keys) or len(set(new_keys)) != len(new_keys):
            self.beginResetModel()
            self.deviceWrapperList = new_list
            self.endResetModel()
            self.countChanged.emit()
            return None
        old_count = None(old_list)
        new_key_set = set(new_keys)
        for row in range(len(old_list) - 1, -1, -1):
            if old_keys[row] in new_key_set:
                continue
            self.beginRemoveRows(QModelIndex(), row, row)
            old_list.pop(row)
            old_keys.pop(row)
            self.endRemoveRows()
        row = 0
    # WARNING: Decompyle incomplete

    
    def clear(self):
