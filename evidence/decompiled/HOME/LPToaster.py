# Source Generated with Decompyle++
# File: LPToaster.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import Main_Text, getApplicationFont

class LPToaster(QtWidgets.QFrame):
    closed = QtCore.pyqtSignal()
    _sharedToaster = None
    
    def __init__(self = None, *args, **kwargs):
        pass
    # WARNING: Decompyle incomplete

    
    def checkClosed(self):
        if self.opacityAni.direction() == self.opacityAni.Direction.Backward:
            self.close()

    
    def restore(self):
        self.timer.stop()
        self.opacityAni.stop()
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    
    def hide(self = None):
        self.timer.stop()
        self.opacityAni.stop()
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)
        super(LPToaster, self).hide()

    
    def _setAnchorWidget(self, anchorWidget):
        '''
        设置 toast 的定位参考控件。

        Args:
            anchorWidget: 用于计算 toast 居中位置的 QWidget。
        '''
        if self.anchorWidget is anchorWidget:
            return None
    # WARNING: Decompyle incomplete

    
    def _anchorGeometry(self):
        '''
        获取定位参考区域。

        Returns:
            全局坐标系下的 QRect，用于计算 toast 居中位置。
        '''
        anchorWidget = self.anchorWidget
        if anchorWidget is None:
            anchorWidget = getattr(LPGlobalUI, 'mainWindow', None)
    # WARNING: Decompyle incomplete

    
    def _moveToAnchorPosition(self):
        parentRect = self._anchorGeometry()
        if not parentRect.isValid():
            return None
        geo = None.geometry()
        if self.corner == QtCore.Qt.Corner.TopLeftCorner:
            geo.moveTopLeft(parentRect.topLeft() + QtCore.QPoint(self.margin, self.margin))
        elif self.corner == QtCore.Qt.Corner.TopRightCorner:
            geo.moveTopRight(parentRect.topRight() + QtCore.QPoint(-(self.margin), self.margin))
        elif self.corner == QtCore.Qt.Corner.BottomRightCorner:
            geo.moveBottomRight(parentRect.bottomRight() + QtCore.QPoint(-(self.margin), -(self.margin)))
        elif self.corner == QtCore.Qt.Corner.BottomLeftCorner:
            geo.moveBottomLeft(parentRect.bottomLeft() + QtCore.QPoint(self.margin, -(self.margin)))
        else:
            bottomLeft = parentRect.bottomLeft()
            bottomLeft.setX(int(bottomLeft.x() + parentRect.width() / 2 - self.width() / 2))
            geo.moveBottomLeft(bottomLeft + QtCore.QPoint(0, -(self.margin)))
        self.setGeometry(geo)

    
    def _raiseAboveAppWindows(self):
        if not self.isVisible():
            return None
        None.raise_()

    
    def eventFilter(self = None, source = None, event = None):
        anchorWidget = self.anchorWidget if self.anchorWidget is not None else self.parent()
        if source == anchorWidget and event.type() in (QtCore.QEvent.Type.Resize, QtCore.QEvent.Type.Move, QtCore.QEvent.Type.Show):
            self.opacityAni.stop()
            self._moveToAnchorPosition()
        return super(LPToaster, self).eventFilter(source, event)

    
    def closeEvent(self = None, event = None):
        pass
    # WARNING: Decompyle incomplete

    
    def resizeEvent(self = None, event = None):
        super(LPToaster, self).resizeEvent(event)
        if not self.parent():
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()).translated(-0.5, -0.5), 4, 4)
            self.setMask(QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon()))
        else:
            self.clearMask()

    
    def showMessage(parent, message, icon, corner, margin, closable, timeout, desktop, parentWindow = (QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation, QtCore.Qt.Corner.TopLeftCorner, 10, False, 2000, False, True)):
        if parent and parentWindow:
            parent = parent.window()
        if LPToaster._sharedToaster is None:
            LPToaster._sharedToaster = LPToaster(None)
            LPToaster._sharedToaster._LPToaster__self = LPToaster._sharedToaster
            LPToaster._sharedToaster.setWindowFlags(QtCore.Qt.WindowType.Tool | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
            LPToaster._sharedToaster.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self = LPToaster._sharedToaster
        self._setAnchorWidget(None if desktop else parent)
        self.timer.setInterval(timeout)
        if not message:
            pass
        self.label.setText(str(''))
        if closable:
            if self.closeButton is None:
                self.closeButton = QtWidgets.QToolButton()
                self.layout().addWidget(self.closeButton)
                self.closeButton.clicked.connect(self.hide)
            closeIcon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton)
            self.closeButton.setIcon(closeIcon)
            self.closeButton.setAutoRaise(True)
            self.closeButton.show()
        elif self.closeButton is not None:
            self.closeButton.hide()
        self.timer.stop()
        self.timer.start()
        self.adjustSize()
        self.corner = corner
        self.margin = margin
        self._moveToAnchorPosition()
        self.opacityAni.stop()
        self.setWindowOpacity(1)
        self.show()
        self._raiseAboveAppWindows()

    showMessage = staticmethod(showMessage)
    __classcell__ = None


class W(QtWidgets.QWidget):
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)
        toasterLayout = QtWidgets.QHBoxLayout()
        layout.addLayout(toasterLayout)
        self.textEdit = QtWidgets.QLineEdit('Request resource timeout')
        toasterLayout.addWidget(self.textEdit)
        self.cornerCombo = QtWidgets.QComboBox()
        toasterLayout.addWidget(self.cornerCombo)
        for pos in ('TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'):
            corner = getattr(QtCore.Qt.Corner, '{}Corner'.format(pos))
            self.cornerCombo.addItem(pos, corner)
        self.windowBtn = QtWidgets.QPushButton('Show window toaster')
        toasterLayout.addWidget(self.windowBtn)
        self.windowBtn.clicked.connect(self.showToaster)
        self.screenBtn = QtWidgets.QPushButton('Show desktop toaster')
        toasterLayout.addWidget(self.screenBtn)
        self.screenBtn.clicked.connect(self.showToaster)
        layout.addWidget(QtWidgets.QTableView())

    
    def showToaster(self):
        if self.sender() == self.windowBtn:
            parent = self
            desktop = False
        else:
            parent = None
            desktop = True
        corner = QtCore.Qt.Corner(self.cornerCombo.currentData())
        LPToaster.showMessage(parent, self.textEdit.text(), None, desktop, **('corner', 'desktop'))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = W()
    w.show()
    sys.exit(app.exec())
