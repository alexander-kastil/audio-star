# Source Generated with Decompyle++
# File: LPCustomMenu.pyc (Python 3.9)

'''
@Time ： 2025/10/10 15:00
@Auth ： Chris
@File ：LPCustomMenu.py
@Desc:
'''
from typing import Tuple
from PyQt6.QtCore import QSize, Qt, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame

class LPMenuItem(QObject):
    '''定义菜单项的数据结构'''
    clicked = pyqtSignal()
    
    def __init__(self = None, text = None, icon = None, itemType = None, callback = None, extra = None):
        super().__init__()
        self.text = text
        self.icon = icon
        self.type = itemType
        self.callback = callback
        if not extra:
            pass
        self.extra = { }

    __classcell__ = None


class LPBaseMenuItemWidget(QWidget):
    
    def __init__(self = None, item = None):
        super().__init__()
        self.item = item

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)

    __classcell__ = None


class LPIconTextMenuItemWidget(LPBaseMenuItemWidget):
    
    def __init__(self = None, item = None):
        super().__init__(item)

    
    def setupUi(self = None, ui = None):
        '''子类必须实现，定义自己的布局与内容'''
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        scalePixmap = QPixmap(self.item.icon).scaled(self.iconLabel.width(), self.iconLabel.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.iconLabel.setPixmap(scalePixmap)
        self.textLabel.setText(self.item.text)

    __classcell__ = None

