# Source Generated with Decompyle++
# File: LPTaskButton.pyc (Python 3.9)

'''
@Time ： 2025/5/9 17:13
@Auth ： Chris
@File ：LPTaskButton.py
@Desc:
'''
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPixmap, QPainter, QTransform
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, Qt, QTimer

class TaskButton(QPushButton):
    '''
    用之前先setup
    '''
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self._angle = 0
        self.currentPix = None
        self.animation = QPropertyAnimation(self, b'angle')
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)

    
    def setup(self, loadingIcon, failedIcon, successIcon, idleText, loadingText, failedText, successText, iconSize = (20,)):
        self.iconSize = iconSize
        self.loadingPix = QPixmap(loadingIcon).scaled(iconSize, iconSize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.failedPix = QPixmap(failedIcon).scaled(iconSize, iconSize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.successPix = QPixmap(successIcon).scaled(iconSize, iconSize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.idleText = idleText
        self.loadingText = loadingText
        self.failedText = failedText
        self.successText = successText
        self.state = 'idle'
        self.text = self.idleText
        self.setIdle()
        self.setMinimumHeight(iconSize + 12)

    
    def setAngle(self, angle):
        self._angle = angle
        self.update()

    
    def getAngle(self):
        return self._angle

    angle = pyqtProperty(float, getAngle, setAngle, **('fget', 'fset'))
    
    def paintEvent(self = None, event = None):
        super().paintEvent(event)
        if not self.currentPix:
            return None
        painter = None(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        font = self.font()
        font.setBold(True)
        painter.setFont(font)
        text_metrics = painter.fontMetrics()
        textWidth = text_metrics.horizontalAdvance(self.text)
        textHeight = text_metrics.height()
        if self.state != 'idle':
            spacing = 8
            iconSize = self.iconSize
            totalWidth = iconSize + spacing + textWidth
            startX = (self.width() - totalWidth) // 2
            iconY = (self.height() - iconSize) // 2
            textY = (self.height() + text_metrics.ascent() - text_metrics.descent()) // 2
            center_x = startX + iconSize / 2
            center_y = iconY + iconSize / 2
            painter.save()
            transform = QTransform()
            transform.translate(center_x, center_y)
            if self.state == 'loading':
                transform.rotate(self._angle)
            transform.translate(-(self.iconSize) / 2, -(self.iconSize) / 2)
            painter.setTransform(transform)
            painter.drawPixmap(0, 0, self.iconSize, self.iconSize, self.currentPix)
            painter.restore()
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(startX + iconSize + spacing, textY, self.text)
        else:
            totalWidth = textWidth
            startX = (self.width() - totalWidth) // 2
            textY = (self.height() + text_metrics.ascent() - text_metrics.descent()) // 2
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(startX, textY, self.text)

    
    def setIdle(self):
        self.state = 'idle'
        self.text = self.idleText
        self.currentPix = QPixmap()
        self.setEnabled(True)
        self.setStyleSheet('background-color: rgba(77, 86, 219, 255);')
        self.animation.stop()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update()

    
    def setLoading(self):
        self.state = 'loading'
        self.text = self.loadingText
        self.currentPix = self.loadingPix
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setEnabled(False)
        self.setStyleSheet('background-color: rgba(77, 86, 219, 128);')
        self.animation.start()
        self.update()

    
    def setFailed(self):
        self.state = 'failed'
        self.text = self.failedText
        self.currentPix = self.failedPix
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setEnabled(False)
        self.setStyleSheet('background-color: transparent;')
        self.animation.stop()
        self.update()

    
    def setSuccess(self):
        self.state = 'success'
        self.text = self.successText
        self.currentPix = self.successPix
        self.setStyleSheet('background-color: transparent;')
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setEnabled(False)
        self.animation.stop()
        self.update()

    __classcell__ = None

