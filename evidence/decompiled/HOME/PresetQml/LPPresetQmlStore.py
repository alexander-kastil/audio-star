# Source Generated with Decompyle++
# File: LPPresetQmlStore.pyc (Python 3.9)

'''
Preset（预设快捷键）QML 版数据层。

职责：
- LPPresetListModel：QAbstractListModel，给 QML GridView 提供卡片数据。
- LPPresetQmlStore：封装“解析设备 GetKeyMapping XML -> 构建模型条目 ->
  异步下载封面落盘缓存 -> 回写 coverUrl”的完整流程，并维护页面状态机。

与旧的 HOME/LPPresetViewController.py 完全解耦，仅复用 LPClientFramework 层的工具方法。
'''
import threading
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, pyqtSignal
import LPGlobalUI
from LPClientFramework import LPStreamServiceManager, LPUtility
from LPClientFramework.LPDeviceStreamServiceManager import DEVICE_ACCOUNT_UNKNOWN
from LPClientFramework.LPPublicDefine import SOURCES_NO_LOGIN
from LPClientFramework.LPUtility import logger
_PRESET_NO_LOGIN_SOURCES = SOURCES_NO_LOGIN

def presetSourceNeedsDeviceAccount(source = None):
    '''
    判断某 preset 源是否需要依赖设备账号状态才能判定可播放。

    无需登录的源与 Pandora 失效源（强制不可播）无需拉取账号。

    :param source: KeyMapping 中的 Source 标识。
    :return: 需要设备账号状态返回 True。
    '''
    if not source:
        return False
    if None == 'Pandora' and 'Pandora2' in LPStreamServiceManager.supportContents():
        return False
    return None not in _PRESET_NO_LOGIN_SOURCES


def presetSourceCanPlay(source = None, device = None):
    '''
    判断某 preset 源在当前设备上是否可直接播放（对齐 iOS preset 页规则）。

    iOS 规则：源账号已登录（或该源无需登录）才可播放；Pandora 旧 preset
    在支持列表存在 Pandora2 时视为失效，强制不可播放。

    :param source: KeyMapping 中的 Source 标识。
    :param device: 当前设备对象，用于读取该源的登录账号缓存。
    :return: 可播放返回 True，否则返回 False。
    '''
    if not source:
        return False
    if None == 'Pandora' and 'Pandora2' in LPStreamServiceManager.supportContents():
        return False
    if None in _PRESET_NO_LOGIN_SOURCES:
        return True
    account_manager = None(device, 'deviceStreamServiceManager', None)
    if account_manager is None:
        return False
    account = None.deviceAccountForSource(source)
    if account is DEVICE_ACCOUNT_UNKNOWN:
        return True
    return None is not None


def _sourceIconQrc(source = None):
    '''
    根据来源解析为 preset 卡片来源图标的 qrc 路径。

    直接取 supportContents()[source]["preset_icon"]，该字段已是完整 qrc 路径，
    无需再做扩展名推断；字段为空时返回空字符串（卡片不显示来源图标）。

    :param source: 设备返回的来源标识（如 Qobuz / Tidal / newTuneIn / AIRPLAY）。
    :return: qrc 图标路径字符串；未命中或无对应图标时返回空字符串。
    '''
    if not source:
        return ''
    supportContents = None.supportContents()
    infoDict = supportContents.get(source)
    if not infoDict:
        return ''
    if not infoDict.get('preset_icon', ''):
        pass
    iconPath = None('').strip()
    if not iconPath:
        return ''
    if None.startswith(':/'):
        return 'qrc' + iconPath


class LPPresetListModel(QAbstractListModel):
    '''
    Preset 卡片网格数据模型。

    对外暴露的 role（QML 中以 role 名直接访问）：
        index         -> int    预设序号（1 起）
        displayName   -> str    处理后的展示名称（去掉 “_#~” 后缀）
        sourceIcon    -> str    来源图标 qrc 路径，空字符串表示无图标
        coverUrl      -> str    封面本地 file URL 或 qrc URL；为空表示未就绪
        isEmpty       -> bool   是否为空槽位
    '''
    IndexRole = Qt.ItemDataRole.UserRole + 1
    DisplayNameRole = Qt.ItemDataRole.UserRole + 2
    SourceIconRole = Qt.ItemDataRole.UserRole + 3
    CoverUrlRole = Qt.ItemDataRole.UserRole + 4
    IsEmptyRole = Qt.ItemDataRole.UserRole + 5
    CanPlayRole = Qt.ItemDataRole.UserRole + 6
    countChanged = pyqtSignal()
    coverUrlReady = pyqtSignal(int, str)
    
    def __init__(self = None, parent = None):
        '''
        初始化空模型，并把封面就绪信号连接到回写槽。

        :param parent: 父级 QObject。
        '''
        super().__init__(parent)
        self._items = []
        self.coverUrlReady.connect(self.updateCoverUrl)

    
    def items(self = None):
        '''
        返回内部条目列表（控制器可读，便于删除等操作）。

        :return: 条目字典列表的引用。
        '''
        return self._items

    items = None(items)
    
    def rowCount(self = None, parent = None):
        '''
        返回模型行数。

        :param parent: 父索引（列表模型恒为无效索引）。
        :return: 当条条目数量。
        '''
        if parent.isValid():
            return 0
        return None(self._items)

    
    def roleNames(self = None):
        '''
        返回 role 名映射，供 QML delegate 通过 model.<role> 访问。

        :return: role 枚举到 role 名的字节串字典。
        '''
        return {
            self.CanPlayRole: b'canPlay',
            self.IsEmptyRole: b'isEmpty',
            self.CoverUrlRole: b'coverUrl',
            self.SourceIconRole: b'sourceIcon',
            self.DisplayNameRole: b'displayName',
            self.IndexRole: b'index' }

    
    def data(self = None, index = None, role = None):
        '''
        返回指定索引、指定 role 的数据。

        :param index: 模型索引。
        :param role: 数据 role。
        :return: 对应数据；越界或不匹配时返回 None。
        '''
        if not index.isValid():
            return None
        row = None.row()
        if row < 0 or row >= len(self._items):
            return None
        item = None._items[row]
        if role == self.IndexRole:
            return item.get('index', 0)
        if None == self.DisplayNameRole:
            return item.get('displayName', '')
        if None == self.SourceIconRole:
            return item.get('sourceIcon', '')
        if None == self.CoverUrlRole:
            return item.get('coverUrl', '')
        if None == self.IsEmptyRole:
            return item.get('isEmpty', True)
        if None == self.CanPlayRole:
            return item.get('canPlay', False)

    
    def setItems(self = None, items = None):
        '''
        整体替换模型数据并通知视图。

        :param items: 新条目字典列表。
        :return: None。
        '''
        self.beginResetModel()
        if not items:
            pass
        self._items = list([])
        self.endResetModel()
        self.countChanged.emit()

    
    def updateCoverUrl(self = None, index = None, coverUrl = None):
        '''
        单条更新某预设的封面 URL（异步下载完成后回写）。

        :param index: 预设序号（1 起）。
        :param coverUrl: 已落盘的本地 file URL。
        :return: None。
        '''
        for row, item in enumerate(self._items):
            if item.get('index') == index or item.get('coverUrl') != coverUrl:
                item['coverUrl'] = coverUrl
                idx = self.index(row)
                self.dataChanged.emit(idx, idx, [
                    self.CoverUrlRole])
            return None

    
    def updateCanPlay(self = None, index = None, canPlay = None):
        '''
        单条更新某预设的可播放状态（账号登录状态变化后刷新）。

        :param index: 预设序号（1 起）。
        :param canPlay: 是否可播放。
        :return: None。
        '''
        for row, item in enumerate(self._items):
            if item.get('index') == index or item.get('canPlay') != canPlay:
                item['canPlay'] = canPlay
                idx = self.index(row)
                self.dataChanged.emit(idx, idx, [
                    self.CanP