# Source Generated with Decompyle++
# File: LPPlayViewMouseMonitor.pyc (Python 3.9)

'''
@Time ： 2025/11/5 9:47
@Auth ： Chris
@File ：LPPlayViewMouseMonitor.py
@Desc: application level filter for play view
'''
from PyQt6.QtCore import QObject, QEvent
import LPGlobalUI
PLAY_VIEW_ACTIVITY_EVENT_TYPES = frozenset((QEvent.Type.MouseMove, QEvent.Type.Wheel, QEvent.Type.HoverMove, QEvent.Type.MouseButtonPress))

class LPPlayViewMouseMonitor(QObject):
    '''在应用级别监听全屏播放页的用户活动。'''
    
    def __init__(self = None):
        '''保存主窗口和播放页控制器引用。'''
        super().__init__()
        self.mianUI = LPGlobalUI.mainWindow
        self.playView = self.mianUI.playViewController

    
    def eventFilter(self, obj, event):
        '''将全屏播放页活动事件转发给播放页控制器。

        参数:
            obj: 当前事件的目标对象。
            event: QApplication 分发的事件。
        返回值:
            False，继续交由原目标对象处理事件。
        '''
        if event.type() not in PLAY_VIEW_ACTIVITY_EVENT_TYPES:
            return False
        if not None.playView or self.mianUI.isPlayViewShow:
            return False
        if not None.mianUI.isFullScreen():
            return False
        None.playView.handleMouseMove(event)
        return False

    __classcell__ = None

