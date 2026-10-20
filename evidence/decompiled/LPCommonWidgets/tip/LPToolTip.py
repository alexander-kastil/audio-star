# Source Generated with Decompyle++
# File: LPToolTip.pyc (Python 3.9)

'''
@Time ： 2025/5/12 18:13
@Auth ： Chris
@File ：LPToolTip.py
@Desc:
'''
import platform
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget

class LPToolTip(QWidget):
    
    def __init__(self = None, text = None, parent = None):
        super().__init__(parent)
        self.text = text
        self._use_painted_shadow = False

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if platform.system() == 'Darwin':
            pass
        self._use_painted_shadow = platform.machine().lower() in ('arm64', 'aarch64')
        self.setStyleSheet('\n            QWidget{\n                border-radius: 12px;\n            }\n            QFrame#mainFrame{\n                background-color: #282828;\n                border-radius: 12px;\n                color: rgba(255, 255, 255, 166);\n                border: none;\n            }\n            QLabel{\n                color: rgba(255, 255, 255, 166);\n            }\n            QPushButton#closeButton{\n                background-color: transparent;\n                border: none;\n            }\n            ')
        self.closeButton.setIcon(QIcon(':/images/dialog_close.png'))
        self.closeButton.clicked.connect(self.hide)
        self.textLabel.setContentsMargins(0, 12, 20, 0)
        self.textLabel.setTextFormat(Qt.TextFormat.RichText)
        self.textLabel.setText(self.text)
        self.textLabel.setWordWrap(True)
        if hasattr(self, 'verticalLayout'):
            self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.setContentsMargins(0, 0, 0, 0)
        if not self._use_painted_shadow:
            shadowEffect = QGraphicsDropShadowEffect(self.mainFrame)
            shadowEffect.setBlurRadius(20)
            shadowEffect.setOffset(0, 5)
            shadowEffect.setColor(QColor(0, 0, 0, 217))
            self.mainFrame.setGraphicsEffect(shadowEffect)

    
    def paintEvent(self = None, event = None):
        super().paintEvent(event)
        if not self._use_painted_shadow or hasattr(self, 'mainFrame'):
            return None
        rect = None.mainFrame.geometry()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        for expand, alpha in ((0, 44), (2, 30), (4, 20), (6, 12)):
            shadow_rect = rect.adjusted(-expand, -expand, expand, expand).translated(0, 3)
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawRoundedRect(shadow_rect, 12 + expand, 12 + expand)

    __classcell__ = None

