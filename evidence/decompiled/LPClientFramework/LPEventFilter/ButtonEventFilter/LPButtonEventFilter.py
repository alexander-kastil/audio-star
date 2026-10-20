# Source Generated with Decompyle++
# File: LPButtonEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QEvent, QSize
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPButtonEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, widget = None, defaultImage = None, hoverImage = None, pressImage = None, effect = None, tipStr = None):
        super().__init__(widget)
        self.effect = effect if effect else 'bigger'
        self.button = widget
        self.tipStr = tipStr
        if self.button.underMouse() and hoverImage:
            self.button.setIcon(hoverImage)
        else:
            self.button.setIcon(defaultImage)
        self.defaultImage = defaultImage
        self.hoverImage = hoverImage
        self.pressImage = pressImage
        if tipStr is not None:
            self.button.setToolTip(tipStr)

    
    def eventFilter(self = None, obj = None, event = None):
        if self.button.isEnabled():
            if event.type() == QEvent.Type.Enter:
                if self.effect == 'bigger':
                    self.button.setIconSize(QSize(self.button.iconSize().width() + 2, self.button.iconSize().height() + 2))
                elif self.effect == 'image':
                    self.button.setIcon(self.hoverImage)
                return True
            if None.type() == QEvent.Type.Leave:
                if self.effect == 'bigger':
                    self.button.setIconSize(QSize(self.button.iconSize().width() - 2, self.button.iconSize().height() - 2))
                elif self.effect == 'image':
                    self.button.setIcon(self.defaultImage)
                return True
            if None.type() == QEvent.Type.MouseButtonPress or self.pressImage:
                self.button.setIcon(self.pressImage)
            elif event.type() == QEvent.Type.MouseButtonRelease and self.hoverImage:
                self.button.setIcon(self.hoverImage)
        return super(LPButtonEventFilter, self).eventFilter(obj, event)

    __classcell__ = None

