# Source Generated with Decompyle++
# File: LPConfirmDialogHost.pyc (Python 3.9)

'''
通用 QML 确认/提示弹窗宿主，通过 app 级 QDialog + QQuickWidget 实现整窗覆盖。
'''
from pathlib import Path
from typing import Callable, Optional
from PyQt6.QtCore import QMetaObject, Qt, QUrl, pyqtSignal
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QDialog, QVBoxLayout
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class LPConfirmDialogHost(QDialog):
    '''通用 QML 确认/提示弹窗宿主，负责整窗显示层与信号回传。'''
    _instance: Optional['LPConfirmDialogHost'] = None
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()
    
    def __init__(self = None, parent = None):
        '''
        初始化确认弹窗宿主并加载通用 QML 组件。

        :param parent: 父级窗口，默认由 instance() 传入主窗口。
        :return: None。
        '''
        super().__init__(parent)
        self._on_confirmed_callback = None
        self._on_cancelled_callback = None
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
        local_qml = Path(__file__).resolve().parents[2] / 'resources' / 'qml' / 'common' / 'LPConfirmDialog.qml'
        if local_qml.exists():
            self._quick_widget.setSource(QUrl.fromLocalFile(str(local_qml)))
        else:
            self._quick_widget.setSource(QUrl('qrc:/qml/common/LPConfirmDialog.qml'))
        if self._quick_widget.status() != QQuickWidget.Status.Ready:
            for err in self._quick_widget.errors():
                logger.error('[QML] LPConfirmDialog load failed: %s', err.toString())
        layout.addWidget(self._quick_widget)
        root = self._quick_widget.rootObject()
        if root is not None:
            root.confirmed.connect(self._on_qml_confirmed)
            root.cancelled.connect(self._on_qml_cancelled)
            root.contentHeightChanged.connect(self._resizeToContent)

    
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
    
    def showDialog(self = None, title = None, message = None, confirmText = None, cancelText = None, showCancel = None, confirmButtonColor = None, onConfirmed = None, onCancelled = None):
        '''
        弹出确认/提示弹窗，设置文案后打开 QML Popup 并显示 QDialog。

        :param title: 弹窗标题。
        :param message: 弹窗消息内容。
        :param confirmText: 确定按钮文字。
        :param cancelText: 取消按钮文字。
        :param showCancel: 是否显示取消按钮，false 时为单按钮提示模式。
        :param confirmButtonColor: 确定按钮底色，非空时覆盖默认值，空时恢复默认。
        :param onConfirmed: 确定后的可选回调。
        :param onCancelled: 取消后的可选回调。
        :return: None。
        '''
        root = self._quick_widget.rootObject()
        if root is None:
            logger.error('[QML] LPConfirmDialog root object is not ready')
            return None
        self._on_confirmed_callback = None
        self._on_cancelled_callback = onCancelled
        root.setProperty('title', str(title))
        root.setProperty('message', str(message))
        root.setProperty('confirmText', str(confirmText))
        root.setProperty('cancelText', str(cancelText))
        root.setProperty('showCancelButton', bool(showCancel))
        confirm_color = str(confirmButtonColor).strip()
        root.setProperty('confirmButtonColor', confirm_color if confirm_color else '#4F59F7')
        QMetaObject.invokeMethod(root, 'open', Qt.ConnectionType.QueuedConnection)
        super().show()
        self.raise_()
        self.activateWindow()

    
    def _resizeToContent(self = None):
        '''
        根据 QML 弹窗内容高度调整宿主窗口，避免长消息被裁切。

        :return: None。
        '''
        root = self._quick_widget.rootObject()
        if root is None:
            return None
        if not root.property('contentHeight'):
            pass
        content_height = None(0)
        if content_height <= 0:
            return None
        desired_height = None(max(260, int(content_height) + 80), 720)
        self.resize(480, desired_height)

    
    def _on_qml_confirmed(self = None):
        '''
        处理 QML 确定信号：隐藏弹窗、发 confirmed 信号并执行可选回调。

        :return: None。
        '''
        self.hide()
        callback = self._on_confirmed_callback
        self._on_confirmed_callback = None
        self._on_cancelled_callback = None
        self.confirmed.emit()
        if callback is not None:
            callback()

    
    def _on_qml_cancelled(self = None):
        '''
        处理 QML 取消信号：隐藏弹窗、发 cancelled 信号并执行可选回调。

        :return: None。
        '''
        self.hide()
        callback = self._on_cancelled_callback
        self._on_confirmed_callback = None
        self._on_cancelled_callback = None
        self.cancelled.emit()
        if callback is not None:
            callback()

    __classcell__ = None

