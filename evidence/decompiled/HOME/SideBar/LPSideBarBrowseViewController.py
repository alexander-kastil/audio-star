# Source Generated with Decompyle++
# File: LPSideBarBrowseViewController.pyc (Python 3.9)

'''
@Time ： 2025/11/17 11:15
@Auth ： Chris
@File ：LPSideBarBrowseViewController.py
@Desc:
'''
from string import Template
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication, QEvent, QPropertyAnimation, QEasingCurve
import LPGlobalUI
from HOME.SideBar.LPSideBarListView import LPSideBarListDelegate, LPSideBarListModel
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import Min_Text
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter

class LPSideBarBrowseViewController(QObject):
    updateCurrentSelectSignal = pyqtSignal(object)
    
    def __init__(self = None, mainUI = None, browseSelectMethod = None):
        super().__init__()
        self.dataArray = [
            {
                'id': 'recently',
                'icon': 'sidebar/favorite_browse.png',
                'title': QCoreApplication.translate('SideBarBrowse', 'Recently Played') },
            {
                'id': 'presets',
                'icon': 'sidebar/preset_browse.png',
                'title': QCoreApplication.translate('SideBarBrowse', 'Presets') },
            {
                'id': 'homeshare',
                'icon': 'sidebar/homeshare_browse.png',
                'title': QCoreApplication.translate('SideBarBrowse', 'Home Music Server') }]
        self.browseSelectMethod = browseSelectMethod
        self.browseList = mainUI.browseListView
        model = LPSideBarListModel(self.dataArray, self.browseList)
        delegate = LPSideBarListDelegate(self.browseList)
        self.browseList.setModel(model)
        self.browseList.setItemDelegate(delegate)
        self.browseList.clicked.connect(self.itemSelect)
        self.collapseButton = mainUI.browseCollapseButton
        self.collapseButton.setCheckable(True)
        self.collapseButton.setChecked(False)
        self.collapseButtonUpDefaultImage = LPUtility.tintImage(LPGlobalUI.imagePath('arrow_up.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        self.collapseButtonDownDefaultImage = LPUtility.tintImage(LPGlobalUI.imagePath('arrow_down.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonUpDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_up.png')), QIcon(LPGlobalUI.imagePath('arrow_up.png')), 'image')
        self.anim = QPropertyAnimation(self.browseList, b'maximumHeight')
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.collapseButton.toggled.connect(self.toggleCollapse)
        self.browseTitleLabel = mainUI.browseTitleLabel
        self.browseTitleLabel.setText(QCoreApplication.translate('SiderBar', 'Browse'))
        self.browseSectionFrame = mainUI.browseSectionFrame
        stylesheetTemplate = Template('\n                QFrame {\n                    background: transparent;\n                    border:none;\n                }\n                QLabel#browseTitleLabel {\n                    color: ${titleColor};\n                    font-size: ${browseTitleLabelFontSize}pt;\n                }\n                ')
        self.browseSectionFrame.setStyleSheet(stylesheetTemplate.substitute(LPGlobalUI.QSS_THEME_LIGHT_COLOR_UI, f'''{Min_Text}''', **('titleColor', 'browseTitleLabelFontSize')))
        self.browseList.setMaximumHeight(45 * len(self.dataArray))
        self.listHeight = self.browseList.maximumHeight()
        self.updateCurrentSelectSignal.connect(self.updateCurrentSelect)

    
    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.dataArray = [
                {
                    'id': 'recently',
                    'icon': 'sidebar/favorite_browse.png',
                    'title': QCoreApplication.translate('SideBarBrowse', 'Recently Played') },
                {
                    'id': 'preset',
                    'icon': 'browse/preset.png',
                    'title': QCoreApplication.translate('SideBarBrowse', 'Preset') },
                {
                    'id': 'preset_qml',
                    'icon': 'browse/preset.png',
                    'title': QCoreApplication.translate('SideBarBrowse', 'Preset (QML)') },
                {
                    'id': 'homeshare',
                    'icon': 'browse/homeshare.png',
                    'title': QCoreApplication.translate('SideBarBrowse', 'Home Music Server') }]

    
    def toggleCollapse(self = None, collapsed = None):
        if collapsed:
            LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonDownDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_down.png')), QIcon(LPGlobalUI.imagePath('arrow_down.png')), 'image')
        else:
            LPButtonEventFilter(self.collapseButton, QIcon(self.collapseButtonUpDefaultImage), QIcon(LPGlobalUI.imagePath('arrow_up.png')), QIcon(LPGlobalUI.imagePath('arrow_up.png')), 'image')
        w = self.browseList
        cur = w.height()
        full = self.listHeight
        self.anim.stop()
        if collapsed:
            self.browseList.setMinimumHeight(0)
            self.anim.setStartValue(cur)
            self.anim.setEndValue(0)
        else:
            self.anim.setStartValue(cur)
            self.anim.setEndValue(full)
        self.anim.start()

    
    def updateCurrentSelect(self, itemId):
        for row, itemDict in enumerate(self.dataArray):
            if itemDict['id'] == itemId:
                model = self.browseList.model()
                index = model.index(row, 0)
                self.browseList.setCurrentIndex(index)
                return None
            self.browseList.clearSelection()
            return None

    
    def itemSelect(self, index):
        selectedIndex = index.row()
        dataDict = self.dataArray[selectedIndex]
        if self.browseSelectMethod:
            self.browseSelectMethod(dataDict['id'])

    __classcell__ = None

