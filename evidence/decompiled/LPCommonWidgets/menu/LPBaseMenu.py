# Source Generated with Decompyle++
# File: LPBaseMenu.pyc (Python 3.9)

'''
@Time ： 2024/11/21 18:58
@Auth ： Chris
@File ：LPBaseMenu.py
@Desc: 基础的圆角menu。自带QMenu有阴影和边框，设置圆角无效，需设置属性去掉阴影和边框才行。
'''
import sys
from PyQt6.QtCore import Qt, QSize, pyqtSlot, QPoint, QRect
from PyQt6.QtGui import QIcon, QColor, QPixmap
from PyQt6.QtWidgets import QMenu, QHBoxLayout, QGraphicsDropShadowEffect, QListWidgetItem, QApplication, QWidgetAction, QSizePolicy
import LPGlobalUI
from LPClientFramework.CacheLog import logger
from LPCommonWidgets.menu.LPBaseActionListWidget import BaseActionListWidget

class BaseMenu(QMenu):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.parent = parent
        self._actions = []
        self.item_height = 28
        self.h_BoxLayout = QHBoxLayout(self)
        self.view = BaseActionListWidget(self)
        self._init_widgets()

    
    def _init_widgets(self):
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet('\n            QMenu {\n                background-color: transparent;\n                border: none;\n            }\n        ')
        self.setMouseTracking(True)
        self.h_BoxLayout.addWidget(self.view, 1, Qt.AlignmentFlag.AlignCenter)
        self.h_BoxLayout.setContentsMargins(0, 0, 0, 0)
        self.view.itemClicked.connect(self._on_item_clicked)

    
    def _on_item_clicked(self, item):
        action = item.data(Qt.ItemDataRole.UserRole)
        if action not in self._actions:
            logger.error(action.text() + ' not in action list!')
            return None
        None._hide_menu(False)
        logger.debug(action.text() + ' trigger!')
        action.trigger()

    
    def _set_shadow_effect(self, blur_radius, offset, color = (30, (0, 8), QColor(0, 0, 0, 30))):
        '''QGraphicsDropShadowEffect 为控件添加阴影'''
        shadow_effect = QGraphicsDropShadowEffect(self.view)
        shadow_effect.setBlurRadius(blur_radius)
    # WARNING: Decompyle incomplete

    
    def _adjust_size(self):
        m = self.layout().contentsMargins()
        w = m.left() + self.view.width() + m.right()
        h = m.top() + self.view.height() + m.bottom()
        self.setFixedSize(w, h)

    
    def _adjust_item_size(self, item, action):
        item.setText(' ' + action.text())
        space = 4 - self.view.fontMetrics().horizontalAdvance(' ')
        width = 60 + self.view.fontMetrics().horizontalAdvance(item.text()) + space
        item.setSizeHint(QSize(width, self.item_height))
        return width

    
    def _create_icon(self, action):
        icon = QIcon(action.icon())
        return icon

    
    def _create_action_item(self = None, action = None, before = None):
        if not before:
            self._actions.append(action)
            super().addAction(action)
        elif before in self._actions:
            index = self._actions.index(before)
            super().insertAction(before, action)
        else:
            logger.error('before not in action list')
        item = QListWidgetItem(self._create_icon(action), action.text())
        self._adjust_item_size(item, action)
        item.setData(Qt.ItemDataRole.UserRole, action)
        action.setProperty('item', item)
        action.changed.connect(self._on_action_changed)
        return item

    
    def _on_action_changed(self):
        self.view.adjust_size()
        self._adjust_size()

    _on_action_changed = pyqtSlot()(_on_action_changed)
    
    def _remove_item(self, item):
        self.view.take_item(self.view.row(item))
        item.setData(Qt.ItemDataRole.UserRole, None)
        widget = self.view.itemWidget(item)
        if widget:
            widget.deleteLater()

    
    def _hide_menu(self, is_hide_auto = (False,)):
        self.view.clearSelection()
        self.close()

    
    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())
        if not widget is not self.view and self.view.isAncestorOf(widget):
            self._hide_menu(True)

    
    def add_action(self, action):
        item = self._create_action_item(action)
        self.view.add_item(item)
        self._adjust_size()

    
    def insert_action(self, action, before):
        if before not in self._actions:
            return None
        before_item = None.property('item')
        if not before_item:
            return None
        index = None.view.row(before_item)
        item = self._create_action_item(action)
        self.view.insert_item(index, item)
        self._adjust_size()

    
    def remove_action(self = None, action = None):
        if action not in self._actions:
            return None
        item = None.property('item')
        self._actions.remove(action)
        action.setProperty('item', None)
        if not item:
            return None
        None._remove_item(item)
        super().removeAction(action)

    
    def add_actions(self, actions):
        for action in actions:
            self.add_action(action)

    
    def clear(self):
        for _a in self._actions:
            self.removeAction(_a)

    
    def exec_(self, mouse_pos):
        menu_size = self.sizeHint()
        logger.debug('mouse_pos === x %d y %d' % (mouse_pos.x(), mouse_pos.y()))
        logger.debug('menu_size === width %d height %d' % (menu_size.width(), menu_size.height()))
        adjusted_pos = mouse_pos
        self.exec(adjusted_pos)

    __classcell__ = None

if __name__ == '__main__':
    app = QApplication([])
    menu = BaseMenu()
    menu.show()
    sys.exit(app.exec())
