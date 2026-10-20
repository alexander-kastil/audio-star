# Source Generated with Decompyle++
# File: LPTidalConfirmDialogHost.pyc (Python 3.9)

'''
TIDAL 通用确认弹窗宿主，通过 app 级 QDialog + QQuickWidget 实现顶层弹窗。
'''
from typing import Callable, Optional
from PyQt6.QtCore import QMetaObject, Qt, QUrl, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QDialog, QVBoxLayout
import LPGlobalUI
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalSharedQmlContext, resolveTidalQmlPath
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPUtility import logger

class LPTidalConfirmDialogHost(QDialog):
    '''TIDAL 通用确认弹窗宿主，通过 app 级 QDialog + QQuickWidget 实现顶层弹窗。'''
    _instance: Optional['LPTidalConfirmDialogHost'] = None
    
    def __init__(self = None, parent = None):
        '''
        初始化确认弹窗宿主。

        :param parent: 父级窗口，默认使用 LPGlobalUI.mainWindow。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPTidalStore.instance()
        self._on_confirm_callback = None
        self.setModal(True)
        self.setWindowTitle('Confirm')
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(480, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._quick_widget = QQuickWidget(self)
        self._quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self._quick_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._quick_widget.setClearColor(Qt.GlobalColor.transparent)
        ctx = self._quick_widget.rootContext()
        applyTidalSharedQmlContext(ctx)
        ctx.setContextProperty('tidalStore', self._store)
        ctx.setContextProperty('sharedStore', self._store)
        ctx.setContextProperty('confirmDialogHost', self)
        local_qml = resolveTidalQmlPath('dialogs/TidalConfirmDialog.qml')
        if local_qml.exists():
            self._quick_widget.setSource(QUrl.fromLocalFile(str(local_qml)))
        else:
            self._quick_widget.setSource(QUrl('qrc:/qml/Tidal/dialogs/TidalConfirmDialog.qml'))
        if self._quick_widget.status() != QQuickWidget.Status.Ready:
            for err in self._quick_widget.errors():
                logger.error('[TIDAL] ConfirmDialog load failed: %s', err.toString())
        layout.addWidget(self._quick_widget)

    
    def instance(cls = None):
        '''
        返回确认弹窗宿主单例。

        :return: 宿主实例。
        '''
        if cls._instance is None:
            parent = getattr(LPGlobalUI, 'mainWindow', None)
            cls._instance = cls(parent)
        return cls._instance

    instance = None(instance)
    
    def show(self = None, title = None, message = None, confirmText = None, cancelText = None, confirmButtonColor = None):
        '''
        弹出确认弹窗，设置文案后打开 QML Popup 并显示 QDialog。

        :param title: 弹窗标题。
        :param message: 弹窗消息内容。
        :param confirmText: 确认按钮文字。
        :param cancelText: 取消按钮文字。
        :param confirmButtonColor: 确认按钮底色，仅非空时设置。
        :return: None。
        '''
        root = self._quick_widget.rootObject()
        if root is not None:
            root.setProperty('title', str(title))
            root.setProperty('message', str(message))
            root.setProperty('confirmText', str(confirmText))
            root.setProperty('cancelText', str(cancelText))
            confirm_color = str(confirmButtonColor).strip()
            if confirm_color:
                root.setProperty('confirmButtonColor', confirm_color)
            QMetaObject.invokeMethod(root, 'open', Qt.ConnectionType.QueuedConnection)
        super().show()
        self.raise_()
        self.activateWindow()

    show = None(show)
    
    def onConfirm(self = None):
        '''
        QML 确认按钮回调，隐藏弹窗并执行确认回调。

        :return: None。
        '''
        self.hide()
        cb = self._on_confirm_callback
        self._on_confirm_callback = None
        if cb is not None:
            cb()

    onConfirm = None(onConfirm)
    
    def onCancel(self = None):
        '''
        QML 取消/关闭按钮回调，隐藏弹窗并清理回调。

        :return: None。
        '''
        self.hide()
        self._on_confirm_callback = None

    onCancel = None(onCancel)
    __classcell__ = None

