# Source Generated with Decompyle++
# File: LPSideBarMyLibraryViewController.pyc (Python 3.9)

'''
@Time ： 2025/11/17 13:40
@Auth ： Chris
@File ：LPSideBarMyLibraryViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication, QEvent, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor, QIcon
import LPGlobalUI
from HOME.LPWaitingSpinner import LPWaitingSpinner
from HOME.SideBar.LPSideBarListView import LPSideBarListModel, LPSideBarListDelegate
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import Min_Text
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPUtility import logger

class LPSideBarMyLibraryViewController(QObject):
    updateCurrentSelectSignal = pyqtSignal(object)
    showLoadingButtonSignal = pyqtSignal(object)
    DETAIL_ID_TO_SIDEBAR_ID = {
        'albumdetail': 'albums_lib',
        'artistdetail': 'artists_lib',
        'genredetail': 'genres_lib',
        'mymusic': 'folders_lib',
        'mymusicsettings': 'folders_lib' }
    
    def __init__(self = None, mainUI = None, libSelectMethod = None, showImportWaitingDialogMethod = None):
        super().__init__()
        self.loadingSpinner = None
        self.dataArray = [
            {
                'id': 'genres_lib',
                'icon': 'sidebar/genres_lib.png',
                'title': QCoreApplication.translate('SideBarLib', 'Genres') },
            {
                'id': 'albums_lib',
                'icon': 'sidebar/albums_lib.png',
                'title': QCoreApplication.translate('SideBarLib', 'Albums') },
            {
                'id': 'artists_lib',
                'icon': 'sidebar/artists_lib.png',
                'title': QCoreApplication.translate('SideBarLib', 'Artists') },
            {
                'id': 'tracks_lib',
                'icon': 'sidebar/tracks_lib.png',
                'title': QCoreApplication.translate('SideBarLib', 'Tracks') },
            {
                'id': 'folders_lib',
                'icon': 'sidebar/folders_lib.png',
                'title': QCoreApplication.translate('SideBarLib', 'Folders') }]
        self.libSelectMethod = libSelectMethod
        self.showImportWaitingDialogMethod = showImportWaitingDialogMethod
        self.libList = mainUI.myLibraryListView
        model = LPSideBarListModel(self.dataArray, self.libList)
        delegate = LPSideBarListDelegate(self.libList)
        self.libList.setModel(model)
        self.libList.setItemDelegate(delegate)
        self.libList.clicked.connect(self.itemSelect)
        self.collapseButton = mainUI.myLibraryCollapseButton
        self.collapseButton.setCheckable(True)
        self.collapseButton.setChecked(False)
        self.collapseButtonUpDefaultImage = LPUtility.tintImage(LPGlobalUI.imagePath('arrow_up.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        self.collapseButtonDownDefaultImage = LPUtility.tintImage(LPGlobalUI.imagePath('arrow_down.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonUpDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_up.png')), QIcon(LPGlobalUI.imagePath('arrow_up.png')), 'image')
        self.anim = QPropertyAnimation(self.libList, b'maximumHeight')
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self.onAnimFinished)
        self.collapseButton.toggled.connect(self.toggleCollapse)
        self.showLoadingButtonSignal.connect(self._showLoadingButton)
        self.loadingButton = mainUI.myLibraryLoadingButton
        self.loadingButton.setEnabled(False)
        self.loadingButton.clicked.connect(self.loadingButtonPressed)
        self.myLibraryTitleLabel = mainUI.myLibraryTitleLabel
        self.myLibraryTitleLabel.setText(QCoreApplication.translate('SiderBar', 'My Library'))
        self.myLibrarySectionFrame = mainUI.myLibrarySectionFrame
        stylesheetTemplate = Template('\n                QFrame {\n                    background: transparent;\n                    border:none;\n                }\n                QLabel#myLibraryTitleLabel {\n                    color: ${titleColor};\n                    font-size: ${myLibraryTitleLabelFontSize}pt;\n                }\n                ')
        self.myLibrarySectionFrame.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.QSS_THEME_LIGHT_COLOR_UI, f'''{Min_Text}''', **('titleColor', 'myLibraryTitleLabelFontSize')))
        self.listHeight = self.libList.maximumHeight()
        self.updateCurrentSelectSignal.connect(self.updateCurrentSelect)

    
    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.dataArray = [
                {
                    'id': 'genres_lib',
                    'icon': 'sidebar/genres_lib.png',
                    'title': QCoreApplication.translate('SideBarLib', 'Genres') },
                {
                    'id': 'albums_lib',
                    'icon': 'sidebar/albums_lib.png',
                    'title': QCoreApplication.translate('SideBarLib', 'Albums') },
                {
                    'id': 'artists_lib',
                    'icon': 'sidebar/artists_lib.png',
                    'title': QCoreApplication.translate('SideBarLib', 'Artists') },
                {
                    'id': 'tracks_lib',
                    'icon': 'sidebar/tracks_lib.png',
                    'title': QCoreApplication.translate('SideBarLib', 'Tracks') },
                {
                    'id': 'folders_lib',
                    'icon': 'sidebar/folders_lib.png',
                    'title': QCoreApplication.translate('SideBarLib', 'Folders') }]

    
    def toggleCollapse(self = None, collapsed = None):
        if collapsed:
            LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonDownDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_down.png')), QIcon(LPGlobalUI.imagePath('arrow_down.png')), 'image')
        else:
            LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonUpDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_up.png')), QIcon(LPGlobalUI.imagePath('arrow_up.png')), 'image')
        w = self.libList
        cur = w.height()
        full = self.listHeight
        logger.debug(f'''cur = {cur}''')
        logger.debug(f'''full = {full}''')
        self.anim.stop()
        if collapsed:
            self.libList.setMinimumHeight(0)
            self.anim.setStartValue(cur)
            self.anim.setEndValue(0)
        else:
            self.anim.setStartValue(cur)
            self.anim.setEndValue(full)
        self.anim.start()

    
    def onAnimFinished(self):
        w = self.libList
        cur = w.height()
        if cur == 0:
            self.libList.setMinimumHeight(0)
        else:
            self.libList.setMinimumHeight(self.listHeight)

    
    def _showLoadingButton(self, show):
        if show:
            self.loadingButton.show()
            self.loadingButton.setEnabled(True)
            self.loadingButton.setCursor(Qt.CursorShape.PointingHandCursor)
            if self.loadingSpinner is None:
                self.loadingSpinner = LPWaitingSpinner(self.loadingButton, 30, 40, 6, 50, 3, 1, 1.5, QColor(255, 255, 255), **('roundness', 'fade', 'radius', 'lines', 'line_length', 'line_width', 'speed', 'color'))
            if not self.loadingSpinner.is_spinning:
                self.loadingSpinner.show()
                self.loadingSpinner.start()
            else:
                self.loadingButton.hide()
                self.loadingButton.setEnabled(False)
                if self.loadingSpinner and self.loadingSpinner.is_spinning:
                    self.loadingSpinner.stop()

    
    def showLoadingButton(self, show):
        self.showLoadingButtonSignal.emit(show)

    
    def loadingButtonPressed(self):
        self.showImportWaitingDialogMethod()

    
    def updateCurrentSelect(self, itemId):
        '''
        根据当前导航 id 更新 My Library 侧边栏选中项。

        参数:
            itemId: 当前页面导航标识。
        返回值:
            None。
        '''
        normalizedItemId = self.DETAIL_ID_TO_SIDEBAR_ID.get(itemId, itemId)
        for row, itemDict in enumerate(self.dataArray):
            if itemDict['id'] == normalizedItemId:
                model = self.libList.model()
                index = model.index(row, 0)
                self.libList.setCurrentIndex(index)
                return None
            self.libList.clearSelection()
            return None

    
    def itemSelect(self, item):
        selectedIndex = item.row()
        dataDict = self.dataArray[selectedIndex]
        if self.libSelectMethod:
            self.libSelectMethod(dataDict['id'])

    __classcell__ = None

