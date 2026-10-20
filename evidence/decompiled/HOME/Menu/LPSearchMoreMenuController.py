# Source Generated with Decompyle++
# File: LPSearchMoreMenuController.pyc (Python 3.9)

'''搜索页 More 菜单控制器。

将从 WiiMHome.py 中拆分出的 _showMoreMenu 代码迁移至此，
负责搜索页 moreButton 弹出的 More 菜单（手动 IP 发现 / 发送日志）。
'''
from PyQt6.QtCore import QCoreApplication, QObject, Qt, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily

class LPSearchMoreMenuController(QObject):
    '''管理搜索页 moreButton 弹出的 More 菜单。'''
    
    def __init__(self = None, owner = None, onOpenIPDiscover = None, anchorButton = None):
        '''初始化搜索页 More 菜单控制器。

        参数:
            owner (QMainWindow): 主窗口实例。
            onOpenIPDiscover (callable): 打开 IP 发现对话框的回调。
            anchorButton (QWidget): 菜单锚点按钮（moreButton），用于计算弹出位置。
        返回:
            无。
        '''
        super().__init__()
        self.owner = owner
        self._onOpenIPDiscover = onOpenIPDiscover
        self.anchorButton = anchorButton

    
    def showMoreMenu(self):
        '''
        弹出搜索页 More 菜单。

        参数:
            无
        返回:
            无
        '''
        moreMenu = QMenu()
        moreMenu.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        moreMenu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        font_family = getFontFamily()
        font_family_rule = f'''font-family: "{font_family}";''' if font_family else ''
        moreMenu.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                %s\n                font-size: 14px;\n            }\n            QMenu::item{\n                border-radius: 2px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                margin-left: 4px;\n                margin-right: 4px;\n                margin-top: 4px;\n                margin-bottom: 4px;\n                padding-left: 6px;\n                padding-right: 6px;\n\n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n\n            QMenu::item:hover {\n                background-color: %s;\n            }\n\n            QMenu::item:disabled{\n                color: %s;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), font_family_rule, LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
        ipDiscoverMenuText = QCoreApplication.translate('MoreMenu', 'Manually discovering devices via IP')
        ipDiscoverAction = QAction(ipDiscoverMenuText)
        ipDiscoverAction.triggered.connect(self._onOpenIPDiscover)
        sendLogMenuText = QCoreApplication.translate('MoreMenu', 'Send logs to WiiM Support')
        sendLogAction = QAction(sendLogMenuText)
        sendLogAction.triggered.connect((lambda : LPUtility.openFileInSystem(LPUtility.logDir)))
        moreMenu.addAction(ipDiscoverAction)
        moreMenu.addAction(sendLogAction)
        pos = self.anchorButton.mapToGlobal(QPoint(0, self.anchorButton.height() + 5))
        moreMenu.exec(pos)

    __classcell__ = None

