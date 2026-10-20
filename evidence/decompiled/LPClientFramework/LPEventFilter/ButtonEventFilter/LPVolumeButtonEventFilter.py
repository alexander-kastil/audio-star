# Source Generated with Decompyle++
# File: LPVolumeButtonEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QEvent, QTimer
from PyQt6.QtWidgets import QApplication
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPVolumeButtonEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, volButton = None, volSliderController = None, defaultImage = None, hoverImage = None, pressImage = None):
        super().__init__(volButton)
        self.volButton = volButton
        self.volSliderController = volSliderController
        self.volSlider = volSliderController.volumeSlider
        self.volButton.setIcon(defaultImage)
        self.defaultImage = defaultImage
        self.hoverImage = hoverImage
        self.pressImage = pressImage
        self.volSliderController.leaveEvent = self.checkHide

    
    def eventFilter(self = None, obj = None, event = None):
        if event.type() == QEvent.Type.Enter:
            self.volSlider.enableHover(True)
            self.showSlider(event)
            self.volButton.setIcon(self.hoverImage)
            return True
        if None.type() == QEvent.Type.Leave:
            self.volSlider.enableHover(False)
            self.checkHide(event)
            self.volButton.setIcon(self.defaultImage)
            return True
        if (None.type() == QEvent.Type.Wheel or self.volSliderController.isVisible()) and self.volSlider.isEnabled():
            QApplication.sendEvent(self.volSlider, event)
        elif event.type() == QEvent.Type.MouseButtonPress or self.pressImage:
            self.volButton.setIcon(self.pressImage)
        elif event.type() == QEvent.Type.MouseButtonRelease and self.hoverImage:
            self.volButton.setIcon(self.hoverImage)
        return super(LPVolumeButtonEventFilter, self).eventFilter(obj, event)

    
    def showSlider(self, event = (None,)):
        self.volSliderController.updatePosition()
        self.volSliderController.show()

    
    def checkHide(self, event = (None,)):
        QTimer.singleShot(300, self.volSliderController._maybeHide)

    __classcell__ = None

