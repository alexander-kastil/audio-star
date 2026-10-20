# Source Generated with Decompyle++
# File: LPBaseActionListWidget.pyc (Python 3.9)

'''
@Time ： 2024/11/22 9:30
@Auth ： Chris
@File ：LPBaseActionListWidget.py
@Desc:
'''
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QListWidget, QStyledItemDelegate
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily

class BaseActionListWidget(QListWidget):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self._item_height = 28
        self.setViewportMargins(0, 6, 0, 6)
        self.setIconSize(QSize(14, 14))
        self.setMouseTracking(True)
        self.setStyleSheet('\n            QListWidget {\n                border: 1px solid rgba(255, 255, 255, 0.1);\n                border-radius: 5px;\n                background-color: rgb(43, 43, 43);\n                outline: none;\n                font-family: "%s";\n                font-size: 14px;\n            }\n            \n            QListWidget::item {\n                padding-left: 6px;\n                padding-right: 6px;\n                border-radius: 5px;\n                margin-left: 6px;\n                margin-right: 6px;\n                border: none;\n                color: white;\n            }\n            \n            QListWidget::item:hover {\n                background-color: rgba(255, 255, 255, 0.08);\n            }\n\n            MenuActionListWidget::item:selected {\n                background-color: rgba(255, 255, 255, 0.08);\n                color: white;\n            }\n\n            MenuActionListWidget::item:selected:active {\n                background-color: rgba(255, 255, 255, 0.06);\n                color: rgba(255, 255, 255, 0.7);\n            }\n        ' % getFontFamily())

    
    def insert_item(self = None, row = None, item = None):
        super().insertItem(row, item)
        self.adjustSize()

    
    def add_item(self = None, item = None):
        super().addItem(item)
        self.adjust_size()

    
    def take_item(self = None, row = None):
        item = super().takeItem(row)
        self.adjust_size()
        return item

    
    def adjust_size(self):
        size = QSize()
        for i in range(self.count()):
            _size = self.item(i).sizeHint()
            size.setWidth(max(_size.width(), size.width(), 1))
            size.setHeight(max(_size.height() + size.height(), 1))
        m = self.viewportMargins()
        size += QSize(m.left() + m.right() + 3, m.top() + m.bottom() + 3)
        self.setFixedSize(size)

    __classcell__ = None

