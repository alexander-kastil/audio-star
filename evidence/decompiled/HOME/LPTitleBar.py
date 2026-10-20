# Source Generated with Decompyle++
# File: LPTitleBar.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QPoint, Qt, QEvent, pyqtSignal
import platform
import LPGlobalUI

class LPTitleBar(QtWidgets.QFrame):
    windowStateChangeSignal = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        super(LPTitleBar, self).__init__(parent)
        self.windowStateChangeSignal.connect(self.windowChangeEvent)

    
    def windowChangeEvent(self, state):
        if state == QtCore.Qt.WindowState.WindowNoState:
            if platform.system() == 'Windows':
                self.parent.winMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('win_max.png')))
            elif platform.system() == 'Darwin':
                self.parent.macButtonFrame.setHidden(False)
            elif state == QtCore.Qt.WindowState.WindowMaximized:
                if platform.system() == 'Windows':
                    self.parent.winMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('win_max_normal.png')))
                elif platform.system() == 'Darwin':
                    self.parent.macButtonFrame.setHidden(False)
                elif state == QtCore.Qt.WindowState.WindowFullScreen and platform.system() == 'Darwin':
                    self.parent.macButtonFrame.setHidden(True)

    
    def updateByPlatForm(self, parent, winHoverColor, winCloseHoverColor = (LPGlobalUI.QSS_THEME_TABLE_HOVER_BACK_COLOR, LPGlobalUI.QSS_CLOSE_BACK_COLOR)):
        self.parent = parent
        if hasattr(self.parent, 'winLogoFrame'):
            if platform.system() == 'Darwin':
                self.parent.winLogoFrame.setHidden(True)
            else:
                self.parent.winLogoFrame.setHidden(False)
                self.parent.winLogo.setFixedSize(28, 28)
                self.parent.winLogo.setIconSize(QtCore.QSize(28, 28))
                self.parent.winLogo.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('title_wiim_logo.svg')))
        if hasattr(self.parent, 'closeButtonFrame'):
            if platform.system() == 'Darwin':
                self.parent.closeButtonFrame.layout().setContentsMargins(0, 3, 0, 0)
            else:
                self.parent.closeButtonFrame.layout().setContentsMargins(15, 3, 0, 0)
        
        def _fullscreenMethod():
            if platform.system() == 'Darwin':
                self.parent.macButtonFrame.setHidden(True)
            LPGlobalUI.mainWindow.showFullScreen()

        
        def _maxscreenMethod():
            windowState = LPGlobalUI.mainWindow.windowState()
            if not windowState & QtCore.Qt.WindowState.WindowMaximized:
                LPGlobalUI.mainWindow.showMaximized()
            else:
                LPGlobalUI.mainWindow.showNormal()

        if platform.system() == 'Darwin':
            self.parent.winButtonFrame.setHidden(True)
            self.parent.macButtonFrame.setHidden(False)
            self.parent.macMaxButton.clicked.connect(_fullscreenMethod)
            self.parent.macMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_max.png')))
            self.parent.macMinButton.clicked.connect((lambda : LPGlobalUI.mainWindow.showMinimized()))
            self.parent.macMinButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_min.png')))
            self.parent.macCloseButton.clicked.connect(self.onCloseButtonClicked)
            self.parent.macCloseButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_close.png')))
            self.parent.macButtonFrame.installEventFilter(self)
        else:
            self.parent.macButtonFrame.setHidden(True)
            self.parent.winButtonFrame.setHidden(False)
            self.parent.winMaxButton.clicked.connect(_maxscreenMethod)
            self.parent.winMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('win_max.png')))
            hoverColor = winHoverColor
            self.parent.winMaxButton.setStyleSheet('\n            QPushButton {border:none;outline:none;}\n            QPushButton:hover {\n            background-color: %s;\n            }\n            ' % hoverColor)
            self.parent.winMinButton.clicked.connect((lambda : LPGlobalUI.mainWindow.showMinimized()))
            self.parent.winMinButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('win_min.png')))
            self.parent.winMinButton.setStyleSheet('\n            QPushButton {border:none;outline:none;}\n            QPushButton:hover {\n            border:none;\n            outline:none;\n            background-color: %s;\n            }\n            ' % hoverColor)
            self.parent.winCloseButton.clicked.connect(self.onCloseButtonClicked)
            self.parent.winCloseButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('win_close.png')))
            hoverColor = winCloseHoverColor
            self.parent.winCloseButton.setStyleSheet('\n            QPushButton {border:none;outline:none;}\n            QPushButton:hover {\n            background-color: %s;\n            }' % hoverColor)
            self.parent.winButtonFrame.installEventFilter(self)

    
    def onCloseButtonClicked(self):
        if LPGlobalUI.mainWindow.enableMemoryResident:
            LPGlobalUI.mainWindow.hide()
        else:
            LPGlobalUI.mainWindow.quitApp()

    
    def mouseDoubleClickEvent(self, event):
        isMaximized = LPGlobalUI.mainWindow.windowState() & QtCore.Qt.WindowState.WindowMaximized
        if not isMaximized:
            LPGlobalUI.mainWindow.showMaximized()
        else:
            LPGlobalUI.mainWindow.showNormal()

    
    def mouseMoveEvent(self, event):
        if LPGlobalUI.mainWindow.isFullScreen():
            return None
        None.mainWindow.windowHandle().startSystemMove()

    
    def eventFilter(self = None, source = None, event = None):
        if source == self.parent.macButtonFrame:
            if event.type() == QEvent.Type.Enter:
                self.parent.macMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_max_high.png')))
                self.parent.macMinButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_min_high.png')))
                self.parent.macCloseButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_close_high.png')))
            elif event.type() == QEvent.Type.Leave:
                self.parent.macMaxButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_max.png')))
                self.parent.macMinButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_min.png')))
                self.parent.macCloseButton.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('mac_close.png')))
        return super().eventFilter(source, event)

    __classcell__ = None

