# Source Generated with Decompyle++
# File: LPLineEdit.pyc (Python 3.9)

'''
@Time ： 2025/8/28 17:28
@Auth ： Chris
@File ：LPLineEdit.py
@Desc:
'''
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import pyqtProperty, QEvent

class LPLineEdit(QLineEdit):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self._placeholder_color = QColor('gray')

    
    def getPlaceholderColor(self):
        return self._placeholder_color

    
    def setPlaceholderColor(self, color):
        if self._placeholder_color != color:
            self._placeholder_color = color
            self._updatePalette()

    placeholderColor = pyqtProperty(QColor, getPlaceholderColor, setPlaceholderColor, **('fget', 'fset'))
    
    def _updatePalette(self):
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, self._placeholder_color)
        self.setPalette(pal)

    
    def event(self = None, ev = None):
        if ev.type() == QEvent.Type.PaletteChange:
            pal = self.palette()
            if pal.color(QPalette.ColorRole.PlaceholderText) != self._placeholder_color:
                pal.setColor(QPalette.ColorRole.PlaceholderText, self._placeholder_color)
                self.setPalette(pal)
        return super().event(ev)

    __classcell__ = None

