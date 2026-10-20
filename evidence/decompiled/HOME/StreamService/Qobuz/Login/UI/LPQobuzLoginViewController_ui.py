# Source Generated with Decompyle++
# File: LPQobuzLoginViewController_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_qobuzLoginWidget(object):
    
    def setupUi(self, qobuzLoginWidget):
        qobuzLoginWidget.setObjectName('qobuzLoginWidget')
        qobuzLoginWidget.resize(924, 657)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(qobuzLoginWidget)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.frame = QtWidgets.QFrame(qobuzLoginWidget)
        self.frame.setStyleSheet('border: none')
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName('frame')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName('verticalLayout')
        spacerItem = QtWidgets.QSpacerItem(20, 273, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.qobuzLabel = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qobuzLabel.sizePolicy().hasHeightForWidth())
        self.qobuzLabel.setSizePolicy(sizePolicy)
        self.qobuzLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.qobuzLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.qobuzLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.qobuzLabel.setObjectName('qobuzLabel')
        self.verticalLayout.addWidget(self.qobuzLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
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
        self.retranslateUi(qobuzLoginWidget)
        QtCore.QMetaObject.connectSlotsByName(qobuzLoginWidget)

    
    def retranslateUi(self, qobuzLoginWidget):
        _translate = QtCore.QCoreApplication.translate
        qobuzLoginWidget.setWindowTitle(_translate('qobuzLoginWidget', 'Form'))
        self.qobuzLabel.setText(_translate('qobuzLoginWidget', 'Qobuz'))
        self.tipLabel.setText(_translate('qobuzLoginWidget', 'If you already have a Qobuz account, log in now.'))
        self.loginButton.setText(_translate('qobuzLoginWidget', 'Login'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qobuzLoginWidget = QtWidgets.QWidget()
    ui = Ui_qobuzLoginWidget()
    ui.setupUi(qobuzLoginWidget)
    qobuzLoginWidget.show()
    sys.exit(app.exec())
