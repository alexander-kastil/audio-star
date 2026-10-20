# Source Generated with Decompyle++
# File: LPCheckableButtonEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QEvent, QSize, QTimer
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPCheckableButtonEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, widget = None, defaultImage = None, hoverImage = None, checkedImage = None, effect = None, tipStr = None):
        super().__init__(widget)
        self.effect = effect if effect else 'bigger'
        self.button = widget
        if self.button.underMouse() and hoverImage:
            self.button.setIcon(hoverImage)
        else:
            self.button.setIcon(defaultImage)
        self.defaultImage = defaultImage
        self.hoverImage = hoverImage
        self.checkedImage = checkedImage
        self._hovering = False
        self.button.setCheckable(True)
        self._checked = False
        self.button.toggled.connect(self.updateCheckIcon)

    
    def updateCheckIcon(self, checked):
        self._checked = checked
        self.updateIcon()

    
    def updateIcon(self):
        print(self.button.isChecked())
        if self.button.isChecked():
            image = self.checkedImage
        elif self._hovering:
            image = self.hoverImage
        else:
            image = self.defaultImage
        self.button.setIcon(image)

    
    def eventFilter(self = None, obj = None, event = None):
