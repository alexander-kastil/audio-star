# Source Generated with Decompyle++
# File: LPBadgeButtonEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QEvent, QSize
from PyQt6.QtWidgets import QPushButton, QToolButton
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPBadgeButtonEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, widget = None, defaultImage = None, hoverImage = None, pressImage = None, tipStr = None):
        super().__init__(widget)
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
                self.button.setIcon(self.hoverImage)
                if hasattr(self.button, 'badge') and isinstance(self.button.badge, QToolButton) and self.button.badge.isVisible() and hasattr(self.button.badge, 'hoverImage'):
                    badgeHoverImage = self.button.badge.hoverImage
                    if badgeHoverImage:
                        self.button.badge.setIcon(badgeHoverImage)
                return True
            if None.type() == QEvent.Type.Leave:
                self.button.setIcon(self.defaultImage)
                if hasattr(self.button, 'badge') and isinstance(self.button.badge, QToolButton) and self.button.badge.isVisible() and hasattr(self.button.badge, 'defaultImage'):
                    badgeDefaultImage = self.button.badge.defaultImage
                    if badgeDefaultImage:
                        self.button.badge.setIcon(badgeDefaultImage)
                return True
            if None.type() == QEvent.Type.MouseButtonPress or self.pressImage:
                self.button.setIcon(self.pressImage)
                if hasattr(self.button, 'badge') and isinstance(self.button.badge, QToolButton) and self.button.badge.isVisible() and hasattr(self.button.badge, 'pressImage'):
                    badgePressImage = self.button.badge.pressImage
                    if badgePressImage:
                        self.button.badge.setIcon(badgePressImage)
                    elif event.type() == QEvent.Type.MouseButtonRelease and self.hoverImage:
                        self.button.setIcon(self.hoverImage)
                        if hasattr(self.button, 'badge') and isinstance(self.button.badge, QToolButton) and self.button.badge.isVisible() and hasattr(self.button.badge, 'hoverImage'):
                            badgeHoverImage = self.button.badge.hoverImage
                            if badgeHoverImage:
                                self.button.badge.setIcon(badgeHoverImage)
        return super().eventFilter(obj, event)

    __classcell__ = None

