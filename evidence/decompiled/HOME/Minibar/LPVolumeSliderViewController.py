# Source Generated with Decompyle++
# File: LPVolumeSliderViewController.pyc (Python 3.9)

'''
@Time ： 2025/9/28 15:42
@Auth ： Chris
@File ：LPVolumeSliderViewController.py
@Desc:
'''
from PyQt6.QtCore import Qt, QEvent, QRect
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QWidget, QDialog, QApplication

class LPVolumeSliderViewController(QWidget):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setStyleSheet('\n                    QFrame#mainFrame{\n                        border-radius: 8px;\n                        background: rgb(28, 28, 28);\n                    }\n                    QWidget {\n                        background: transparent;\n                    }\n        ')

    
    def updatePosition(self):
        parent = self.parent()
        parent_global_topLeft = parent.mapToGlobal(parent.rect().topLeft())
        slider_size = self.size()
        px = parent_global_topLeft.x() + (parent.width() - slider_size.width()) // 2
        py = parent_global_topLeft.y() - slider_size.height() - 5
        self.winId()
        self.move(px, py)

    
    def _maybeHide(self):
