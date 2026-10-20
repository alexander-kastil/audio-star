# Source Generated with Decompyle++
# File: LPSuperComboBox.pyc (Python 3.9)

import LPGlobalUI
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QEvent
import threading
from LPClientFramework.LPConfig.LPFontConfig import getApplicationFont
GroupRole = QtCore.Qt.ItemDataRole.UserRole
extraRole = GroupRole + 1

class LPSuperComboBox(QComboBox):
    
    def __init__(self = None, parent = None):
        super(LPSuperComboBox, self).__init__(parent)
        self.installEventFilter(self)

    
    def eventFilter(self = None, obj = None, event = None):
        if event.type() == QEvent.Type.Wheel:
            return True
        return None(LPSuperComboBox, self).eventFilter(obj, event)

    
    def setCurrentText(self = None, text = None):
        super().setCurrentText(text)
        self.startEditText = text

    
    def setupUI(self):
        self.setStyleSheet('\n        QComboBox { \n        background-color: %s; \n        color: white; \n        border-radius: 5px; \n        padding-left: 10px;\n        padding-right: 10px;\n        combobox-popup: 0;\n        }\n\n        QComboBox::drop-down { \n        border: 0px;\n        }\n\n        QComboBox QAbstractItemView {\n        background-color: %s; \n        padding-bottom: 5px;\n        min-height: 30px;\n        min-width: 100px;\n        border-bottom-right-radius: 10px;\n        border-bottom-left-radius: 10px;\n        selection-background-color: %s;\n        }\n\n        QComboBox QAbstractItemView::item {\n        min-height: 30px;\n        color: rgb(255, 255, 255);\n        }\n\n        QComboBox::down-arrow {\n        image: url("%s");\n        width: 14px;\n        height: 14px;\n        padding-right: 10px;\n        }\n        QScrollBar {\n        border: 0px;\n        background: %s;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle {\n        background: %s;\n        min-height: 0px;\n\tborder-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        border: 0px;\n}\n        ' % (LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name(), LPGlobalUI.imagePath('arrow_down.png'), LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name(), LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name()))
        self.view().window().setWindowFlags(QtCore.Qt.WindowType.Popup | QtCore.Qt.WindowType.NoDropShadowWindowHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.view().window().setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    
    def restoreText(self):
        self.setCurrentText(self.startEditText)

    __classcell__ = None


class LPGroupComboBoxDelegate(QStyledItemDelegate):
    
    def initStyleOption(self = None, option = None, index = None):
        super(LPGroupComboBoxDelegate, self).initStyleOption(option, index)
        if not index.data(GroupRole):
            option.text = '   ' + option.text

    __classcell__ = None


class LPGroupComboBoxItem(QtGui.QStandardItem):
    
    def __init__(self = None, text = None):
        super(LPGroupComboBoxItem, self).__init__(text)
        self.setData(True, GroupRole)
        self._number_of_childrens = 0
        font = getApplicationFont()
        font.setPointSize(12)
        font.setWeight(QtGui.QFont.Weight.Light)
        self.setFont(font)
        self.setFlags(self.flags() & ~(QtCore.Qt.ItemFlag.ItemIsSelectable))
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 255))
        self.setForeground(brush)

    
    def addChild(self, text, extraData = (None,)):
        it = QtGui.QStandardItem(text)
        it.setData(False, GroupRole)
        if extraData is not None:
            it.setData(extraData, extraRole)
        self._number_of_childrens += 1
        self.model().insertRow(self.row() + self._number_of_childrens, it)
        return it

    __classcell__ = None


class LPGroupComboBox(LPSuperComboBox):
    
    def __init__(self = None, parent = None):
        super(LPGroupComboBox, self).__init__(parent)
        self.setModel(QtGui.QStandardItemModel(self))
        delegate = LPGroupComboBoxDelegate(self)
        self.setItemDelegate(delegate)

    
    def addGroup(self, text):
        it = LPGroupComboBoxItem(text)
        self.model().appendRow(it)
        return it

    
    def addChild(self, text):
        it = QtGui.QStandardItem(text)
        it.setData(True, GroupRole)
        self.model().appendRow(it)

    __classcell__ = None

