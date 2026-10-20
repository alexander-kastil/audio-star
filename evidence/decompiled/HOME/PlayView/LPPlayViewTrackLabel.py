# Source Generated with Decompyle++
# File: LPPlayViewTrackLabel.pyc (Python 3.9)

'''PlayView 曲目标题滚动标签。'''
from PyQt6.QtCore import QEvent, QSize, Qt, QTimer
from PyQt6.QtGui import QFontMetrics, QPainter
from PyQt6.QtWidgets import QLabel, QSizePolicy

class LPPlayViewTrackLabel(QLabel):
    '''在曲目标题超出可视宽度时从右向左循环滚动。'''
    SCROLL_GAP = 24
    SCROLL_STEP = 1
    SCROLL_INTERVAL_MS = 35
    HOLD_INTERVAL_MS = 1000
    
    def __init__(self = None, parent = None):
        '''初始化曲目标题标签。

        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self.full_text = ''
        self._scrollOffset = 0
        self._holdingAtStart = True
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advanceScroll)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    
    def setText(self = None, text = None):
        '''设置完整标题，并从标题开头重新判断滚动状态。

        :param text: 曲目标题文本。
        :return: None。
        '''
        if not text:
            pass
        self.full_text = str('')
        self._resetScrollPosition()
        self.setToolTip(self.full_text)
        super().setText(self.full_text)
        self._updateScrollState()
        self.updateGeometry()
        self.update()

    
    def text(self):
        '''返回未裁剪的完整曲目标题。

        :return: 完整曲目标题字符串。
        '''
        return self.full_text

    
    def minimumSizeHint(self = None):
        '''允许布局压缩标题宽度，同时保留标签建议高度。

        :return: 宽度为零的最小建议尺寸。
        '''
        hint = super().minimumSizeHint()
        return QSize(0, hint.height())

    
    def resizeEvent(self = None, event = None):
        '''尺寸变化后从标题开头重新计算是否需要滚动。

        :param event: Qt 尺寸变化事件。
        :return: None。
        '''
        super().resizeEvent(event)
        self._resetScrollPosition()
        self._updateScrollState()

    
    def changeEvent(self = None, event = None):
        '''字体变化后重新计算标题宽度和滚动状态。

        :param event: Qt 属性变化事件。
        :return: None。
        '''
        super().changeEvent(event)
        if event.type() == QEvent.Type.FontChange:
            self._resetScrollPosition()
            self._updateScrollState()
            self.updateGeometry()

    
    def hideEvent(self = None, event = None):
        '''标签隐藏时停止滚动，避免不可见页面持续刷新。

        :param event: Qt 隐藏事件。
        :return: None。
        '''
        self._timer.stop()
        super().hideEvent(event)

    
    def showEvent(self = None, event = None):
        '''标签显示时从标题开头恢复必要的滚动。

        :param event: Qt 显示事件。
        :return: None。
        '''
        super().showEvent(event)
        self._resetScrollPosition()
        self._updateScrollState()

    
    def paintEvent(self = None, event = None):
        '''短标题居中绘制，超宽标题从左边界向左循环绘制。

        :param event: Qt 绘制事件。
        :return: None。
        '''
        if not self._shouldScroll():
            super().paintEvent(event)
            return None
        painter = None(self)
        painter.setClipRect(self.contentsRect())
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        rect = self.contentsRect()
        text_width = QFontMetrics(self.font()).horizontalAdvance(self.full_text)
        first_x = rect.x() - self._scrollOffset
        second_x = first_x + text_width + self.SCROLL_GAP
        alignment = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        painter.drawText(first_x, rect.y(), text_width, rect.height(), alignment, self.full_text)
        painter.drawText(second_x, rect.y(), text_width, rect.height(), alignment, self.full_text)

    
    def _advanceScroll(self):
        '''结束开头停留或推进一帧滚动位置。

        :return: None。
        '''
        if not self._shouldScroll():
            self._resetScrollPosition()
            self._updateScrollState()
            return None
        if None._holdingAtStart:
            self._holdingAtStart = False
            self._timer.setInterval(self.SCROLL_INTERVAL_MS)
            return None
        text_width = None(self.font()).horizontalAdvance(self.full_text)
        self._scrollOffset += self.SCROLL_STEP
        if self._scrollOffset >= text_width + self.SCROLL_GAP:
            self._resetScrollPosition()
            self._timer.setInterval(self.HOLD_INTERVAL_MS)
        self.update()

    
    def _shouldScroll(self):
        '''判断完整标题是否超出当前可视宽度。

        :return: 标题超宽时返回 True，否则返回 False。
        '''
        if not self.full_text:
            return False
        text_width = None(self.font()).horizontalAdvance(self.full_text)
        return text_width > max(0, self.contentsRect().width())

    
    def _resetScrollPosition(self):
        '''将滚动位置恢复到标题开头并进入停留状态。

        :return: None。
        '''
        self._scrollOffset = 0
        self._holdingAtStart = True

    
    def _updateScrollState(self):
        '''根据标题宽度启动或停止滚动定时器。

        :return: None。
        '''
        if self._shouldScroll():
            if self.isVisible() and self._holdingAtStart:
                self._timer.start(self.HOLD_INTERVAL_MS)
            elif not self.isVisible() and self._timer.isActive():
                self._timer.start(self.SCROLL_INTERVAL_MS)
            return None
        None._timer.stop()

    __classcell__ = None

