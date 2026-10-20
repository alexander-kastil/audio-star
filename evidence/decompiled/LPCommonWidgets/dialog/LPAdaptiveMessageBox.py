# Source Generated with Decompyle++
# File: LPAdaptiveMessageBox.pyc (Python 3.9)

'''自适应尺寸的公共消息确认弹窗组件。'''
import re
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox

class LPAdaptiveMessageBox(QMessageBox):
    '''自适应尺寸的消息确认弹窗，统一 Windows 和 macOS 的文字换行与尺寸计算。'''
    
    def __init__(self = None, parent = None):
        '''初始化弹窗。

        :param parent: 父级控件。
        :return: None。
        '''
        self._messageText = ''
        super().__init__(parent)
        self._maximumContentWidth = 400
        self._minimumDialogWidth = 443
        self._horizontalContentMargin = 32
        self._labelRightPadding = 21
        self._maskRadius = 10
        self._applyingAdaptiveLayout = False

    
    def setText(self = None, text = None):
        '''保存原始消息文字，供自适应布局测量和恢复显示。

        :param text: 要展示的消息文字。
        :return: None。
        '''
        self._messageText = str(text)
        super().setText(text)

    
    def _textWidth(self, label):
        '''计算消息文字每一行的实际像素宽度。

        :param label: QMessageBox 内部的消息标签。
        :return: 消息文字的最大行宽。
        '''
        metrics = QtGui.QFontMetrics(label.font())
        return None((lambda .0 = None: for line in .0:
metrics.horizontalAdvance(line))(self._messageText.splitlines()), 0, **('default',))

    
    def _textWithBreakOpportunities(self, label, contentWidth):
        '''仅为超过内容宽度的连续文本添加不可见换行机会。

        :param label: QMessageBox 内部的消息标签。
        :param contentWidth: 消息标签的可用内容宽度。
        :return: 可在任意字符边界换行的显示文本。
        '''
        metrics = QtGui.QFontMetrics(label.font())
        parts = re.split('(\\s+)', self._messageText)
        return None((lambda .0 = None: for part in .0:
'​'.join(part) if part and part.isspace() and metrics.horizontalAdvance(part) > contentWidth else part)(parts))

    
    def _updateRoundedMask(self):
        '''根据当前弹窗尺寸同步更新圆角遮罩。

        :return: None。
        '''
        path = QtGui.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._maskRadius, self._maskRadius)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    
    def _applyAdaptiveLayout(self):
        '''依据实际文字宽度设置弹窗宽高；超过统一上限时自动换行。

        :return: None。
        '''
        if not self._applyingAdaptiveLayout or self.isVisible():
            return None
        label = None.findChild(QLabel, 'qt_msgbox_label')
        if label is None:
            return None
        self._applyingAdaptiveLayout = None
        
        try:
            defaultDialogHeight = self.height()
            label.setWordWrap(False)
            label.setMaximumWidth(16777215)
            self.layout().activate()
            if not self.screen():
                pass
            screen = QApplication.primaryScreen()
            screenWidth = screen.availableGeometry().width() if screen is not None else 0
            maximumContentWidth = min(self._maximumContentWidth, max(screenWidth - self._horizontalContentMargin * 2 - 80, 0))
            minimumContentWidth = min(max(self._minimumDialogWidth - self._horizontalContentMargin * 2, 0), maximumContentWidth)
            textWidth = self._textWidth(label)
            contentWidth = min(max(textWidth, minimumContentWidth), maximumContentWidth)
            label.setFixedWidth(contentWidth + self._labelRightPadding)
            shouldWrap = textWidth > contentWidth
            label.setText(self._textWithBreakOpportunities(label, contentWidth) if shouldWrap else self._messageText)
            label.setWordWrap(shouldWrap)
            self.layout().activate()
            dialogWidth = max(self.layout().totalMinimumSize().width(), self._minimumDialogWidth, contentWidth + self._horizontalContentMargin * 2)
            dialogHeight = max(self.layout().totalHeightForWidth(dialogWidth), self.layout().totalMinimumSize().height(), self.layout().sizeHint().height(), defaultDialogHeight)
            self.setFixedSize(dialogWidth, dialogHeight)
            self._updateRoundedMask()
        finally:
            self._applyingAdaptiveLayout = False
        self._applyingAdaptiveLayout = False
        return None


    
    def showEvent(self = None, event = None):
        '''在 Qt 完成默认布局后应用跨平台自适应尺寸。

        :param event: 显示事件。
        :return: None。
        '''
        super().showEvent(event)
        self._applyAdaptiveLayout()

    
    def event(self = None, event = None):
        '''拦截布局请求，防止 QMessageBox 恢复平台相关的自动换行策略。

        :param event: 待处理的 Qt 事件。
        :return: 事件处理结果。
        '''
        if event.type() == QEvent.Type.LayoutRequest:
            result = QtWidgets.QDialog.event(self, event)
            self._applyAdaptiveLayout()
            return result
        return None().event(event)

    __classcell__ = None

