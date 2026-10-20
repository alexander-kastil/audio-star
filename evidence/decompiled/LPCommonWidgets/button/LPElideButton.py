# Source Generated with Decompyle++
# File: LPElideButton.pyc (Python 3.9)

'''
@Time ： 2025/9/4 14:29
@Auth ： Chris
@File ：LPElideButton.py
@Desc:
'''
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QPushButton, QSizePolicy

class LPElideButton(QPushButton):
    '''支持尾部省略号的按钮：宽度不足时按可用宽度省略文本并保留完整悬停提示。'''
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.full_text = ''
        self.maxLength = 200
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet('text-align: left;')

    
    def setText(self = None, text = None, maxLength = None):
        self.full_text = text
        self.maxLength = maxLength
        self.setToolTip(text)
        self._updateElidedText()

    
    def minimumSizeHint(self = None):
        '''
        重写最小尺寸提示：宽度固定为 0，避免完整文本把布局最小宽度撑大，
        保证窗口回缩时控件可以收缩并重新触发省略。

        返回:
            QSize: 宽度为 0 的最小尺寸提示。
        '''
        hint = super().minimumSizeHint()
        return QSize(0, hint.height())

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        self._updateElidedText()

    
    def _updateElidedText(self = None):
        '''
        按控件当前实际宽度对完整文本做尾部省略并刷新显示。
        宽度由布局按 Expending 策略分配，省略点跟随控件宽度变化，
        配合 minimumSizeHint 宽度为 0 可随窗口收缩。
        maxLength 属性保留仅为兼容旧调用方签名，不再参与省略计算。
        '''
        metrics = QFontMetrics(self.font())
        availableWidth = max(self.width(), 1)
        elided = metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, availableWidth)
        super().setText(elided)

    __classcell__ = None

