# Source Generated with Decompyle++
# File: LPPlayViewBackWidget.pyc (Python 3.9)

'''
@Time ： 2025/11/27 17:11
@Auth ： Chris
@File ：LPPlayViewBackWidget.py
@Desc:
'''
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget

class LPPlayViewBackWidget(QWidget):
    '''播放页背景控件，负责绘制封面模糊背景或默认纯色背景。

    历史实现继承 QOpenGLWidget（硬件 GL 表面），双显卡 Windows 机器上
    切换全屏会触发驱动级显示模式切换导致 1~2 秒黑屏；改为 QWidget +
    QPainter 软件光栅化绘制以规避该问题。始终从原始图缩放，避免对已
    缩放图反复缩放导致的画质劣化和耗时累积。
    '''
    
    def __init__(self = None, parent = None):
        '''初始化背景控件。

        参数:
            parent (QWidget | None): 父控件。
        返回:
            无。
        '''
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.sourcePixmap = None
        self.pixmap = None
        self.default_color = Qt.GlobalColor.black
        self.default_source_pixmap = None
        self.default_pixmap = None

    
    def setDefaultBackground(self = None, pixmap = None, color = None):
        '''设置默认背景。

        参数:
            pixmap (QPixmap | None): 默认背景图，可为空；为空时仅使用颜色。
            color: 默认背景颜色。
        返回:
            无。
        '''
        self.default_source_pixmap = pixmap
        self.default_color = color
        if not pixmap is not None and pixmap.isNull():
            self.default_pixmap = self._scaleToWidget(pixmap)
        else:
            self.default_pixmap = None
        self.update()

    
    def setBackground(self = None, pixmap = None):
        '''切歌时调用，设置新背景。

        参数:
            pixmap (QPixmap): 原始未缩放的封面背景图。
        返回:
            无。
        '''
        if pixmap is None or pixmap.isNull():
            self.sourcePixmap = None
            self.pixmap = None
        else:
            self.sourcePixmap = pixmap
            self.pixmap = self._scaleToWidget(pixmap)
        self.update()

    
    def _scaleToWidget(self = None, source = None):
        '''将原始图等比放大缩放到覆盖当前控件区域。

        参数:
            source (QPixmap): 原始未缩放图。
        返回:
            QPixmap: 缩放后的 pixmap；控件尺寸无效时原样返回。
        '''
        if source is None and source.isNull() and self.width() <= 0 or self.height() <= 0:
            return source
        return None.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

    
    def resizeEvent(self = None, event = None):
        '''尺寸变化时从原始图重新缩放，避免对已缩放图链式缩放。

        参数:
            event (QResizeEvent): Qt 尺寸变化事件。
        返回:
            无。
        '''
        if self.sourcePixmap:
            self.pixmap = self._scaleToWidget(self.sourcePixmap)
        if self.default_source_pixmap:
            self.default_pixmap = self._scaleToWidget(self.default_source_pixmap)
        super().resizeEvent(event)

    
    def paintEvent(self, event):
        '''软件绘制背景：优先封面背景图，其次默认图，最后纯色。

        参数:
            event (QPaintEvent): Qt 绘制事件。
        返回:
            无。
        '''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self.pixmap:
            painter.drawPixmap(self.rect(), self.pixmap)
        elif self.default_pixmap:
            painter.drawPixmap(self.rect(), self.default_pixmap)
        else:
            painter.fillRect(self.rect(), self.default_color)
        painter.end()

    __classcell__ = None

