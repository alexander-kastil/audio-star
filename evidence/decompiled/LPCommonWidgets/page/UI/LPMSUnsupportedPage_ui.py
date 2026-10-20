# Source Generated with Decompyle++
# File: LPMSUnsupportedPage_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MSUnsupportedWidget(object):
    
    def setupUi(self, MSUnsupportedWidget):
        MSUnsupportedWidget.setObjectName('MSUnsupportedWidget')
        MSUnsupportedWidget.resize(757, 590)
        self.verticalLayout = QtWidgets.QVBoxLayout(MSUnsupportedWidget)
        self.verticalLayout.setObjectName('verticalLayout')
        self.mainFrame = QtWidgets.QFrame(MSUnsupportedWidget)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.mainFrame)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.noteLabel = QtWidgets.QLabel(self.mainFrame)
        self.noteLabel.setText('')
        self.noteLabel.setObjectName('noteLabel')
        self.horizontalLayout.addWidget(self.noteLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout.addWidget(self.mainFrame)
        self.retranslateUi(MSUnsupportedWidget)
        QtCore.QMetaObject.connectSlotsByName(MSUnsupportedWidget)

    
    def retranslateUi(self, MSUnsupportedWidget):
        _translate = QtCore.QCoreApplication.translate
        MSUnsupportedWidget.setWindowTitle(_translate('MSUnsupportedWidget', 'Form'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MSUnsupportedWidget = QtWidgets.QWidget()
    ui = Ui_MSUnsupportedWidget()
    ui.setupUi(MSUnsupportedWidget)
    MSUnsupportedWidget.show()
    sys.exit(app.exec())
