# Source Generated with Decompyle++
# File: LPGifPlayButtonEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QEvent, QSize, Qt, QRect
from PyQt6.QtGui import QMovie, QIcon, QPixmap, QPainter, QPainterPath
import LPGlobalUI
from LPClientFramework.LPEventFilter.LPSingleEventFilter import LPSingleEventFilter

class LPGifPlayButtonEventFilter(LPSingleEventFilter):
    
    def __init__(self = None, widget = None, gifPath = None, backgroundColor = None, effect = None):
        super().__init__(widget)
        self.effect = effect if effect else 'bigger'
        self.button = widget
        self.frame_cache = { }
        self.backgroundColor = backgroundColor
        self.movie = QMovie(LPGlobalUI.imagePath(gifPath))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start()

    
    def onFrameChanged(self):
        frame_number = self.movie.currentFrameNumber()
        if frame_number in self.frame_cache:
            pass
        else:
            frame = self.movie.currentPixmap()
            if frame.isNull():
                return None
            pixmap = None.create_circular_pixmap(frame, self.button.size())
            self.frame_cache[frame_number] = pixmap
        self.button.update()

    
    def eventFilter(self = None, obj = None, event = None):
        if self.button.isEnabled():
            if event.type() == QEvent.Type.Enter:
                if self.effect == 'bigger':
                    self.button.setIconSize(QSize(self.button.iconSize().width() + 2, self.button.iconSize().height() + 2))
                return True
            if None.type() == QEvent.Type.Leave:
                if self.effect == 'bigger':
                    self.button.setIconSize(QSize(self.button.iconSize().width() - 2, self.button.iconSize().height() - 2))
                return True
            if None == self.button and event.type() == QEvent.Type.Paint:
                frame_number = self.movie.currentFrameNumber()
                if frame_number in self.frame_cache:
                    self.button.setIcon(QIcon(self.frame_cache[frame_number]))
        return super().eventFilter(obj, event)

    
    def create_circular_pixmap(self, pixmap, size):
        '''创建带白色背景的圆形 QPixmap'''
        target_size = min(size.width(), size.height())
        circular_pixmap = QPixmap(target_size, target_size)
        circular_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.backgroundColor)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, target_size, target_size)
        scaled_pixmap = pixmap.scaled(target_size, target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        clip_path = QPainterPath()
        clip_path.addEllipse(0, 0, target_size, target_size)
        painter.setClipPath(clip_path)
        painter.drawPixmap(QRect(0, 0, target_size, target_size), scaled_pixmap)
        painter.end()
        return circular_pixmap

    __classcell__ = None

