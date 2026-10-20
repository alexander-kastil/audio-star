# Source Generated with Decompyle++
# File: LPQobuzGenresSelector_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_qobuzGenres_Form(object):
    
    def setupUi(self, qobuzGenres_Form):
        qobuzGenres_Form.setObjectName('qobuzGenres_Form')
        qobuzGenres_Form.resize(450, 300)
        qobuzGenres_Form.setMinimumSize(QtCore.QSize(450, 0))
        qobuzGenres_Form.setMaximumSize(QtCore.QSize(450, 300))
        qobuzGenres_Form.setStyleSheet('border:none;')
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(qobuzGenres_Form)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.mainFrame = QtWidgets.QFrame(qobuzGenres_Form)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout.setObjectName('verticalLayout')
        self.titleFrame = QtWidgets.QFrame(self.mainFrame)
        self.titleFrame.setMinimumSize(QtCore.QSize(0, 50))
        self.titleFrame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.titleFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.titleFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.titleFrame.setObjectName('titleFrame')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.titleFrame)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.toggleBox = QtWidgets.QCheckBox(self.titleFrame)
        self.toggleBox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.toggleBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.toggleBox.setText('')
        self.toggleBox.setObjectName('toggleBox')
        self.horizontalLayout.addWidget(self.toggleBox, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.verticalLayout.addWidget(self.titleFrame)
        self.frame = QtWidgets.QFrame(self.mainFrame)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName('frame')
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName('verticalLayout_3')
        self.genresGridLayout = QtWidgets.QGridLayout()
        self.genresGridLayout.setContentsMargins(40, 0, 40, -1)
        self.genresGridLayout.setSpacing(6)
        self.genresGridLayout.setObjectName('genresGridLayout')
        self.verticalLayout_3.addLayout(self.genresGridLayout)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout_2.addWidget(self.mainFrame)
        self.retranslateUi(qobuzGenres_Form)
        QtCore.QMetaObject.connectSlotsByName(qobuzGenres_Form)

    
    def retranslateUi(self, qobuzGenres_Form):
        _translate = QtCore.QCoreApplication.translate
        qobuzGenres_Form.setWindowTitle(_translate('qobuzGenres_Form', 'Form'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qobuzGenres_Form = QtWidgets.QWidget()
    ui = Ui_qobuzGenres_Form()
    ui.setupUi(qobuzGenres_Form)
    qobuzGenres_Form.show()
    sys.exit(app.exec())
