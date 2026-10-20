# Source Generated with Decompyle++
# File: LPMinibarMarqueeLabel.pyc (Python 3.9)

'''
@Time ： 2026/5/22
@Auth ： Codex
@File ：LPMinibarMarqueeLabel.py
@Desc: minibar 设备名称滚动横幅标签。
'''
from PyQt6.QtCore import QEvent, QRectF, Qt, QTimer
from PyQt6.QtGui import QFontMetrics, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy

class LPMinibarMarqueeLabel(QLabel):
    '''minibar 设备名称滚动标签，负责在文本超宽时横向循环滚动。'''
    
    def __init__(self = None, parent = None):
        '''初始化滚动标签。

        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._fullText = ''
        self._textWidth = 0
        self._scrollOffset = 0
        self._scrollGap = 24
        self._scrollStep = 1
        self._strip = None
        self._stripKey = None
        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._advanceScroll)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

    
    def setText(self, text):
        '''设置完整设备名称，并根据宽度决定是否启动滚动。

        :param text: 需要展示的设备名称。
        :return: None。
        '''
        if not text:
            pass
        self._fullText = str('')
        self._scrollOffset = 0
        self._updateTextWidth()
        self._invalidateStrip()
        self.setToolTip(self._fullText)
        self._updateScrollState()
        self.update()

    
    def text(self):
        '''返回当前完整设备名称。

        :return: 完整设备名称字符串。
        '''
        return self._fullText

    
    def _updateTextWidth(self):
        '''重新计算并缓存完整文本的像素宽度，避免每帧重复度量。

        :return: None。
        '''
        self._textWidth = QFontMetrics(self.font()).horizontalAdvance(self._fullText)

    
    def _invalidateStrip(self):
        '''使预渲染滚动条失效，下次绘制时重建。

        :return: None。
        '''
        self._strip = None
        self._stripKey = None

    
    def _renderStrip(self):
        '''把两段文本预渲染到位图，逐帧绘制时只做位图平移。

        :return: None。
        '''
        rect = self.contentsRect()
        strip_width = max(1, rect.width() + self._textWidth + self._scrollGap)
        strip_height = max(1, rect.height())
        dpr = self.devicePixelRatioF()
        self._strip = QPixmap(max(1, int(round(strip_width * dpr))), max(1, int(round(strip_height * dpr))))
        self._strip.setDevicePixelRatio(dpr)
        self._strip.fill(Qt.GlobalColor.transparent)
        self._stripKey = (strip_width, strip_height, dpr)
        painter = QPainter(self._strip)
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        text_rect = QRectF(0, 0, self._textWidth, strip_height)
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter), self._fullText)
        text_rect.moveLeft(self._textWidth + self._scrollGap)
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter), self._fullText)
        painter.end()

    
    def changeEvent(self = None, event = None):
        '''字体或配色变化时刷新文本宽度与预渲染位图。

        :param event: Qt 事件。
        :return: None。
        '''
        super().changeEvent(event)
        if event.type() == QEvent.Type.FontChange:
            self._scrollOffset = 0
            self._updateTextWidth()
            self._invalidateStrip()
            self._updateScrollState()
            self.update()
        elif event.type() == QEvent.Type.PaletteChange:
            self._invalidateStrip()
            self.update()

    
    def resizeEvent(self = None, event = None):
        '''处理尺寸变化并重新计算滚动状态。

        :param event: Qt 尺寸变化事件。
        :return: None。
        '''
        super().resizeEvent(event)
        self._scrollOffset = 0
        self._invalidateStrip()
        self._updateScrollState()

    
    def hideEvent(self = None, event = None):
        '''隐藏时停止滚动定时器，避免不可见时继续空转。

        :param event: Qt 隐藏事件。
        :return: None。
        '''
        super().hideEvent(event)
        if self._timer.isActive():
            self._timer.stop()

    
    def showEvent(self = None, event = None):
        '''重新显示时按需恢复滚动定时器。

        :param event: Qt 显示事件。
        :return: None。
        '''
        super().showEvent(event)
        self._updateScrollState()
        self.update()

    
    def paintEvent(self = None, event = None):
        '''绘制设备名称，超宽时绘制循环滚动横幅。

        :param event: Qt 绘制事件。
        :return: None。
        '''
        if not self._shouldScroll():
            return super().paintEvent(event)
        rect = None.contentsRect()
        strip_width = rect.width() + self._textWidth + self._scrollGap
        strip_height = rect.height()
        if self._strip is None or self._stripKey != (strip_width, strip_height, self.devicePixelRatioF()):
            self._renderStrip()
        painter = QPainter(self)
        painter.drawPixmap(rect.x() - self._scrollOffset, rect.y(), self._strip)

    
    def _advanceScroll(self):
        '''推进滚动位置。

        :return: None。
        '''
        if not self.isVisible():
            if self._timer.isActive():
                self._timer.stop()
            return None
        if not None._shouldScroll():
            self._scrollOffset = 0
            self._updateScrollState()
            return None
        None._scrollOffset += self._scrollStep
        if self._scrollOffset >= self._textWidth + self._scrollGap:
            self._scrollOffset = 0
        self.update()

    
    def _shouldScroll(self):
        '''判断当前文本是否需要滚动。

        :return: 需要滚动时返回 True，否则返回 False。
        '''
        if not self._fullText:
            return False
        return None._textWidth > max(0, self.contentsRect().width() - 4)

    
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

