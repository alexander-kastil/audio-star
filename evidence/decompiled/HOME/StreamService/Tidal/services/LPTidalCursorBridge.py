# Source Generated with Decompyle++
# File: LPTidalCursorBridge.pyc (Python 3.9)

'''TIDAL QQuickWidget 宿主光标同步桥。'''
from typing import Dict, Optional, Tuple
from PyQt6.QtCore import QObject, Qt, pyqtSlot

class LPTidalCursorBridge(QObject):
    '''TIDAL 宿主光标同步桥，负责把 QML hover 状态同步到 QQuickWidget 光标。'''
    
    def __init__(self = None, parent = None):
        '''
        初始化宿主光标同步桥。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._quick_widget = None
        self._hover_cursor_states = { }
        self._hover_cursor_state_seq = 0

    
    def setQuickWidget(self = None, quickWidget = None):
        '''
        绑定当前页面的 QQuickWidget 宿主。

        :param quickWidget: 当前页面承载 QML 的 QQuickWidget。
        :return: None。
        '''
        self._quick_widget = quickWidget

    
    def normalizeCursorShape(self = None, cursorName = None):
        '''
        将字符串光标名称归一化为 Qt 光标形态。

        :param cursorName: 光标名称。
        :return: Qt 光标形态。
        '''
        if not cursorName:
            pass
        cursor_name = str('').strip().lower()
        cursor_shape_map = {
            'arrow': Qt.CursorShape.ArrowCursor,
            'default': Qt.CursorShape.ArrowCursor,
            'pointinghand': Qt.CursorShape.PointingHandCursor,
            'pointing_hand': Qt.CursorShape.PointingHandCursor,
            'hand': Qt.CursorShape.PointingHandCursor,
            'ibeam': Qt.CursorShape.IBeamCursor,
            'i_beam': Qt.CursorShape.IBeamCursor,
            'text': Qt.CursorShape.IBeamCursor,
            'forbidden': Qt.CursorShape.ForbiddenCursor,
            'notallowed': Qt.CursorShape.ForbiddenCursor,
            'not_allowed': Qt.CursorShape.ForbiddenCursor,
            'disabled': Qt.CursorShape.ForbiddenCursor }
        return cursor_shape_map.get(cursor_name, Qt.CursorShape.ArrowCursor)

    
    def setHoverCursorState(self = None, sourceKey = None, hovered = pyqtSlot(str, bool, str), cursorName = {
        'sourceKey': str,
        'hovered': bool,
        'cursorName': str,
        'return': None }):
        '''
        按来源维护 hover 光标状态。

        :param sourceKey: hover 来源唯一键。
        :param hovered: True 表示来源进入 hover，False 表示来源离开 hover。
        :param cursorName: 光标名称，支持 arrow、pointinghand、ibeam、forbidden。
        :return: None。
        '''
        if not sourceKey:
            pass
        source_key = str('').strip()
        if not source_key:
            return None
        self._syncQuickCursorFromHoverStates()

    setHoverCursorState = None(setHoverCursorState)
    
    def setHoverCursorShape(self = None, cursorName = None):
        '''
        兼容单来源调用，设置或清理 legacy hover 光标。

        :param cursorName: 光标名称，空、arrow、default 表示清理。
        :return: None。
        '''
        if not cursorName:
            pass
        cursor_name = str('').strip().lower()
        self.setHoverCursorState('__legacy__', cursor_name not in ('', 'arrow', 'default'), cursor_name)

    setHoverCursorShape = None(setHoverCursorShape)
    
    def clearHoverCursorStates(self = None):
        '''
        清空当前页面全部 hover 光标来源并恢复箭头。

        :return: None。
        '''
        self._hover_cursor_states.clear()
        self._setQuickCursorShape(Qt.CursorShape.ArrowCursor)

    clearHoverCursorStates = None(clearHoverCursorStates)
    
    def _syncQuickCursorFromHoverStates(self = None):
        '''
        根据当前 active hover 来源同步宿主光标。

        :return: None。
        '''
        if not self._hover_cursor_states:
            self._setQuickCursorShape(Qt.CursorShape.ArrowCursor)
            return None
        cursor_shape = None(self._hover_cursor_states.values(), (lambda item: item[1]), **('key',))[0]
        self._setQuickCursorShape(cursor_shape)

    
    def _setQuickCursorShape(self = None, cursorShape = None):
        '''
        设置 QQuickWidget 宿主光标，避免重复设置相同光标。

        :param cursorShape: 目标 Qt 光标形态。
        :return: None。
        '''
        quick = self._quick_widget
        if quick is None:
            return None
        current_cursor = None.cursor()
        if current_cursor is not None and current_cursor.shape() == cursorShape:
            return None
        None.setCursor(cursorShape)

    __classcell__ = None

