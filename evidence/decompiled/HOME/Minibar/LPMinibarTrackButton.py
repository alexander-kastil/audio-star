# Source Generated with Decompyle++
# File: LPMinibarTrackButton.pyc (Python 3.9)

'''
@Time ： 2025/10/31 14:01
@Auth ： Chris
@File ：LPMinibarTrackButton.py
@Desc:
'''
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from LPCommonWidgets.button.LPElideButton import LPElideButton

class LPMinibarTrackButton(LPElideButton):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)

    
    def _updateElidedText(self = None):
        metrics = QFontMetrics(self.font())
        textWidth = metrics.horizontalAdvance(self.full_text)
        parentWidget = self.parentWidget()
        availableWidth = parentWidget.width() - 20 - 20 - 7
        elided = metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, availableWidth)
        super(QPushButton, self).setText(elided)

    __classcell__ = None

