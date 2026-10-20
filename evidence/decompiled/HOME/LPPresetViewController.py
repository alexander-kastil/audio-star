# Source Generated with Decompyle++
# File: LPPresetViewController.pyc (Python 3.9)

import copy
from enum import Enum
from string import Template
from PyQt6.QtWidgets import *
from PyQt6 import QtWidgets
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QCoreApplication
from PyQt6.QtGui import QCursor
import LPGlobalUI
import threading
from bs4 import BeautifulSoup
from HOME.LPPresetItemCard_ui import Ui_PresetItemCard
from LPCommonWidgets.dialog.LPAdaptiveMessageBox import LPAdaptiveMessageBox
from LPClientFramework import LPStreamServiceManager, LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, getFontFamily
from LPClientFramework.LPUtility import logger
round_corner_value = 5

class LPPresetViewControllerState(Enum):
    ready = (0,)
    notReady = (1,)
    notSupport = (3,)
    error = (3,)


class LPPresetItem(object):
    
    def __init__(self):
        self.index = 0
        self.name = None
        self.source = None
        self.picUrl = None



class LPPresetItemCard(QWidget):
    updateSourceSignal = pyqtSignal()
    
    def __init__(self = None):
        super(LPPresetItemCard, self).__init__()
        self._item = None
        self.coverImage = None
        self.hover = False
        self.defaultImage = None
        self.clickMethod = None
        self.installEventFilter(self)
        self.updateSourceSignal.connect(self.updateSource)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.defaultImage = self._roundCornerImage(QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png')))

    
    def _roundCornerImage(self, pixmap):
        width = pixmap.width()
        height = pixmap.height()
        scaledMap = pixmap
        mask = QtGui.QBitmap(width, height)
        mask.fill(Qt.GlobalColor.color0)
        painter = QtGui.QPainter(mask)
        painter.setBrush(QtCore.Qt.GlobalColor.color1)
        painter.drawRoundedRect(0, 0, width, height, round_corner_value, round_corner_value)
        scaledMap.setMask(mask)
        painter.end()
        return scaledMap

    
    def item(self):
        return self._item

    item = property(item)
    
    def item(self, item):
        self._item = item
        self.updateSourceSignal.emit()

    item = item.setter(item)
    
    def updateSource(self):
        supportContents = LPStreamServiceManager.supportContents()
        infoDict = supportContents.get(self.item.source, None)
        if infoDict is None:
            return None
        None.smallSourceImageView.setPixmap(QtGui.QPixmap(LPGlobalUI.imagePath('streamservice/%s.png' % infoDict.get('flat_icon', ''))))

    
    def updateImage(self, imageUrl):
        if imageUrl is None or len(imageUrl) == 0:
            return None
        
        def _asyncFetchImage(imageUrl = None):
            respDict = LPUtility.fetchUrlQPixmap(imageUrl)
            pixmap = respDict.get('image', None)
            if pixmap:
                self.coverImage = self._roundCornerImage(pixmap)
                self.update()

        pixmap = LPUtility.getCachedPixmapWithUrl(imageUrl)
        if pixmap:
            self.coverImage = self._roundCornerImage(pixmap)
            self.update()
        else:
            fetchThread = threading.Thread(_asyncFetchImage, (imageUrl,), **('target', 'args'))
            fetchThread.start()

    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        brush = QtGui.QBrush()
        if self.hover == False:
            brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        else:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(rect), round_corner_value, round_corner_value)
        painter.fillPath(path, brush)
        rect = QtCore.QRect(self.coverImageFrame.pos().x(), self.coverImageFrame.pos().y(), self.coverImageFrame.size().width(), self.coverImageFrame.size().height())
        if self.coverImage:
            icon = QtGui.QIcon()
            icon.addPixmap(self.coverImage)
            icon.paint(painter, rect.x(), rect.y(), rect.width(), rect.height())
        else:
            painter.drawPixmap(rect, self.defaultImage, self.defaultImage.rect())

    
    def eventFilter(self = None, source = None, event = None):
        if event.type() == QEvent.Type.Enter:
            self.hover = True
            if self.item.name is not None:
                self.indexLabel.setPixmap(QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/play.png')))
            self.update()
        elif event.type() == QEvent.Type.Leave:
            self.hover = False
            self.indexLabel.clear()
            self.update()
        elif event.type() == QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton and self.item.name is not None and self.clickMethod:
            self.clickMethod(self.item)
        return super().eventFilter(source, event)

    __classcell__ = None


class LPPresetViewController(QWidget):
    updateUISignal = pyqtSignal()
    
    def __init__(self = None):
        super(LPPresetViewController, self).__init__()
        self.status = LPPresetViewControllerState.notReady
        self.presetList = None
        self.updateUISignal.connect(self._updateUI)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.presetListWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.NoDragDrop)
        self.presetListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.presetListWidget.customContextMenuRequested.connect(self.openMenu)
        stylesheetTemplate = Template('\n                QLabel#label {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))

    
    def openMenu(self, pos):
        item = None
        widgetItem = self.presetListWidget.itemAt(pos)
        if widgetItem:
            widget = self.presetListWidget.itemWidget(widgetItem)
            if widget:
                item = widget.item
        if not item:
            return None
        if not None.name:
            return None
        menu = None(self.presetListWidget)
        menu.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        font_family = getFontFamily()
        font_family_rule = f'''font-family: "{font_family}";''' if font_family else ''
        menu.setStyleSheet('\n                    QMenu{\n                        border-radius: 3px;\n                        background-color: %s;\n                        color: rgb(255, 255, 255);\n                        %s\n                        font-size: 14px;\n                        min-width: 150px;               \n                    }\n                    QMenu::item{\n                        border-radius: 3px;\n                        height: 30px;\n                        color: rgb(255, 255, 255);\n                        min-width: 130px;\n                        margin-left: 5px;\n                        margin-right: 5px;\n                        padding-left: 5px;\n                        padding-right: 5px;\n\n                    }\n                    QMenu::item:selected{\n                        background-color: %s;\n                        color: rgb(255, 255, 255);\n                    }\n\n                    QMenu::item:hover {\n                        background-color: %s;\n                    }\n\n                    QMenu::item:disabled{\n                        color: %s;\n                    }\n                    QMenu::right-arrow {\n                        width: 8px;\n                        height: 8px;\n                    }\n                    ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), font_family_rule, LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
        
        def _showDeleteConfirm():
            '''弹出删除确认弹窗，预设名称较长时自动换行显示。'''
            box = LPAdaptiveMessageBox(self.presetListWidget)
            box.setWindowFlags(box.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
            box.setText(QCoreApplication.translate('Preset', 'Delete %s ? ') % item.name.split('_#~')[0])
            box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            box.setStyleSheet('\n            QMessageBox {\n            background: %s;\n            border-radius: 10px;\n            }\n            QMessageBox QLabel {\n            color: %s;\n            padding-top: 30px;\n            padding-right: 21px;\n            background: transparent;\n            }\n            QPushButton {background-color: transparent;\n        border-radius: 5px;\n            padding: 5px 10px 5px 10px;\n            color: %s;\n            }\n            QPushButton:hover {\n            color: %s;\n            }\n            QPushButton:focus {\n            color: %s;\n            }\n            ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_HIGH_HIGH_COLOR.name(), LPGlobalUI.THEME_HIGH_COLOR.name()))
            box.setDefaultButton(QMessageBox.StandardButton.Yes)
            select = box.exec()
            if select == QMessageBox.StandardButton.Yes:
                self.removePresetItemMethod(item)

        deleteActionText = QCoreApplication.translate('Preset', 'Delete')
        deleteAction = menu.addAction(deleteActionText, _showDeleteConfirm)
        menu.exec(self.presetListWidget.viewport().mapToGlobal(pos))

    
    def removePresetItemMethod(self, item):
        
        def finishedMethod(response = None):
            if response.get('status_code', None) == 200:
                logger.debug(f'''preset delete index:{item.index} success''')
            else:
                logger.debug(f'''preset delete index:{item.index} failed''')

        index = item.index
        item.name = None
        item.source = None
        item.picUrl = None
        self.updateUISignal.emit()
        itemToReplace = self.xmlObj.find('Key' + str(index))
        itemToReplace.clear()
        replaceXml = '<RoutineId>Empty</RoutineId>'
        wrappedXML = f'''<container>{replaceXml}</container>'''
        soup = BeautifulSoup(wrappedXML, 'xml')
        container = soup.find('container')
        contents = container.contents
        for content in contents:
            itemToReplace.append(copy.copy(content))
        setKeyMappingXml = str(self.xmlObj)
        LPGlobalUI.currentDevice.asyncUpnpPost('SetKeyMapping', {
            'QueueContext': setKeyMappingXml }, finishedMethod)

    
    def viewWillAppear(self):
        self.updateUI(LPGlobalUI.currentDevice)

    
    def viewWillDisappear(self):
        pass

    
    def _fetchPresetList(self):
        
        def _parseXML(response = None):
            if response.get('error', None) is not None:
                self.status = LPPresetViewControllerState.error
                self.updateUISignal.emit()
                return None
            xmlStr = None.get('xml', None)
            self.presetList = []
            self.xmlObj = BeautifulSoup(xmlStr, 'xml')
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
            self.status = LPPresetViewControllerState.ready
            self.updateUISignal.emit()

        if LPGlobalUI.currentDevice is None or LPGlobalUI.currentDevice.presetNum == 0:
            self.status = LPPresetViewControllerState.notSupport
            self.updateUISignal.emit()
            return None
        None.currentDevice.asyncUpnpPost('GetKeyMapping', { }, _parseXML)

    
    def updateUI(self, device):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            self._fetchPresetList()

    
    def itemClickMethod(self, item):
        response = LPGlobalUI.currentDevice.commonHttpGet('MCUKeyShortClick:%d' % item.index)

    
    def _updateUI(self):
        if self.status == LPPresetViewControllerState.error:
            self.noteLabel.setText(QCoreApplication.translate('Preset', 'Loading error'))
            self.stackedWidget.setCurrentIndex(1)
        elif self.status == LPPresetViewControllerState.notReady:
            self.noteLabel.setText(QCoreApplication.translate('Preset', 'Loading'))
            self.stackedWidget.setCurrentIndex(1)
        elif self.status == LPPresetViewControllerState.notSupport:
            self.noteLabel.setText(QCoreApplication.translate('Preset', "Current device doesn't support preset"))
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.presetListWidget.clear()
            for item in self.presetList:
                widgetItem = QListWidgetItem()
                widget = LPGlobalUI.loadUI(LPUIPath.LPPresetItemCardUI, Ui_PresetItemCard, LPPresetItemCard)
                widget.item = item
                widgetItem.setSizeHint(widget.sizeHint())
                widget.indexLabel.setText('')
                if item.name is not None:
                    widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    text = f'''{item.index} {item.name.split('_#~')[0]}'''
                    metrics = QtGui.QFontMetrics(widget.nameLabel.font())
                    textElided = metrics.elidedText(text, Qt.TextElideMode.ElideRight, widget.nameLabel.size().width())
                    widget.nameLabel.setText(textElided)
                    widget.nameLabel.setToolTip(text)
                    widget.nameLabel.setStyleSheet('\n                            QLabel {\n                                color: %s;\n                            }\n                            QToolTip {\n                                background-color: white;\n                                color: %s;\n                            }                          \n                        ' % (LPGlobalUI.THEME_DEFAULT_COLOR.name(), LPGlobalUI.THEME_DISABLE_COLOR.name()))
                    widget.updateImage(item.picUrl)
                    widget.clickMethod = self.itemClickMethod
                else:
                    widget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                    widget.nameLabel.setText(QCoreApplication.translate('Preset', '%d Empty') % item.index)
                    widget.smallSourceFrame.hide()
                self.presetListWidget.addItem(widgetItem)
                self.presetListWidget.setItemWidget(widgetItem, widget)

    __classcell__ = None

