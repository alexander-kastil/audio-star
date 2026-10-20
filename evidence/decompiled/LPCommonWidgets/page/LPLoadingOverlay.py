# Source Generated with Decompyle++
# File: LPLoadingOverlay.pyc (Python 3.9)

'''
@Time ： 2025/8/13 14:29
@Auth ： Chris
@File ：LPLoadingOverlay.py
@Desc:
'''
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QWidget
import LPGlobalUI

class LPLoadingOverlay(QWidget):
    
    def __init__(self = None, parent = None, gifPath = None):
        super().__init__(parent)
        self.gifPath = gifPath
        self.movie = QMovie(self.gifPath)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.spinnerLabel.setMovie(self.movie)

    
    def showOverlay(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
            self.raise_()
        self.show()
        self.movie.start()

    
    def hideOverlay(self):
        self.hide()
        self.movie.stop()

    
    def resizeEvent(self = None, event = None):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    __classcell__ = None

