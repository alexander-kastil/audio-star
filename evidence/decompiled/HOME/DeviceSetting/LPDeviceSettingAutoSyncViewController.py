# Source Generated with Decompyle++
# File: LPDeviceSettingAutoSyncViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtWidgets import QWidget, QDialog, QGraphicsBlurEffect
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt6.QtGui import QPainter, QColor, QIcon
from enum import Enum
import LPGlobalUI
from HOME.LPWaitingSpinner import LPWaitingSpinner
from LPClientFramework.LPConfig.LPFontConfig import DEFAULT

class LPDeviceSettingAutoSyncViewController(QWidget):
    updateUISignal = pyqtSignal(object, object)
    
    def __init__(self = None):
        super(LPDeviceSettingAutoSyncViewController, self).__init__()
        self.loadingSpinner = None
        self.updateUISignal.connect(self._updateUI)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setStyleSheet('\n        QFrame#contentFrame{\n        background-color: rgba(0, 0, 0, 30)\n        }\n        ')
        self.dialogFrame.setStyleSheet('\n        QFrame#dialogFrame{\n        background-color: rgba(0, 0, 0, 255);\n        border-radius : 15;\n        border : 0px\n        }\n        ')
        self.doneButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n}        ' % LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name())
        self.doneButton.setCursor(Qt.CursorShape.PointingHandCursor)
        None((lambda : self.hide()))
        self.markFinishImageView.setIcon(QIcon(LPGlobalUI.imagePath('checkmark.png')))
        stylesheetTemplate = Template('\n                       QLabel#noteLabel {\n                           font-size: ${titeFontSize}pt;\n                       }\n               ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{DEFAULT}''', **('titeFontSize',)))

    
    def show(self = None):
        super().show()
        self.doneFrame.hide()
        self.markFinishImageView.hide()
        if self.loadingSpinner is None:
            self.loadingSpinner = LPWaitingSpinner(self.markWidget, 30, 40, 6, 50, 3, 1, 1.5, QColor(255, 255, 255), **('roundness', 'fade', 'radius', 'lines', 'line_length', 'line_width', 'speed', 'color'))
        if not self.loadingSpinner.is_spinning:
            self.loadingSpinner.show()
            self.loadingSpinner.start()

    
    def _updateUI(self, status, latency):
        if status == 0:
            self.noteLabel.setText(QCoreApplication.translate('AutoSync', "Calibrating your speaker's audio timing…"))
            self.detailLabel.setText(QCoreApplication.translate('AutoSync', 'Your speaker and app will both play a sound to match the timing.\n\nThis will take about 30 seconds.'))
            self.doneFrame.hide()
            self.markFinishImageView.hide()
        else:
            self.noteLabel.setText(QCoreApplication.translate('AutoSync', 'All done!'))
            self.detailLabel.setText(QCoreApplication.translate('AutoSync', 'Play some music to check if the audio is in sync. If some adjustment is needed, select Manually Syncing.\n\n Audio path latency: %d') % latency)
            self.doneFrame.show()
            self.markFinishImageView.show()
            if self.loadingSpinner and self.loadingSpinner.is_spinning:
                self.loadingSpinner.stop()
                self.loadingSpinner.hide()

    
    def updateDialogUI(self, status, latency):
        self.updateUISignal.emit(status, latency)

    __classcell__ = None

