# Source Generated with Decompyle++
# File: ToolTip_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_toolTip(object):
    
    def setupUi(self, toolTip):
        toolTip.setObjectName('toolTip')
        toolTip.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(toolTip)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName('verticalLayout')
        self.mainFrame = QtWidgets.QFrame(toolTip)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.verticalLayout_2 = QtWidgets.QGridLayout(self.mainFrame)
        self.verticalLayout_2.setContentsMargins(20, 8, 8, 20)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.textLabel = QtWidgets.QLabel(self.mainFrame)
        self.textLabel.setText('')
        self.textLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.textLabel.setObjectName('textLabel')
        self.verticalLayout_2.addWidget(self.textLabel, 0, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(self.mainFrame)
        self.closeButton.setMinimumSize(QtCore.QSize(20, 20))
        self.closeButton.setMaximumSize(QtCore.QSize(20, 20))
        self.closeButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.closeButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.closeButton.setText('')
        self.closeButton.setIconSize(QtCore.QSize(20, 20))
        self.closeButton.setObjectName('closeButton')
        self.verticalLayout_2.addWidget(self.closeButton, 0, 0, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.addWidget(self.mainFrame)
        self.retranslateUi(toolTip)
        QtCore.QMetaObject.connectSlotsByName(toolTip)

    
    def retranslateUi(self, toolTip):
        _translate = QtCore.QCoreApplication.translate
        toolTip.setWindowTitle(_translate('toolTip', 'Form'))


