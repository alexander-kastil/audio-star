# Source Generated with Decompyle++
# File: LPVolumeSlider.pyc (Python 3.9)

from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6.QtWidgets import QSlider, QStyleOptionSlider
import LPGlobalUI
from PyQt6.QtCore import QEvent, QSize, pyqtSignal
import time
import threading

class LPVolumeSlider(QSlider):
    updateUISignal = pyqtSignal()
    userUpdateValueChanged = pyqtSignal(object)
    userUpdateValueChanging = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        super(LPVolumeSlider, self).__init__(parent)
        self.installEventFilter(self)
        self.isWheelThreadActive = False
        self.lastWheelVolume = -1
        self.wheelUpdateThread = None
        self.updateUISignal.connect(self.updateUISlot)
        self.valueChanged.connect(self.valueChangedSlot)
        self.sliderMoved.connect(self.sliderMovedSlot)
        self.sliderPressed.connect(self.sliderPressedSlot)
        self.sliderReleased.connect(self.sliderReleasedSlot)
        self.lastDragTimestamp = time.time()
        self.lastDragVolume = None
        self.isHover = False
        self.isMuted = False
        self.isLocked = False
        self.userIsOperate = False
        self.baseStylesheet = '\n        QSlider::groove:vertical{\n            width: 4px;\n            top: 10px;\n            bottom: 10px;\n            border: 0px;\n            border-radius: 2px;\n            background: rgba(255,255,255,0.2);\n        }\n        '
        barColor = LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI
        self.hoverStyleSheet = '\n        QSlider::handle:vertical{\n            margin-left: -20px;\n            margin-top: 0px;\n            margin-right: -20px;\n            margin-bottom: 0px;\n            image: url("%s");\n        }\nQSlider::add-page:vertical{\n            border: 0px;\n            border-radius: 2px;\n            background: %s;\n        }\n        ' % (LPGlobalUI.imagePath('miniBar/sliderBar.png'), barColor.name())
        defaultColor = 'rgba(255,255,255,0.65)'
        self.normalStyleSheet = '\n        QSlider::add-page:vertical{\n            border: 0px;\n            border-radius: 2px;\n            background: %s;\n        }\n        QSlider::handle:vertical{\n            margin-left: -20px;\n            margin-top: 0px;\n            margin-right: -20px;\n            margin-bottom: 0px;\n            image: none;\n        }\n        ' % defaultColor
        mutedColor = 'rgba(255,255,255,0.35)'
        self.mutedStyleSheet = '\n        QSlider::add-page:vertical{\n            border: 0px;\n            border-radius: 2px;\n            background: %s;\n        }\n        QSlider::handle:vertical{\n            margin-left: -20px;\n            margin-top: 0px;\n            margin-right: -20px;\n            margin-bottom: 0px;\n            image: none;\n        }\n        ' % mutedColor
        self.zeroStyleSheet = '\n        QSlider::add-page:vertical{\n            border: 0px;\n            border-radius: 2px;\n            background: transparent;\n        }\n        QSlider::handle:vertical{\n            margin-left: -20px;\n            margin-top: 0px;\n            margin-right: -20px;\n            margin-bottom: 0px;\n            image: none;\n        }\n        '

    
    def wheelThreadMethod(self):
        if self.isWheelThreadActive:
            if self.lastWheelVolume != self.value():
                self.lastWheelVolume = self.value()
                self.userUpdateValueChanged.emit(self.lastWheelVolume)
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
            super().setValue(int(value))

    
    def forceSetValue(self = None, value = None):
        super().setValue(int(value))

    
    def valueChangedSlot(self, value):
        print(f'''value={value}''')
        self.updateUISignal.emit()

    
    def updateUISlot(self):
        if self.value() == 0:
            self.setStyleSheet(self.baseStylesheet + self.zeroStyleSheet)
            return None
        if None.isMuted or self.isLocked:
            self.setStyleSheet(self.baseStylesheet + self.mutedStyleSheet)
            return None
        if None.isHover is True:
            self.setStyleSheet(self.baseStylesheet + self.hoverStyleSheet)
        else:
            self.setStyleSheet(self.baseStylesheet + self.normalStyleSheet)

    
    def enableHover(self, hover):
        self.isHover = hover
        self.updateUISignal.emit()

    
    def setMuted(self, muted):
        muted = bool(muted)
        if self.isMuted == muted:
            return None
        self.isMuted = None
        self.updateUISignal.emit()

    
    def setLocked(self, locked):
        locked = bool(locked)
        if self.isLocked == locked:
            return None
        self.isLocked = None
        self.updateUISignal.emit()

    
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
                self.userIsOperate = True
                if self.isWheelThreadActive is False:
                    self.isWheelThreadActive = True
                    self.wheelUpdateThread = threading.Thread(self.wheelThreadMethod, **('target',))
                    self.wheelUpdateThread.start()
        return super(LPVolumeSlider, self).eventFilter(obj, event)

    
    def sliderMovedSlot(self, value):
        if time.time() - self.lastDragTimestamp > 0.15 and self.lastDragVolume != value:
            self.userUpdateValueChanged.emit(value)
            self.lastDragTimestamp = time.time()
            self.lastDragVolume = value
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

