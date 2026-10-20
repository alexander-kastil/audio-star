# Source Generated with Decompyle++
# File: LPQueueOptionMenu.pyc (Python 3.9)

'''
@Time ： 2025/10/10 15:22
@Auth ： Chris
@File ：LPQueueOptionMenu.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMenu, QWidgetAction, QSizePolicy
import LPGlobalUI
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT, Main_Text
from LPCommonWidgets.menu.LPCustomMenu import LPIconTextMenuItemWidget, LPMenuItem
from LPCommonWidgets.menu.UI.LPIconTextMenuItem_ui import Ui_iconTextMenuItemWidget

class LPQueueMenuItemWidget(LPIconTextMenuItemWidget):
    clicked = pyqtSignal()
    
    def __init__(self = None, item = None, callback = None, **kwargs):
        super().__init__(item)
        self.callback = callback

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        stylesheetTemplate = Template('\n                QWidget {\n                    background-color: transparent;\n                }\n                QFrame#mainFrame:hover {\n                    background-color: $itemHoverBg;\n                    border-radius: 4px;\n                }\n                \n                QLabel {\n                    font-size: ${menuItemFontSize}pt;\n                    color: white;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{DEFAULT}''', LPGlobalUI.QSS_MENU_HOVER_COLOR, **('menuItemFontSize', 'itemHoverBg')))

    
    def mouseReleaseEvent(self = None, event = None):
        if event.button() == Qt.MouseButton.LeftButton:
            self.item.clicked.emit()
            if self.callback:
                self.callback()
        super().mouseReleaseEvent(event)

    __classcell__ = None


class LPQueueOptionMenu(QMenu):
    
    def __init__(self = None, items = None, parent = None):
        super().__init__(parent)
        self.items = items
        self.setContent()
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        stylesheetTemplate = Template('\n                QMenu{\n                    border-radius: 4px;\n                    background-color: $menuBg;\n                    color: rgb(255, 255, 255);\n                    font-size: $menuFontSize;\n                    width: 230px;\n                    padding: 3px 4px 3px 4px;\n                }\n            ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{Main_Text}''', LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), **('menuFontSize', 'menuBg')))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    
    def setContent(self):
        self.clear()
        for item in self.items:
            action = QWidgetAction(self)
            widget = LPGlobalUI.loadUI(LPUIPath.LPIconTextMenuItemUI, Ui_iconTextMenuItemWidget, LPQueueMenuItemWidget, item)
            action.setDefaultWidget(widget)
            self.addAction(action)

    
    def updateItems(self, items):
        '''动态刷新菜单内容'''
        self.items = items
        self.setContent()

    __classcell__ = None

