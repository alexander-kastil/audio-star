# Source Generated with Decompyle++
# File: LPContextMenuManager.pyc (Python 3.9)

'''
@Time ： 2024/12/3 18:29
@Auth ： Chris
@File ：LPContextMenuManager.py
@Desc:
'''
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QAction, QIcon
import LPGlobalUI
from LPClientFramework.LPMenu.LPActionCallbackManager import ActionCallbackManager
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPBaseMenu import BaseMenu

class ContextMenuManager(QObject):
    move_delete_lock_signal = pyqtSignal()
    
    def __init__(self = None, parent = None, callback_manager = None):
        super().__init__(parent)
        self.parent = parent
        self.menu = BaseMenu(parent)
        self.actions_group = None
        self.actions = []
        self.callback_manager = callback_manager

    
    def init(self, actions_group, *args, **kwargs):
        pass
    # WARNING: Decompyle incomplete

    
    def add_action(self, action_name, icon_path, callback_name, *args, **kwargs):
        '''添加菜单项，并将回调函数与菜单项绑定'''
        action = QAction(QIcon(LPGlobalUI.imagePath(icon_path)), action_name)
        None((lambda : pass# WARNING: Decompyle incomplete
))
        self.menu.add_action(action)
        self.actions.append(action)

    
    def add_separator(self):
        '''添加分隔符'''
        self.menu.addSeparator()

    
    def show_menu(self, pos):
        '''显示菜单'''
        self.menu.exec_(pos)

    
    def clear_actions(self):
        '''清空所有菜单项'''
        for action in self.actions:
            self.menu.remove_action(action)
        self.actions.clear()

    __classcell__ = None

