# Source Generated with Decompyle++
# File: LPPresetMenu.pyc (Python 3.9)

'''
@Time ： 2025/4/3 10:30
@Auth ： Chris
@File ：LPPresetMenu.py
@Desc:
'''
import copy
from datetime import datetime
from threading import Thread
from xml.sax.saxutils import escape
from PyQt6.QtCore import QCoreApplication, QPoint, pyqtSignal, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import QMenu
from bs4 import BeautifulSoup
import LPGlobalUI
from HOME.LPPresetViewController import LPPresetItem
from LPClientFramework import LPUtility, LPStreamServiceManager
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily
from LPClientFramework.LPPresetManager import PresetManager
from LPClientFramework.LPUtility import logger

def escapeMenuText(text):
    '''转义 Qt 菜单助记符字符。

    :param text: 需要展示在 QMenu/QAction 中的文本。
    :returns: 可按字面显示的菜单文本。
    '''
    return str(text).replace('&', '&&')


class LPPresetMenu(QMenu):
    '''preset 菜单，负责读取预设位并执行保存。'''
    PLAY_SECTION_NAME_MAP_FOR_QOBUZ = {
        'top_tracks': 'Most popular',
        'tracks_appears_on': 'Appears on' }
    updateUISignal = pyqtSignal()
    presetResultSignal = pyqtSignal(bool)
    
    def __init__(self = None, parent = None, playList = None, playSection = None):
        '''初始化 preset 菜单。

        :param parent: 菜单宿主控件。
        :param playList: 显式传入的播放列表；为空时走当前播放队列。
        :param playSection: 仅供 minibar current-track preset 透传的播放分段。
        :returns: None。
        '''
        super().__init__(parent)
        self.parent = parent
        self.playList = playList
        self.playSection = playSection
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.updateUISignal.connect(self.updateUI)
        self.presetResultSignal.connect(self.onPresetResult)
        self.setStyleSheet('\n            QMenu{\n                border-radius: 3px;\n                background-color: %s;\n                color: rgb(255, 255, 255);\n                font-family: "%s";\n                font-size: 14px;\n                min-width: 150px;\n                min-height: 360px;               \n            }\n            QMenu::item{\n                border-radius: 3px;\n                height: 30px;\n                color: rgb(255, 255, 255);\n                min-width: 130px;\n                margin-left: 5px;\n                margin-right: 5px;\n                padding-left: 5px;\n                padding-right: 5px;\n\n            }\n            QMenu::item:selected{\n                background-color: %s;\n                color: rgb(255, 255, 255);\n            }\n\n            QMenu::item:hover {\n                background-color: %s;\n            }\n\n            QMenu::item:disabled{\n                color: %s;\n            }\n            QMenu::right-arrow {\n                width: 8px;\n                height: 8px;\n            }\n        ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), getFontFamily(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
        self.num = LPGlobalUI.currentDevice.presetNum
        self.defaultImage = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        self.aboutToShow.connect(self.fetchPresetList)
        self.presetManager = PresetManager()

    
    def onPresetResult(self, isOk):
        if isOk:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('PresetMenu', 'Preset Ok'), LPGlobalUI.mainWindow)
        else:
            LPGlobalUI.toast.showToast(QCoreApplication.translate('PresetMenu', 'Preset Failed'), LPGlobalUI.mainWindow)

    
    def fetchPresetList(self):
        
        def _parseXML(response = None):
            if response.get('error', None) is not None:
                return None
            self.xmlStr = None.get('xml', None)
            self.presetList = []
            self.xmlObj = BeautifulSoup(self.xmlStr, 'xml')
            keyList = self.xmlObj.find('KeyList', [])
            keyIndexArr = range(1, LPGlobalUI.currentDevice.presetNum + 1)
            for keyIndex in keyIndexArr:
                keyItem = keyList.find('Key%d' % keyIndex)
                presetItem = LPPresetItem()
                presetItem.index = keyIndex
                if not keyItem:
                    self.presetList.append(presetItem)
                    continue
                presetItem = LPPresetItem()
                presetItem.index = keyIndex
                name = keyItem.find('Name', None)
                if name is not None:
                    presetItem.name = name.text
                    sourceItem = keyItem.find('Source', None)
                    if sourceItem:
                        presetItem.source = sourceItem.text
                    picItem = keyItem.find('PicUrl', None)
                    if picItem:
                        presetItem.picUrl = picItem.text
                self.presetList.append(presetItem)
            self.updateUISignal.emit()

        self.presetManager.getKeyMapping(LPGlobalUI.currentDevice, _parseXML)

    
    def updateUI(self):
        self.clear()
        for presetItem in self.presetList:
            name = presetItem.name
            index = presetItem.index
            picUrl = presetItem.picUrl
            presetName = name.split('_#~')[0] if name else 'Empty'
            action = QAction(QIcon(self.defaultImage), escapeMenuText(str(index) + '  ' + str(presetName)), self)
            action.setData(presetItem)
            action.triggered.connect(self.preset)
            if picUrl:
                self.updateImage(picUrl, action)
            self.addAction(action)

    
    def preset(self):
        '''执行 preset 保存动作。

        :param: 无。
        :returns: None。
        '''
        action = self.sender()
        presetItem = action.data()
        
        def _target(presetItem = None):
            device = LPGlobalUI.currentDevice
            streamService = None
            if self.parent.source == 'PC_RemoteLocal':
                streamService = LPStreamServiceManager.streamServiceForSource(self.parent.source)
            else:
                streamService = device.deviceStreamServiceManager.streamServiceForSource(self.parent.source)
            if not streamService:
                self.presetResultSignal.emit(False)
                return None
            playList = self.presetManager.getPlayList(device) if not None.playList else self.playList
            if not playList:
                self.presetResultSignal.emit(False)
                return None
            headTitle = playList.header.headTitle if None.header.headTitle else ''
            timeStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            playSection = None if self.playList else self.playSection
            listNameBase = self.PLAY_SECTION_NAME_MAP_FOR_QOBUZ.get(playSection, playSection) if playSection else headTitle
            listName = listNameBase + '_#~' + timeStr
            ret = self.presetManager.backupQueue(device, streamService, playList, listName, playSection)
            if not ret:
                logger.debug('[preset menu] backupQueue failed')
                self.presetResultSignal.emit(False)
                return None
            replaceItemXml = None.replaceItemXml(playList, listName)
            self.xmlObj = self.presetManager.replaceKeyMappingXml(presetItem.index, replaceItemXml, self.xmlObj)
            setKeyMappingXml = str(self.xmlObj)
            ret = self.presetManager.setKeyMapping(device, setKeyMappingXml)
            if ret:
                self.presetResultSignal.emit(True)
            else:
                self.presetResultSignal.emit(False)

        t = Thread(_target, (presetItem,), **('target', 'args'))
        t.start()

    
    def replaceXmlItem(self, index, replaceXml):
        pass
    # WARNING: Decompyle incomplete

    
    def updateImage(self, url, action):
        
        def _asyncFetchImage(url = None):
            respDict = LPUtility.fetchUrlQPixmap(url)
            pixmap = respDict.get('image', None)
            if pixmap:
                action.setIcon(QIcon(pixmap))

        pixmap = LPUtility.getCachedPixmapWithUrl(url)
        if pixmap:
            action.setIcon(QIcon(pixmap))
        else:
            fetchThread = Thread(_asyncFetchImage, (url,), **('target', 'args'))
            fetchThread.start()

    
    def showMenu(self):
        button_top_right = self.parent.mapToGlobal(self.parent.rect().topRight())
        menu_size = self.sizeHint()
        menu_x = button_top_right.x() + 2
        menu_y = button_top_right.y() - menu_size.height()
        self.exec(QPoint(menu_x, menu_y))

    __classcell__ = None

