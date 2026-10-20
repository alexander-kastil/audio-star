# Source Generated with Decompyle++
# File: LPIconTextMenuItem_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_iconTextMenuItemWidget(object):
    
    def setupUi(self, iconTextMenuItemWidget):
        iconTextMenuItemWidget.setObjectName('iconTextMenuItemWidget')
        iconTextMenuItemWidget.resize(222, 188)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(iconTextMenuItemWidget.sizePolicy().hasHeightForWidth())
        iconTextMenuItemWidget.setSizePolicy(sizePolicy)
        iconTextMenuItemWidget.setMinimumSize(QtCore.QSize(222, 0))
        iconTextMenuItemWidget.setMaximumSize(QtCore.QSize(222, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(iconTextMenuItemWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName('verticalLayout')
        self.mainFrame = QtWidgets.QFrame(iconTextMenuItemWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainFrame.sizePolicy().hasHeightForWidth())
        self.mainFrame.setSizePolicy(sizePolicy)
        self.mainFrame.setMinimumSize(QtCore.QSize(0, 40))
        self.mainFrame.setMaximumSize(QtCore.QSize(16777215, 40))
        self.mainFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainFrame.setObjectName('mainFrame')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.mainFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName('horizontalLayout')
        spacerItem = QtWidgets.QSpacerItem(12, 17, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.iconLabel = QtWidgets.QLabel(self.mainFrame)
        self.iconLabel.setMinimumSize(QtCore.QSize(20, 20))
        self.iconLabel.setMaximumSize(QtCore.QSize(20, 20))
        self.iconLabel.setText('')
        self.iconLabel.setObjectName('iconLabel')
        self.horizontalLayout.addWidget(self.iconLabel)
        spacerItem1 = QtWidgets.QSpacerItem(15, 17, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.textLabel = QtWidgets.QLabel(self.mainFrame)
        self.textLabel.setText('')
        self.textLabel.setObjectName('textLabel')
        self.horizontalLayout.addWidget(self.textLabel)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addWidget(self.mainFrame)
        self.retranslateUi(iconTextMenuItemWidget)
        QtCore.QMetaObject.connectSlotsByName(iconTextMenuItemWidget)

    
    def retranslateUi(self, iconTextMenuItemWidget):
        _translate = QtCore.QCoreApplication.translate
        iconTextMenuItemWidget.setWindowTitle(_translate('iconTextMenuItemWidget', 'Form'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    iconTextMenuItemWidget = QtWidgets.QWidget()
    ui = Ui_iconTextMenuItemWidget()
    ui.setupUi(iconTextMenuItemWidget)
    iconTextMenuItemWidget.show()
    sys.exit(app.exec())
