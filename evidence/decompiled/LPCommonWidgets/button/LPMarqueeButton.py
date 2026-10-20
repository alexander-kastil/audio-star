# Source Generated with Decompyle++
# File: LPMarqueeButton.pyc (Python 3.9)

'''
@Time ： 2026/5/22
@Auth ： Codex
@File ：LPMarqueeButton.py
@Desc: 按钮文本横幅滚动控件。
'''
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontMetrics, QPainter
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QStyle, QStyleOptionButton

class LPMarqueeButton(QPushButton):
    '''横幅滚动按钮，负责在文本超出可视宽度时循环显示完整文本。'''
    
    def __init__(self = None, parent = None):
        '''初始化横幅滚动按钮。

        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._fullText = ''
        self._scrollOffset = 0
        self._scrollGap = 24
        self._scrollStep = 1
        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._advanceScroll)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    
    def setText(self, text):
        '''设置按钮完整文本，并根据宽度决定是否启动滚动。

        :param text: 需要显示的完整文本。
        :return: None。
        '''
        if not text:
            pass
        self._fullText = str('')
        self._scrollOffset = 0
        self.setToolTip(self._fullText)
        self._updateScrollState()
        self.update()

    
    def text(self):
        '''返回按钮完整文本。

        :return: 完整文本字符串。
        '''
        return self._fullText

    
    def resizeEvent(self = None, event = None):
        '''处理按钮尺寸变化并重新计算滚动状态。

        :param event: Qt 尺寸变化事件。
        :return: None。
        '''
        super().resizeEvent(event)
        self._scrollOffset = 0
        self._updateScrollState()

    
    def hideEvent(self = None, event = None):
        '''隐藏按钮时停止滚动定时器。

        :param event: Qt 隐藏事件。
        :return: None。
        '''
        self._timer.stop()
        super().hideEvent(event)

    
    def showEvent(self = None, event = None):
        '''显示按钮时恢复必要的滚动状态。

        :param event: Qt 显示事件。
        :return: None。
        '''
        super().showEvent(event)
        self._updateScrollState()

    
    def paintEvent(self = None, event = None):
        '''绘制按钮文本，超宽时绘制横向循环滚动文本。

        :param event: Qt 绘制事件。
        :return: None。
        '''
        if not self._shouldScroll():
            return super().paintEvent(event)
        option = None()
        self.initStyleOption(option)
        option.text = ''
        painter = QPainter(self)
        self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
        painter.setClipRect(self.contentsRect())
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        rect = self.contentsRect().adjusted(0, 0, 0, 0)
        text_width = QFontMetrics(self.font()).horizontalAdvance(self._fullText)
        first_x = rect.x() - self._scrollOffset
        second_x = first_x + text_width + self._scrollGap
        alignment = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        painter.drawText(first_x, rect.y(), text_width, rect.height(), alignment, self._fullText)
        painter.drawText(second_x, rect.y(), text_width, rect.height(), alignment, self._fullText)

    
    def _advanceScroll(self):
        '''推进滚动位置。

        :return: None。
        '''
        if not self._shouldScroll():
            self._scrollOffset = 0
            self._updateScrollState()
            return None
        text_width = None(self.font()).horizontalAdvance(self._fullText)
        self._scrollOffset += self._scrollStep
        if self._scrollOffset >= text_width + self._scrollGap:
            self._scrollOffset = 0
        self.update()

    
    def _shouldScroll(self):
        '''判断当前完整文本是否超出按钮可视宽度。

        :return: 文本超宽时返回 True，否则返回 False。
        '''
        if not self._fullText:
            return False
        text_width = None(self.font()).horizontalAdvance(self._fullText)
        return text_width > max(0, self.contentsRect().width() - 4)

    
    def _updateScrollState(self = None):
        '''根据文本宽度启动或停止滚动定时器。

        :return: None。
        '''
        if self._shouldScroll():
            super().setText('')
            if not self.isVisible() and self._timer.isActive():
                self._timer.start()
            return None
        if None._timer.isActive():
            self._timer.stop()
        super().setText(self._fullText)

    __classcell__ = None

