# Source Generated with Decompyle++
# File: LPLoginDialog.pyc (Python 3.9)

'''
@Time ： 2025/1/6 16:43
@Auth ： Chris
@File ：LPLoginDialog.py
@Desc:
'''
from string import Template
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QPainterPath, QRegion, QPixmap, QIcon, QAction
from PyQt6.QtWidgets import QDialog, QLineEdit, QToolButton, QWidgetAction
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import SiderBar_Subtitle
from LPClientFramework.LPUtility import logger
from LPClientFramework.util.aes import AESCipher

class LPLoginDialog(QDialog):
    loginSignal = pyqtSignal(str, str, bool)
    loginSuccessSignal = pyqtSignal()
    loginFailSignal = pyqtSignal()
    
    def __init__(self = None, source = None, picUrl = None, parent = None):
        super().__init__(parent)
        self.source = source
        self.parent = parent
        self.picUrl = picUrl
        self.loginSuccessSignal.connect(self.loginSuccess)
        self.loginFailSignal.connect(self.loginFail)
        self.loginSignal.connect(self.validateLogin)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        pixmap = QPixmap(self.picUrl)
        fixed_height = self.imageLabel.height()
        scaledPix = pixmap.scaledToHeight(fixed_height, Qt.TransformationMode.SmoothTransformation)
        self.imageLabel.setPixmap(scaledPix)
        self.imageLabel.setScaledContents(False)
        accountLabelText = QCoreApplication.translate('Login', 'Email/Username')
        accountInputHint = QCoreApplication.translate('Login', 'Enter your username')
        passwordLabelText = QCoreApplication.translate('Login', 'Password')
        passwordInputHint = QCoreApplication.translate('Login', 'Enter your password')
        self.accountLabel.setText(accountLabelText)
        self.accountInput.setPlaceholderText(accountInputHint)
        self.passwordLabel.setText(passwordLabelText)
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.setPlaceholderText(passwordInputHint)
        loginButtonText = QCoreApplication.translate('Login', 'Login')
        self.loginButton.setText(loginButtonText)
        cancelButtonText = QCoreApplication.translate('Login', 'Cancel')
        self.cancelButton.setText(cancelButtonText)
        self.cancelButton.clicked.connect(self.reject)
        self.loginButton.clicked.connect(self.handleLogin)
        rememberText = QCoreApplication.translate('Login', 'Remember me')
        self.remembermeCheckBox.setText(rememberText)
        self.eye_open_img = LPUtility.tintImage(LPGlobalUI.imagePath('eye_open.png'), LPGlobalUI.THEME_BACKGROUND_COLOR)
        self.eye_close_img = LPUtility.tintImage(LPGlobalUI.imagePath('eye_close.png'), LPGlobalUI.THEME_BACKGROUND_COLOR)
        self.toggle_button = QToolButton(self.passwordInput)
        self.toggle_button.setIcon(QIcon(self.eye_close_img))
        self.toggle_button.setIconSize(QSize(22, 22))
        self.toggle_button.setCheckable(True)
        widgetAction = QWidgetAction(self.passwordInput)
        widgetAction.setDefaultWidget(self.toggle_button)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setStyleSheet('QToolButton { border: none; padding: 0px; }')
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        self.passwordInput.addAction(widgetAction, QLineEdit.ActionPosition.TrailingPosition)
        qssTemplate = Template('                \n                QDialog{\n                    color: $fontColor;\n                }\n                QFrame{\n                    border:none;\n                    background-color: transparent;\n                }\n                QFrame#mainFrame{\n                    border-radius: 20px;\n                    background-color: $dialogBg;\n                }\n                QLabel {\n                    color: $fontColor;\n                }\n                QLabel#accountLabel, #passwordLabel{\n                    margin-left: 20px;\n                }\n                QPushButton#loginButton {\n                    border: 0;\n                    border-radius: 17px;\n                    color: $fontColor;\n                    background-color: $buttonBg;\n                }\n                \n                QPushButton#loginButton:hover {\n                    background-color: $buttonHoverBg;\n                }\n                QPushButton#loginButton:disabled {\n                    background-color: $buttonHoverBg;\n                }\n                \n                QPushButton#cancelButton {\n                    border: 0;\n                    border-radius: 17px;\n                    background-color: #2E2E2E;\n                    color: $fontColor;\n                }\n                QPushButton#cancelButton:hover {\n                    background-color: #3E3E3E;\n                }\n                QLineEdit {\n                    border: 0;\n                    border-radius: 8px;\n                    padding-left: 16px;\n                    padding-right: 16px;\n                }\n                QCheckBox {\n                    color: $fontColor;\n                    margin-left: 20px;\n                    font-size: ${checkBoxFontSize}pt;\n                }\n                ')
        self.setStyleSheet(qssTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name(), LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name(), LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR, f'''{SiderBar_Subtitle}''', **('fontColor', 'dialogBg', 'buttonBg', 'buttonHoverBg', 'checkBoxFontSize')))

    
    def handleLogin(self):
        self.loginButton.setEnabled(False)
        username = self.accountInput.text()
        password = self.passwordInput.text()
        remember_me = self.remembermeCheckBox.isChecked()
        if remember_me:
            self.loginSignal.emit(username, password, True)
        else:
            self.loginSignal.emit(username, password, False)

    
    def toggle_password_visibility(self, checked):
        '''切换密码显示状态'''
        if checked:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setIcon(QIcon(self.eye_open_img))
        else:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setIcon(QIcon(self.eye_close_img))

    toggle_password_visibility = pyqtSlot(bool)(toggle_password_visibility)
    
    def autofill(self, username, password):
        self.accountInput.setText(username)
        self.passwordInput.setText(password)
        self.remembermeCheckBox.setChecked(True)
        self.toggle_password_visibility(False)

    
    def exec(self = None):
        data = LPUtility.loadAccountForSource(self.source)
        if data:
            username = data['username']
            password = data['password']
            self.autofill(username, password)
        super().exec()

    
    def loginSuccess(self):
        self.accept()
        self.parent.updateAccountSignal.emit()
        self.parent.updateLoginButtonSignal.emit()
        logger.debug('login success')

    loginSuccess = pyqtSlot()(loginSuccess)
    
    def loginFail(self):
        showtText = QCoreApplication.translate('Login', 'login failed! Please check username or password again!')
        LPGlobalUI.toast.showToast(showtText, self.parent)
        self.passwordInput.clear()
        logger.debug('login fail')

    loginFail = pyqtSlot()(loginFail)
    
    def validateLogin(self, username, password, isRemember):
        
        def finishMethod(account = None):
            self.loginButton.setEnabled(True)
            if account and account.userId:
                self.loginSuccessSignal.emit()
                if isRemember:
                    LPUtility.rememberForSource(LPGlobalUI.currentDevice.uuid[:16], username, password, self.source)
                    logger.debug(self.source + ' remember password')
                else:
                    LPUtility.clearRememberForSource(self.source)
                    logger.debug(self.source + ' clear remember password')
            else:
                self.loginFailSignal.emit()

        username = username.strip()
        if not username:
            showtText = QCoreApplication.translate('Login', "The username can't be empty")
            LPGlobalUI.toast.showToast(showtText, self.parent)
            self.loginButton.setEnabled(True)
            return None
        if not None:
            showtText = QCoreApplication.translate('Login', "The password can't be empty")
            LPGlobalUI.toast.showToast(showtText, self.parent)
            self.loginButton.setEnabled(True)
            return None
        key = None.currentDevice.uuid[:16]
        encryptedPwd = AESCipher.encrypt(key, password)
        LPGlobalUI.currentDevice.deviceStreamServiceManager.loginAccountForSource(self.source, username, encryptedPwd, finishMethod)

    validateLogin = pyqtSlot(str, str, bool)(validateLogin)
    __classcell__ = None

