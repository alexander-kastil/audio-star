# Source Generated with Decompyle++
# File: LPRadioParadise2ViewController_ui.pyc (Python 3.9)

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_radioParadiseWidget(object):
    
    def setupUi(self, radioParadiseWidget):
        radioParadiseWidget.setObjectName('radioParadiseWidget')
        radioParadiseWidget.resize(924, 657)
        self.verticalLayout = QtWidgets.QVBoxLayout(radioParadiseWidget)
        self.verticalLayout.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout.setObjectName('verticalLayout')
        self.frame = QtWidgets.QFrame(radioParadiseWidget)
        self.frame.setStyleSheet('border: none')
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName('frame')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 12, 9, 12)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setStyleSheet('QLabel {color: white}')
        self.label.setObjectName('label')
        self.horizontalLayout.addWidget(self.label)
        self.loginButton = QtWidgets.QPushButton(self.frame)
        self.loginButton.setMinimumSize(QtCore.QSize(0, 0))
        self.loginButton.setMaximumSize(QtCore.QSize(40, 40))
        self.loginButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.loginButton.setStyleSheet('QPushButton{\n    border: none;\n}')
        self.loginButton.setText('')
        self.loginButton.setObjectName('loginButton')
        self.horizontalLayout.addWidget(self.loginButton)
        self.verticalLayout.addWidget(self.frame)
        self.stackedWidget = QtWidgets.QStackedWidget(radioParadiseWidget)
        self.stackedWidget.setObjectName('stackedWidget')
        self.contentPage = QtWidgets.QWidget()
        self.contentPage.setStyleSheet('border: none;')
        self.contentPage.setObjectName('contentPage')
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.contentPage)
        self.verticalLayout_2.setContentsMargins(0, -1, 0, 0)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.listView = LPSuperListView(self.contentPage)
        self.listView.setStyleSheet('QListView::item {color: rgb(108,108,108)}\nQScrollBar {\n        border: 0px;\n        background: transparent;\n        width:10px;\n        height:10px;\n        margin: 0px 0px 0px 0px;\n    }\n    QScrollBar::handle {\n        background: rgb(82,82,82);\n        min-height: 0px;\n    border-radius: 5px;\n    }\n    QScrollBar::add-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n    QScrollBar::sub-line {\n        border: 0px;\n        background: none;\n        height: 0px;\n        width: 0px;\n    }\n        QScrollBar::add-page, QScrollBar::sub-page {\nheight: 0px;\n        width: 0px;\n        border: 0px;\n}\nQHeaderView::section {\nbackground-color: transparent;\ncolor: white;\n}')
        self.listView.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.listView.setGridSize(QtCore.QSize(210, 265))
        self.listView.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.listView.setObjectName('listView')
        self.verticalLayout_2.addWidget(self.listView)
        self.stackedWidget.addWidget(self.contentPage)
        self.notePage = QtWidgets.QWidget()
        self.notePage.setObjectName('notePage')
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.notePage)
        self.horizontalLayout_2.setObjectName('horizontalLayout_2')
        self.noteLabel = QtWidgets.QLabel(self.notePage)
        self.noteLabel.setStyleSheet('QLabel {color: white}')
        self.noteLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.noteLabel.setObjectName('noteLabel')
        self.horizontalLayout_2.addWidget(self.noteLabel)
        self.stackedWidget.addWidget(self.notePage)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.retranslateUi(radioParadiseWidget)
        QtCore.QMetaObject.connectSlotsByName(radioParadiseWidget)

    
    def retranslateUi(self, radioParadiseWidget):
        _translate = QtCore.QCoreApplication.translate
        radioParadiseWidget.setWindowTitle(_translate('radioParadiseWidget', 'Form'))
        self.label.setText(_translate('radioParadiseWidget', 'Radio Paradise'))
        self.noteLabel.setText(_translate('radioParadiseWidget', 'There is currently no radio available, please try again later'))


from HOME.LPSuperListView import LPSuperListView
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    radioParadiseWidget = QtWidgets.QWidget()
    ui = Ui_radioParadiseWidget()
    ui.setupUi(radioParadiseWidget)
    radioParadiseWidget.show()
    sys.exit(app.exec())
