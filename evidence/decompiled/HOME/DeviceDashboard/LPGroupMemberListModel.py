# Source Generated with Decompyle++
# File: LPGroupMemberListModel.pyc (Python 3.9)

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, pyqtProperty, pyqtSignal

class LPGroupMemberListModel(QAbstractListModel):
    '''设备组成员列表模型，负责向 QML 暴露稳定的成员行数据。'''
    UuidRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    VolumeRole = Qt.ItemDataRole.UserRole + 3
    MuteRole = Qt.ItemDataRole.UserRole + 4
    FixedVolumeRole = Qt.ItemDataRole.UserRole + 5
    IsMasterRole = Qt.ItemDataRole.UserRole + 6
    PlayStateRole = Qt.ItemDataRole.UserRole + 7
    VolumeLockedRole = Qt.ItemDataRole.UserRole + 8
    countChanged = pyqtSignal()
    _ROLE_KEYS = {
        VolumeLockedRole: 'volumeLocked',
        PlayStateRole: 'playState',
        IsMasterRole: 'isMaster',
        FixedVolumeRole: 'fixedVolume',
        MuteRole: 'mute',
        VolumeRole: 'volume',
        NameRole: 'name',
        UuidRole: 'uuid' }
    
    def __init__(self = None, rows = None, parent = None):
        '''初始化设备组成员模型。

        参数:
            rows: 初始成员行列表。
            parent: Qt 父对象。
        返回:
            None。
        '''
        super().__init__(parent)
        if not rows:
            pass
        self._rows = (lambda .0 = None: [ self._normalizeRow(row) for row in .0 ])(list([]))

    
    def count(self):
        '''返回当前成员行数量。

        参数:
            无。
        返回:
            int: 当前模型行数。
        '''
        return len(self._rows)

    count = pyqtProperty(int, countChanged, **('notify',))(count)
    
    def rowCount(self, parent = (QModelIndex(),)):
        '''返回模型行数。

        参数:
            parent: Qt 模型父索引，本模型不使用层级结构。
        返回:
            int: 当前模型行数。
        '''
        if parent.isValid():
            return 0
        return None(self._rows)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        '''按 role 返回指定成员行字段。

        参数:
            index: Qt 模型索引。
            role: QML 请求的字段 role。
        返回:
            object: 对应字段值；索引或 role 无效时返回 None。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._rows):
            return None
        key = None._ROLE_KEYS.get(role)
        if key is None:
            return None
        return None._rows[row].get(key)

    
    def roleNames(self):
        '''返回 QML 可访问的 role 名称。

        参数:
            无。
        返回:
            dict: role id 到 QByteArray 名称的映射。
        '''
        return {
            self.VolumeLockedRole: b'volumeLocked',
            self.PlayStateRole: b'playState',
            self.IsMasterRole: b'isMaster',
            self.FixedVolumeRole: b'fixedVolume',
            self.MuteRole: b'mute',
            self.VolumeRole: b'volume',
            self.NameRole: b'name',
            self.UuidRole: b'uuid' }

    
    def rows(self):
        '''返回成员行快照，便于测试和兼容旧逻辑。

        参数:
            无。
        返回:
            list: 成员行字典副本列表。
        '''
        return (lambda .0: [ dict(row) for row in .0 ])(self._rows)

    
    def setRows(self, rows):
