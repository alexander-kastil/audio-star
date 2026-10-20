# Source Generated with Decompyle++
# File: LPElideLabel.pyc (Python 3.9)

'''
@Time ： 2025/6/23 13:38
@Auth ： Chris
@File ：LPElideLabel.py
@Desc:
'''
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QFontMetrics

class LPElideLabel(QLabel):
    '''支持尾部省略号的自适应标签：宽度不足时按当前宽度省略文本并保留完整悬停提示。'''
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.full_text = ''
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    
    def setText(self = None, text = None):
        '''
        保存完整文本并按当前宽度刷新省略显示。

        参数:
            text (str): 完整展示文本。
        返回:
            无
        '''
        self.full_text = text
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
        按控件当前宽度对完整文本做尾部省略并刷新显示。

        参数:
            无
        返回:
            无
        '''
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, self.width())
        super().setText(elided)

    __classcell__ = None

