# Source Generated with Decompyle++
# File: LPTidalShellRouter.pyc (Python 3.9)

'''
TIDAL Shell 内部路由工具。
'''
from typing import List, Optional, TypeVar
from PyQt6.QtWidgets import QWidget
RouteEntry = TypeVar('RouteEntry')
TIDAL_SHELL_EMBEDDED_ITEM_IDS = {
    'tidal_home',
    'tidal_collection'}
TIDAL_SHELL_NO_HOME_TABS_ITEM_IDS = {
    'tidal_search'}

class LPTidalShellRouteStack:
    '''TIDAL Shell 内部页面栈，负责维护内容页顺序和返回目标。'''
    
    def __init__(self):
        '''
        初始化空路由栈。

        :return: None。
        '''
        self._entries = []

    
    def resetRoot(self = None, entry = None):
        '''
        重置根页面并返回被移除的旧页面。

        :param entry: 新根页面。
        :return: 被移除的旧页面列表。
        '''
        removed = list(self._entries)
        self._entries = [
            entry]
        return removed

    
    def replaceRoot(self = None, entry = None):
        '''
        替换根页面并移除所有后续页面。

        :param entry: 新根页面。
        :return: 被移除的非根页面列表。
        '''
        removed = list(self._entries[1:])
        self._entries = [
            entry]
        return removed

    
    def push(self = None, entry = None):
        '''
        推入新页面。

        :param entry: 新页面。
        :return: 被裁剪的前进页面列表。
        '''
        self._entries.append(entry)
        return []

    
    def pop(self = None):
        '''
        弹出当前页面，根页面不可弹出。

        :return: 被弹出的页面；无可弹页面时返回 None。
        '''
        if len(self._entries) <= 1:
            return None
        return None._entries.pop()

    
    def current(self = None):
        '''
        返回当前页面。

        :return: 当前页面；空栈返回 None。
        '''
        if self._entries:
            return self._entries[-1]

    
    def entries(self = None):
        '''
        返回页面栈快照。

        :return: 页面列表副本。
        '''
        return list(self._entries)



def findTidalShell(widget = None):
    '''
    从当前页面向上查找 TIDAL Shell 容器。

    :param widget: 当前页面。
    :return: Shell 容器；未找到返回 None。
    '''
    current = widget
    if current is not None:
        if hasattr(current, 'pushContentPage') and hasattr(current, 'popContentPage'):
            return current
        parent = None.parent()
        current = parent if isinstance(parent, QWidget) else None
        continue


def pushTidalPage(parent = None, widget = None, itemId = None):
    '''
    在 Shell 内部或全局导航中推入 TIDAL 页面。

    :param parent: 触发跳转的页面。
    :param widget: 目标页面。
    :param itemId: 页面标识。
    :return: None。
    '''
    shell = findTidalShell(parent)
    if shell is not None and shouldOpenTidalPageInShell(itemId):
        shell.pushContentPage(widget, itemId)
        return None
    import LPGlobalUI
    if shouldOpenTidalPageInShell(itemId):
        shell = createTidalShellWithContentPage(widget, itemId)
        LPGlobalUI.navigationManager.push(shell, 'Tidal')
        return None
    widget.openedAsTidalIndependentPage = None
    LPGlobalUI.navigationManager.push(widget, itemId)


def shouldOpenTidalPageInShell(itemId = None):
    '''
    判断页面是否应作为 TIDAL Shell 内容页内嵌展示。

    :param itemId: 页面标识。
    :return: 应放入 Shell 内容区返回 True。
    '''
    if not itemId:
        pass
    normalized_id = str('').strip().lower()
    return normalized_id in TIDAL_SHELL_EMBEDDED_ITEM_IDS


def createTidalShellWithContentPage(widget = None, itemId = None):
    '''
    创建 TIDAL Shell 并把目标页面推入 Shell 内容栈。

    :param widget: 目标内容页。
    :param itemId: 页面标识。
    :return: 已包含目标页面的 Shell。
    '''
    LPTidalShellViewController = LPTidalShellViewController
    import HOME.StreamService.Tidal.controllers.shell.LPTidalShellViewController
    shell = LPTidalShellViewController()
    shell.pushContentPage(widget, itemId)
    return shell


def isTidalShellHomeTabsVisible(entries = None):
    '''
    判断 Shell 顶部导航是否需要显示 Home/My Collection 页签。

    :param entries: Shell 内部页面栈快照。
    :return: 需要显示 Home/My Collection 页签返回 True。
    '''
    if not entries:
        return True
    current = None[-1]
    if not getattr(current, 'stackedItemId', current):
        pass
    item_id = str('')
    return item_id not in TIDAL_SHELL_NO_HOME_TABS_ITEM_IDS


def isCurrentTidalDetailPage(itemType = None, itemId = None):
    '''
    判断当前顶层页面是否已经是指定类型 + ID 的 TIDAL 详情页。
    主要用于 Album/Artist 详情页重复跳转防护（已在详情页内再次点击同一条目时跳过 push）。

    支持两种情况：
    - 全局导航栈顶（详情页通常以独立页面形式存在）
    - Shell 容器作为顶层时，检查其内部 _route_stack 当前内容页

    :param itemType: 详情类型（"album" / "artist" 等，内部会 lower）
    :param itemId: 业务 ID（专辑ID 或 艺人ID）
    :return: 如果当前正在查看的就是该详情页，返回 True（应跳过重复 push）
    '''
    if not itemType:
        pass
    normalized_type = str('').strip().lower()
    if not itemId:
        pass
    normalized_id = str('').strip()
    if not normalized_type or normalized_id:
        return False
    import LPGlobalUI
# WARNING: Decompyle incomplete


def _isDetailWidgetMatch(widget = None, item_type = None, item_id = None):
    '''
    内部辅助：判断一个 widget 是否为匹配的 TIDAL 详情页（基于 _item_type / _item_id）。
    使用 hasattr 避免强依赖具体子类。
    '''
    if widget is None:
        return False
    if not getattr(widget, '_item_type', ''):
        pass
    w_type = None('').strip().lower()
    if not getattr(widget, '_item_id', ''):
        pass
    w_id = str('').strip()
    if w_type == item_type:
        pass
    return w_id == item_id

