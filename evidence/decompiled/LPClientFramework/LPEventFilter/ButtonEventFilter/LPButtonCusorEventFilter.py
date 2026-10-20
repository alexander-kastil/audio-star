# Source Generated with Decompyle++
# File: LPButtonCusorEventFilter.pyc (Python 3.9)

'''
@Time ： 2025/2/7 17:22
@Auth ： Chris
@File ：LPButtonCusorEventFilter.py
@Desc:
'''
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QPushButton
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPButtonCursorEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, button = None, image = None):
        super().__init__(button)
        button.setIcon(QIcon(image))

    
    def eventFilter(self = None, obj = None, event = None):
        if isinstance(obj, QPushButton):
            if not event.type() == event.Type.Enter and obj.isEnabled():
                QApplication.setOverrideCursor(Qt.CursorShape.ForbiddenCursor)
            elif event.type() == event.Type.Leave:
                QApplication.restoreOverrideCursor()
        return super().eventFilter(obj, event)

    __classcell__ = None

