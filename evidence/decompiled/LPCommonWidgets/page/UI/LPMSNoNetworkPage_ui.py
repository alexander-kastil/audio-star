# Source Generated with Decompyle++
# File: LPMSNoNetworkPage_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MSNoNetworkWidget(object):
    
    def setupUi(self, MSNoNetworkWidget):
        MSNoNetworkWidget.setObjectName('MSNoNetworkWidget')
        MSNoNetworkWidget.resize(757, 590)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(MSNoNetworkWidget)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.mainFrame = QtWidgets.QFrame(MSNoNetworkWidget)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout.setObjectName('verticalLayout')
        spacerItem = QtWidgets.QSpacerItem(20, 215, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.noteLabel = QtWidgets.QLabel(self.mainFrame)
        self.noteLabel.setText('')
        self.noteLabel.setObjectName('noteLabel')
        self.verticalLayout.addWidget(self.noteLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.retryButton = QtWidgets.QPushButton(self.mainFrame)
        self.retryButton.setMinimumSize(QtCore.QSize(100, 0))
        self.retryButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.retryButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.retryButton.setObjectName('retryButton')
        self.verticalLayout.addWidget(self.retryButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 214, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.mainFrame)
        self.retranslateUi(MSNoNetworkWidget)
        QtCore.QMetaObject.connectSlotsByName(MSNoNetworkWidget)

    
    def retranslateUi(self, MSNoNetworkWidget):
        _translate = QtCore.QCoreApplication.translate
        MSNoNetworkWidget.setWindowTitle(_translate('MSNoNetworkWidget', 'Form'))
        self.retryButton.setText(_translate('MSNoNetworkWidget', 'Try again'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MSNoNetworkWidget = QtWidgets.QWidget()
    ui = Ui_MSNoNetworkWidget()
    ui.setupUi(MSNoNetworkWidget)
    MSNoNetworkWidget.show()
    sys.exit(app.exec())
