# Source Generated with Decompyle++
# File: LPLoadingOverlay_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_loadingOverlay(object):
    
    def setupUi(self, loadingOverlay):
        loadingOverlay.setObjectName('loadingOverlay')
        loadingOverlay.resize(698, 669)
        loadingOverlay.setStyleSheet('border:none;')
        self.verticalLayout = QtWidgets.QVBoxLayout(loadingOverlay)
        self.verticalLayout.setObjectName('verticalLayout')
        self.mainFrame = QtWidgets.QFrame(loadingOverlay)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.mainFrame)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.spinnerLabel = QtWidgets.QLabel(self.mainFrame)
        self.spinnerLabel.setText('')
        self.spinnerLabel.setObjectName('spinnerLabel')
        self.horizontalLayout.addWidget(self.spinnerLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout.addWidget(self.mainFrame)
        self.retranslateUi(loadingOverlay)
        QtCore.QMetaObject.connectSlotsByName(loadingOverlay)

    
    def retranslateUi(self, loadingOverlay):
        _translate = QtCore.QCoreApplication.translate
        loadingOverlay.setWindowTitle(_translate('loadingOverlay', 'Form'))


