# Source Generated with Decompyle++
# File: LPTooTipElideButton.pyc (Python 3.9)

'''
@Time ： 2026/1/28 17:24
@Auth ： Chris
@File ：LPToolTipElideButton.py
@Desc:
'''
from PyQt6.QtCore import QEvent, QRect, Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QToolTip, QPushButton
from LPCommonWidgets.button.LPElideButton import LPElideButton

class LPToolTipElideButton(LPElideButton):
    
    def _updateElidedText(self = None):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, self.width())
        super(QPushButton, self).setText(elided)

    
    def event(self = None, event = None):
        if event.type() == QEvent.Type.ToolTip:
            help_event = event
            fm = QFontMetrics(self.font())
            text_width = fm.horizontalAdvance(self.full_text)
            text_rect = QRect(0, 0, text_width, self.height())
            if text_rect.contains(help_event.pos()):
                QToolTip.showText(help_event.globalPos(), self.full_text, self)
            else:
                QToolTip.hideText()
            return True
        return None().event(event)

    __classcell__ = None

