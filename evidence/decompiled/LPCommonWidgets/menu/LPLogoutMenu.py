# Source Generated with Decompyle++
# File: LPLogoutMenu.pyc (Python 3.9)

'''
@Time ： 2025/1/7 15:26
@Auth ： Chris
@File ：LPLogoutMenu.py
@Desc:
'''
from PyQt6.QtCore import QCoreApplication, QPoint, pyqtSignal, pyqtSlot, Qt, QSize
from PyQt6.QtGui import QAction, QFontMetrics
from PyQt6.QtWidgets import QMenu
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPBaseMenu import BaseMenu

class LogoutMenu(QMenu):
    
    def __init__(self = None, loginButton = None, parent = None):
        super().__init__(parent)
        self.loginButton = loginButton
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                font-family: "%s";\n                font-size: 14px;\n            }\n            QMenu::item{\n                border-radius: 1px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                margin-left: 2px;\n                margin-right: 2px;\n                margin-top: 2px;\n                margin-bottom: 2px;\n                padding-left: 6px;\n                padding-right: 6px;\n                \n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n                      \n            QMenu::item:hover {\n                background-color: %s;\n            }\n            \n            QMenu::item:disabled{\n                color: %s;\n            }\n        ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), getFontFamily(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
        self.accountAction = QAction(self.parent.account.showName)
        self.set_elided_action_text(self.accountAction, 150)
        self.addAction(self.accountAction)
        logoutActionText = QCoreApplication.translate('logout', 'Logout')
        self.logoutAction = self.addAction(logoutActionText)
        self.logoutAction.triggered.connect(self.validateLogout)

    
    def showMenu(self):
        button_bottom_right = self.loginButton.mapToGlobal(self.loginButton.rect().bottomRight())
        menu_size = self.sizeHint()
        menu_x = button_bottom_right.x() - menu_size.width()
        menu_y = button_bottom_right.y() + 10
        self.exec(QPoint(menu_x, menu_y))

    
    def set_elided_action_text(self, action, max_width):
        '''超出部分设置省略号'''
        font = action.font()
        font_metrics = QFontMetrics(font)
        elided_text = font_metrics.elidedText(action.text(), Qt.TextElideMode.ElideRight, max_width)
        action.setText(elided_text)

    
    def validateLogout(self):
        if self.parent.account.userId:
            LPGlobalUI.currentDevice.deviceStreamServiceManager.logoutAccountForSource(self.parent.source)
            self.parent.updateAccountSignal.emit()
            self.parent.updateLoginButtonSignal.emit()

    validateLogout = pyqtSlot()(validateLogout)
    __classcell__ = None

