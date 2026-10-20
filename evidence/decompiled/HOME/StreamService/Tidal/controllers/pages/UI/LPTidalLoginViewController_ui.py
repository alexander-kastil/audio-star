# Source Generated with Decompyle++
# File: LPTidalLoginViewController_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_tidalLoginWidget(object):
    
    def setupUi(self, tidalLoginWidget):
        tidalLoginWidget.setObjectName('tidalLoginWidget')
        tidalLoginWidget.resize(924, 657)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(tidalLoginWidget)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.frame = QtWidgets.QFrame(tidalLoginWidget)
        self.frame.setStyleSheet('border: none')
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName('frame')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName('verticalLayout')
        spacerItem = QtWidgets.QSpacerItem(20, 273, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.tidalLabel = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tidalLabel.sizePolicy().hasHeightForWidth())
        self.tidalLabel.setSizePolicy(sizePolicy)
        self.tidalLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.tidalLabel.setObjectName('tidalLabel')
        self.verticalLayout.addWidget(self.tidalLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.tipLabel = QtWidgets.QLabel(self.frame)
        self.tipLabel.setObjectName('tipLabel')
        self.verticalLayout.addWidget(self.tipLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.loginButton = QtWidgets.QPushButton(self.frame)
        self.loginButton.setMinimumSize(QtCore.QSize(100, 30))
        self.loginButton.setMaximumSize(QtCore.QSize(100, 30))
        self.loginButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.loginButton.setObjectName('loginButton')
        self.verticalLayout.addWidget(self.loginButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 273, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.frame)
        self.retranslateUi(tidalLoginWidget)
        QtCore.QMetaObject.connectSlotsByName(tidalLoginWidget)

    
    def retranslateUi(self, tidalLoginWidget):
        _translate = QtCore.QCoreApplication.translate
        tidalLoginWidget.setWindowTitle(_translate('tidalLoginWidget', 'Form'))
        self.tidalLabel.setText(_translate('tidalLoginWidget', 'TIDAL'))
        self.tipLabel.setText(_translate('tidalLoginWidget', 'If you already have a TIDAL account, log in now.'))
        self.loginButton.setText(_translate('tidalLoginWidget', 'Login'))


