# Source Generated with Decompyle++
# File: LPProgressSlider.pyc (Python 3.9)

from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6.QtWidgets import QSlider, QStyleOptionSlider
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPixmap
import LPGlobalUI
from PyQt6.QtCore import QEvent, QSize, QRectF, pyqtSignal
import time
import threading

class LPProgressSlider(QSlider):
    updateUISignal = pyqtSignal()
    userUpdateValueChanged = pyqtSignal(object)
    userUpdateValueChanging = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        '''
        初始化播放进度条。

        参数:
            parent: Qt 父控件。
        返回值:
            None。
        '''
        super(LPProgressSlider, self).__init__(parent)
        self.installEventFilter(self)
        self.wheelHandleFunc = None
        self.isWheelThreadActive = False
        self.lastWheelVolume = -1
        self.wheelUpdateThread = None
        self.updateUISignal.connect(self.updateUISlot)
        self.valueChanged.connect(self.valueChangedSlot)
        self.sliderMoved.connect(self.sliderMovedSlot)
        self.sliderPressed.connect(self.sliderPressedSlot)
        self.sliderReleased.connect(self.sliderReleasedSlot)
        self.isHover = False
        self.userIsOperate = False
        self.alwaysShowHandle = False
        self.useFixedTrackGradient = False
        barStartColor = QColor(153, 150, 244)
        barEndColor = QColor(LPGlobalUI.THEME_ACCENT_COLOR)
        self._trackStartColor = barStartColor
        self._trackEndColor = barEndColor
        self._trackBackgroundColor = QColor(255, 255, 255, 51)
        self._trackHandlePixmap = QPixmap(LPGlobalUI.imagePath('miniBar/sliderBar.png'))
        self.baseStylesheet = '\nQSlider::groove:horizontal{\nheight: 4px;\nleft: 10px;\nright: 10px;\nborder:0px;\nborder-radius: 2px;\nbackground: rgba(255,255,255,0.2);\n}\n'
        self.hoverStyleSheet = '\n        QSlider::handle:horizontal{\nmargin-top: -20px;\nmargin-left: 0px;\nmargin-bottom: -20px;\nmargin-right: 0px;\nimage:url("%s");\n}\nQSlider::sub-page:horizontal{\nborder:0px;\nborder-radius: 2px;\nbackground: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s);\n}\n        ' % (LPGlobalUI.imagePath('miniBar/sliderBar.png'), barStartColor.name(), barEndColor.name())
        self.normalStyleSheet = '\nQSlider::sub-page:horizontal{\nborder:0px;\nborder-radius: 2px;\nbackground: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s);\n}\n        QSlider::handle:horizontal{\nmargin-top: -20px;\nmargin-left: 0px;\nmargin-bottom: -20px;\nmargin-right: 0px;\nimage: none;\n}\n        ' % (barStartColor.name(), barEndColor.name())
        self.zeroStyleSheet = '\nQSlider::sub-page:horizontal{\nborder:0px;\nborder-radius: 2px;\nbackground: transparent;\n}\n        QSlider::handle:horizontal{\nmargin-top: -20px;\nmargin-left: 0px;\nmargin-bottom: -20px;\nmargin-right: 0px;\nimage: none;\n}\n        '

    
    def wheelThreadMethod(self):
        if self.isWheelThreadActive:
            if self.lastWheelVolume != self.value():
                self.lastWheelVolume = self.value()
                self.wheelHandleFunc()
            else:
                self.userIsOperate = False
                self.isWheelThreadActive = False
                self.lastWheelVolume = -1
        else:
            time.sleep(0.2)

    
    def updateUserUpdateTimestamp(self):
        self.lastUserUpdateTimestamp = time.time()
        if self.preventUpdateThread is None:
            self.preventUpdateThread = threading.Thread(self.preventUpdateThreadMethod, **('target',))
            self.preventUpdateThread.start()

    
    def setValue(self = None, value = None):
        if self.userIsOperate == False:
            super().setValue(value)

    
    def forceSetValue(self = None, value = None):
        super().setValue(value)

    
    def valueChangedSlot(self, value):
        self.updateUISignal.emit()

    
    def updateUISlot(self):
        '''
        根据 hover 和进度状态刷新进度条 UI。

        参数:
            无。
        返回值:
            None。
        '''
        if self.useFixedTrackGradient:
            self.setStyleSheet('')
            self.update()
            return None
        if None.isHover is True or self.alwaysShowHandle is True:
            self.setStyleSheet(self.baseStylesheet + self.hoverStyleSheet)
        elif self.value() != 0:
            self.setStyleSheet(self.baseStylesheet + self.normalStyleSheet)
        else:
            self.setStyleSheet(self.baseStylesheet + self.zeroStyleSheet)

    
    def eventFilter(self = None, obj = None, event = None):
        if self.isEnabled():
            if event.type() == QEvent.Type.Enter:
                self.isHover = True
                self.updateUISignal.emit()
                return True
            if None.type() == QEvent.Type.Leave:
                self.isHover = False
                self.updateUISignal.emit()
                return True
            if None.type() == QEvent.Type.MouseButtonPress:
                self.userIsOperate = True
                val = self.pixelPosToRangeValue(event.pos())
                self.setSliderPosition(val)
                self.userUpdateValueChanging.emit(val)
            if event.type() == QEvent.Type.Wheel:
                if self.wheelHandleFunc is None:
                    return True
                self.userIsOperate = None
                if self.isWheelThreadActive is False:
                    self.isWheelThreadActive = True
                    self.wheelUpdateThread = threading.Thread(self.wheelThreadMethod, **('target',))
                    self.wheelUpdateThread.start()
        return super(LPProgressSlider, self).eventFilter(obj, event)

    
    def paintEvent(self = None, event = None):
        '''
        绘制固定整轨渐变坐标系的播放进度条。

        参数:
            event: Qt 绘制事件。
        返回值:
            None。
        '''
        if not self.useFixedTrackGradient:
            super().paintEvent(event)
            return None
        painter = None(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grooveRect = self._trackGrooveRect()
        if grooveRect.width() <= 0 or grooveRect.height() <= 0:
            painter.end()
            return None
        groovePath = None()
        groovePath.addRoundedRect(grooveRect, 2, 2)
        painter.fillPath(groovePath, self._trackBackgroundColor)
        progressRatio = self._trackProgressRatio()
        if progressRatio > 0:
            progressRect = QRectF(grooveRect.left(), grooveRect.top(), grooveRect.width() * progressRatio, grooveRect.height())
            progressPath = QPainterPath()
            progressPath.addRoundedRect(progressRect, 2, 2)
            gradient = QLinearGradient(grooveRect.left(), grooveRect.center().y(), grooveRect.right(), grooveRect.center().y())
            gradient.setColorAt(0, self._trackStartColor)
            gradient.setColorAt(1, self._trackEndColor)
            painter.fillPath(progressPath, gradient)
        if self.isHover is True or self.alwaysShowHandle is True:
            self._paintTrackHandle(painter, grooveRect, progressRatio)
        painter.end()

    
    def _trackGrooveRect(self):
        '''
        获取自绘进度条轨道区域。

        参数:
            无。
        返回值:
            QRectF: 轨道绘制区域。
        '''
        horizontalPadding = 10
        grooveHeight = 4
        return QRectF(horizontalPadding, (self.height() - grooveHeight) / 2, max(0, self.width() - horizontalPadding * 2), grooveHeight)

    
    def _trackProgressRatio(self):
        '''
        获取当前进度在整条轨道中的比例。

        参数:
            无。
        返回值:
            float: 0 到 1 之间的进度比例。
        '''
        valueRange = self.maximum() - self.minimum()
        if valueRange <= 0:
            return 0
        ratio = (None.value() - self.minimum()) / valueRange
        return max(0, min(1, ratio))

    
    def _paintTrackHandle(self, painter, grooveRect, progressRatio):
        '''
        绘制 hover 或强制展示时的进度条拖拽点。

        参数:
            painter: 当前 QPainter。
            grooveRect: 轨道区域。
            progressRatio: 当前进度比例。
        返回值:
            None。
        '''
        if self._trackHandlePixmap.isNull():
            return None
        handleSize = None._trackHandlePixmap.size()
        handleX = grooveRect.left() + grooveRect.width() * progressRatio - handleSize.width() / 2
        handleY = (self.height() - handleSize.height()) / 2
        painter.drawPixmap(int(handleX), int(handleY), self._trackHandlePixmap)

    
    def sliderMovedSlot(self, value):
        self.userUpdateValueChanging.emit(value)

    
    def sliderPressedSlot(self):
        self.userIsOperate = True
        self.userUpdateValueChanging.emit(self.value())

    
    def sliderReleasedSlot(self):
        self.userIsOperate = False
        self.userUpdateValueChanged.emit(self.value())

    
    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QtWidgets.QStyle.ComplexControl.CC_Slider, opt, QtWidgets.QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QtWidgets.QStyle.ComplexControl.CC_Slider, opt, QtWidgets.QStyle.SubControl.SC_SliderHandle, self)
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = (gr.right() - sliderLength) + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = (gr.bottom() - sliderLength) + 1
        pr = (pos - sr.center()) + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Orientation.Horizontal else pr.y()
        return QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin, sliderMax - sliderMin, opt.upsideDown)

    __classcell__ = None

