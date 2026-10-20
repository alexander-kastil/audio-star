# Source Generated with Decompyle++
# File: LPAboutViewController.pyc (Python 3.9)

from PyQt6.QtWidgets import QWidget, QDialog, QGraphicsBlurEffect, QApplication
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap
import LPGlobalUI
from LPClientFramework import LPUtility

class LPAboutViewController(QWidget):
    
    def __init__(self = None):
        super(LPAboutViewController, self).__init__()

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setStyleSheet('\n        QFrame#contentFrame{\n        background-color: rgba(0, 0, 0, 200)\n        }\n        ')
        self.dialogFrame.setStyleSheet('\n        QFrame#dialogFrame{\n        background-color: %s;\n        border-radius : 15;\n        border : 0px\n        }\n        ' % LPGlobalUI.THEME_ITEM_BACK_COLOR.name())
        logoPixmap = QPixmap(LPGlobalUI.imagePath('ico.png'))
        scaled = logoPixmap.scaled(self.logoImageView.width(), self.logoImageView.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logoImageView.setPixmap(scaled)
        self.titleLabel.setStyleSheet('QLabel {color: %s;}' % LPGlobalUI.THEME_DEFAULT_COLOR.name())
        self.versionLabel.setStyleSheet('QLabel {color: %s;}' % LPGlobalUI.THEME_DEFAULT_COLOR.name())
        self.descLabel.setStyleSheet('QLabel {color: %s;}' % LPGlobalUI.THEME_DEFAULT_COLOR.name())
        self.closeButton.setIcon(QIcon(LPGlobalUI.imagePath('win_close.png')))
        self.closeButton.setCursor(Qt.CursorShape.PointingHandCursor)
        None((lambda : self.hide()))
        datetime = datetime
        import datetime
        releaseTime = datetime.strptime(LPUtility.appRelease, '%Y-%m-%d %H:%M:%S')
        releaseDateStr = datetime.strftime(releaseTime, '%Y-%m-%d')
        self.versionLabel.setText('Version %s (%s)' % (QApplication.applicationVersion(), releaseDateStr))
        self.descLabel.setText('© %d Linkplay Technology Inc.' % releaseTime.year)

    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.deleteLater()

    
    def mousePressEvent(self = None, event = None):
        super().mousePressEvent(event)
        if not self.dialogFrame.underMouse():
            self.hide()
            self.deleteLater()

    
    def show(self = None):
        super().show()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    __classcell__ = None

