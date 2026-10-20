# Source Generated with Decompyle++
# File: LPDialog.pyc (Python 3.9)

'''
@Time ： 2024/12/2 17:26
@Auth ： Chris
@File ：LPDialog.py
@Desc:
'''
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

class LPDialog(QDialog):
    
    def __init__(self = None, title = None, content = None, yes_text = None, no_text = None, parent = None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.yes_text = yes_text
        self.no_text = no_text
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet('\n            QDialog {\n                background-color: #121212;\n                color: #FFFFFF;\n                border-radius: none;\n            }\n            QLabel {\n                font-size: 16px;\n                color: #FFFFFF;\n                background-color: #121212;\n            }\n            QPushButton {\n                padding: 8px 16px;\n                font-size: 14px;\n                border-radius: 4px;\n            }\n            QPushButton#deleteButton {\n                background-color: #E53935;\n                color: white;\n            }\n            QPushButton#deleteButton:hover {\n                background-color: #D32F2F;\n            }\n            QPushButton#cancelButton {\n                background-color: #2E2E2E;\n                color: white;\n            }\n            QPushButton#cancelButton:hover {\n                background-color: #3E3E3E;\n            }\n            ')
        radius = 10
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        self.init_widgets()

    
    def init_widgets(self):
        layout = QVBoxLayout(self)
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        layout.addWidget(self.title_label, Qt.AlignmentFlag.AlignCenter, **('alignment',))
        self.description_label = QLabel(self.content)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.description_label)
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton(self.no_text)
        self.cancel_button.setObjectName('cancelButton')
        self.delete_button = QPushButton(self.yes_text)
        self.delete_button.setObjectName('deleteButton')
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)
        self.cancel_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self.accept)

    __classcell__ = None

