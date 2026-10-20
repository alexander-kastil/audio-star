# Source Generated with Decompyle++
# File: LPMS4xxErrorPage_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MS4xxErrorWidget(object):
    
    def setupUi(self, MS4xxErrorWidget):
        MS4xxErrorWidget.setObjectName('MS4xxErrorWidget')
        MS4xxErrorWidget.resize(757, 590)
        self.verticalLayout = QtWidgets.QVBoxLayout(MS4xxErrorWidget)
        self.verticalLayout.setObjectName('verticalLayout')
        self.mainFrame = QtWidgets.QFrame(MS4xxErrorWidget)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        spacerItem = QtWidgets.QSpacerItem(20, 215, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.statusCodeLabel = QtWidgets.QLabel(self.mainFrame)
        self.statusCodeLabel.setText('')
        self.statusCodeLabel.setObjectName('statusCodeLabel')
        self.verticalLayout_2.addWidget(self.statusCodeLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.noteLabel = QtWidgets.QLabel(self.mainFrame)
        self.noteLabel.setText('')
        self.noteLabel.setObjectName('noteLabel')
        self.verticalLayout_2.addWidget(self.noteLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        spacerItem2 = QtWidgets.QSpacerItem(20, 214, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addWidget(self.mainFrame)
        self.retranslateUi(MS4xxErrorWidget)
        QtCore.QMetaObject.connectSlotsByName(MS4xxErrorWidget)

    
    def retranslateUi(self, MS4xxErrorWidget):
        _translate = QtCore.QCoreApplication.translate
        MS4xxErrorWidget.setWindowTitle(_translate('MS4xxErrorWidget', 'Form'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MS4xxErrorWidget = QtWidgets.QWidget()
    ui = Ui_MS4xxErrorWidget()
    ui.setupUi(MS4xxErrorWidget)
    MS4xxErrorWidget.show()
    sys.exit(app.exec())
