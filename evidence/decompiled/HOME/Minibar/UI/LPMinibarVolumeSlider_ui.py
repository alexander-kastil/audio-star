# Source Generated with Decompyle++
# File: LPMinibarVolumeSlider_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_volumeSliderWidget(object):
    
    def setupUi(self, volumeSliderWidget):
        volumeSliderWidget.setObjectName('volumeSliderWidget')
        volumeSliderWidget.resize(94, 150)
        volumeSliderWidget.setMinimumSize(QtCore.QSize(40, 150))
        volumeSliderWidget.setMaximumSize(QtCore.QSize(94, 150))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(volumeSliderWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.mainFrame = QtWidgets.QFrame(volumeSliderWidget)
        self.mainFrame.setMinimumSize(QtCore.QSize(40, 0))
        self.mainFrame.setMaximumSize(QtCore.QSize(40, 16777215))
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName('verticalLayout')
        self.volumeSlider = LPVolumeSlider(self.mainFrame)
        self.volumeSlider.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.volumeSlider.setObjectName('volumeSlider')
        self.verticalLayout.addWidget(self.volumeSlider, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.verticalLayout_2.addWidget(self.mainFrame, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.retranslateUi(volumeSliderWidget)
        QtCore.QMetaObject.connectSlotsByName(volumeSliderWidget)

    
    def retranslateUi(self, volumeSliderWidget):
        _translate = QtCore.QCoreApplication.translate
        volumeSliderWidget.setWindowTitle(_translate('volumeSliderWidget', 'Form'))


from HOME.LPVolumeSlider import LPVolumeSlider
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    volumeSliderWidget = QtWidgets.QWidget()
    ui = Ui_volumeSliderWidget()
    ui.setupUi(volumeSliderWidget)
    volumeSliderWidget.show()
    sys.exit(app.exec())
