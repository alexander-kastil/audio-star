# Source Generated with Decompyle++
# File: LPQobuzViewController.pyc (Python 3.9)

'''
@Time ： 2025/5/29 9:16
@Auth ： Chris
@File ：LPQobuzViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QTimer, QSize, QEvent
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QButtonGroup, QListView, QLineEdit, QPushButton
import LPGlobalUI
from HOME.StreamService.Qobuz.Browse.LPQobuzBrowseBaseViewController import LPQobuzBrowseBaseViewController, LPQobuzBrowseType
from HOME.StreamService.Qobuz.Browse.LPQobuzDiscoverViewController import LPQobuzDiscoverViewController
from HOME.StreamService.Qobuz.Browse.LPQobuzLibraryViewController import LPQobuzLibraryViewController
from HOME.StreamService.Qobuz.Browse.UI.LPQobuzDiscoverViewController_ui import Ui_qobuzDiscoverWidget
from HOME.StreamService.Qobuz.Browse.UI.LPQobuzLibraryViewController_ui import Ui_qobuzLibraryWidget
from HOME.StreamService.Qobuz.Login.LPQobuzLogoutDialog import LPQobuzLogoutDialog
from HOME.StreamService.Qobuz.Login.UI.LPQobuzLogout_ui import Ui_qobuzLogoutDialog
from HOME.StreamService.Qobuz.Search.LPQobuzSearchViewController import LPQobuzSearchViewController
from HOME.StreamService.Qobuz.Util import LPQobuzUtil
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, Qobuz_Tab_Title
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.search.LPSearch_ui import Ui_searchWidget

class LPQobuzViewController(LPQobuzBrowseBaseViewController):
    startQobuzSignal = pyqtSignal()
    updateLoginButtonSignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        self.account = None
        self.startQobuzSignal.connect(self._startQobuz)
        self.updateLoginButtonSignal.connect(self.updateLoginButtonUI)
        self.searchPage = None
        self.currentPage = None
        self.group = None

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.discoverButton.setCheckable(True)
        None((lambda : self.switchTo('discover')))
        self.libButton.setCheckable(True)
        None((lambda : self.switchTo('library')))
        self.group = QButtonGroup(self)
        self.group.addButton(self.discoverButton)
        self.group.addButton(self.libButton)
        self.group.setExclusive(True)
        self.searchFieldClearAction = QAction('clear', self)
        self.searchFieldClearAction.setIcon(QIcon(LPGlobalUI.imagePath('search_close.png')))
        self.searchField.addAction(self.searchFieldClearAction, QLineEdit.ActionPosition.TrailingPosition)
        None((lambda : self.searchField.clear()))
        self.searchFieldClearAction.setVisible(False)
        self.searchField.installEventFilter(self)
        self.loginButton.clicked.connect(self.loginButtonClicked)
        stylesheetTemplate = Template('\n                LPLineEdit {\n                    background-color: rgb(31, 31, 31); \n                    color: white; \n                    padding: 5px; \n                    border-radius: 5px; \n                    qproperty-placeholderColor: rgba(255, 255, 255, 89);\n                }\n                \n                QLabel#label {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n                QFrame#VSplitFrame{\n                    background-color: rgb(30, 30, 30);\n                }\n                QPushButton {\n                    font-size: ${tabTitleFontSize}pt;\n                    color: $fontColor;\n                    background-color: transparent;\n                }\n                QPushButton:checked {\n                    color: $checkedFontColor;\n                    \n                }\n                QPushButton#discoverButton, #libButton {\n                    background-color: rgb(31, 31, 31); \n                    border-radius: 5px;\n                    padding: 8px 16px;\n                    width: 80px;                   \n                }\n                QScrollBar {\n                    border: 0px;\n                    background: transparent;\n                    width:10px;\n                    height:10px;\n                    margin: 0px 0px 0px 0px;\n                }\n                QScrollBar::handle {\n                    background: rgb(82,82,82);\n                    min-height: 0px;\n                    border-radius: 5px;\n                }\n                QScrollBar::add-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::sub-line {\n                    border: 0px;\n                    background: none;\n                    height: 0px;\n                    width: 0px;\n                }\n                QScrollBar::add-page, QScrollBar::sub-page {\n                    height: 0px;\n                    width: 0px;\n                    border: 0px;\n            }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', f'''{Qobuz_Tab_Title}''', LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), **('stackWidgetTiteFontSize', 'tabTitleFontSize', 'fontColor', 'checkedFontColor')))
        self.pages = {
            'discover': LPGlobalUI.loadUI(LPUIPath.QobuzDiscoverViewControllerUI, Ui_qobuzDiscoverWidget, LPQobuzDiscoverViewController, self) }
        for page in self.pages.values():
            self.stackedWidget.addWidget(page)

    
    def switchTo(self = None, pageName = None):
        logger.debug(f'''[qobuz switchTo] == {pageName}''')
        if pageName not in self.pages:
            if pageName == 'library':
                page = LPGlobalUI.loadUI(LPUIPath.QobuzLibraryViewControllerUI, Ui_qobuzLibraryWidget, LPQobuzLibraryViewController, self)
            elif pageName == 'search':
                page = LPGlobalUI.loadUI(LPUIPath.SearchUI, Ui_searchWidget, LPQobuzSearchViewController, self)
            else:
                page = self.pages['discover']
            self.pages[pageName] = page
        page = self.pages[pageName]
        self.currentPage = pageName
        LPQobuzUtil.setCurrentWidget(self.stackedWidget, page)

    
    def _startQobuz(self):
        if self.currentPage:
            self.switchTo(self.currentPage)
        else:
            self.switchTo('discover')
            self.discoverButton.setChecked(True)

    
    def viewWillAppear(self):
        logger.debug('Qobuz viewWillAppear')
        self.stackedWidget.setCurrentIndex(0)
        self.updateUI(LPGlobalUI.currentDevice)

    
    def viewWillDisappear(self):
        self.endSkeleton()

    
    def updateUI(self, device):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            if self.source not in LPGlobalUI.currentDevice.deviceStreamServiceManager.streamServiceCapability.keys():
                return None
            None._onUserLoginFinish()

    
    def _onUserLoginFinish(self):
        '''账号就绪后刷新登录按钮并进入 Qobuz 页面，未登录时保持当前状态。'''
        self.account = self.qobuz.loginMgr.getAccount(LPGlobalUI.currentDevice)
        if self.account and self.account.userId:
            self.updateLoginButtonSignal.emit()
            self.startQobuzSignal.emit()

    _onUserLoginFinish = pyqtSlot()(_onUserLoginFinish)
    
    def updateLoginButtonUI(self):
        self.loginButton.setVisible(True)
        if self.account.userId:
            logger.debug('[Qobuz] updateLoginButtonUI ==== self.account')
            firstLetter = self.account.showName[:1].upper()
            avatarPixmap = LPUtility.generate_avatar(firstLetter)
            self.loginButton.setIcon(QIcon(avatarPixmap))
            self.loginButton.setFixedSize(40, 40)
            self.loginButton.setIconSize(QSize(40, 40))

    updateLoginButtonUI = pyqtSlot()(updateLoginButtonUI)
    
    def loginButtonClicked(self):
        if self.account and self.account.userId:
            logoutDialog = LPGlobalUI.loadUI(LPUIPath.QobuzLogoutDialogUI, Ui_qobuzLogoutDialog, LPQobuzLogoutDialog, self.account, self.loginButton, self)
            logoutDialog.showDialog()

    loginButtonClicked = pyqtSlot()(loginButtonClicked)
    
    def searchFieldChanged(self, text):
        logger.debug(f'''[LPQobuzViewController] searchFieldChanged text={text}''')
        self.searchFieldClearAction.setVisible(len(text) > 0)

    
    def eventFilter(self = None, obj = None, event = None):
        if obj == self.searchField and event.type() == QEvent.Type.MouseButtonPress:
            self.clearButtonGroupselection(self.group)
            self.switchTo('search')
            return False
        return None().eventFilter(obj, event)

    
    def clearButtonGroupselection(self, group):
        group.setExclusive(False)
        for btn in group.buttons():
            btn.setChecked(False)
        group.setExclusive(True)

    
    def onFavIdsLoaded(self):
        logger.debug('onFavIdsLoaded====')
        page = self.pages[self.currentPage]
        if self.currentPage == 'library':
            page.onSectionDataChanged(self.qobuz.currentAccount, 'Purchased Tracks')

    __classcell__ = None

