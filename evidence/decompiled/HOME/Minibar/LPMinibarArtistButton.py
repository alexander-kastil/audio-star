# Source Generated with Decompyle++
# File: LPMinibarArtistButton.pyc (Python 3.9)

'''
@Time ： 2025/11/5 14:53
@Auth ： Chris
@File ：LPMinibarArtistButton.py
@Desc:
'''
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QLabel
from LPCommonWidgets.button.LPElideButton import LPElideButton

class LPMinibarArtistButton(LPElideButton):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)

    
    def _updateElidedText(self = None):
        metrics = QFontMetrics(self.font())
        textWidth = metrics.horizontalAdvance(self.full_text)
        parentWidget = self.parentWidget()
        icon = self.parentWidget().findChild(QLabel, 'msIconLabel')
        iconW = 0
        if icon:
            iconW = icon.width()
        availableWidth = parentWidget.width() - iconW - 12
        elided = metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, availableWidth)
        super(QPushButton, self).setText(elided)

    __classcell__ = None

