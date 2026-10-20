# Source Generated with Decompyle++
# File: LPToggle.pyc (Python 3.9)

import sys
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF, QRectF, QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QEvent
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter
import LPGlobalUI

class LPToggle(QCheckBox):
    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_grey_pen = QPen(Qt.GlobalColor.transparent)
    
    def __init__(self = None, parent = None, bar_color = None, checked_color = None, handle_color = None):
        super().__init__(parent)
        self.checked_color = checked_color
        self._checked_color = QColor(LPGlobalUI.THEME_HIGH_COLOR)
        self._checked_hover_color = QColor(checked_color)
        self._bar_brush = QBrush(bar_color)
        self._bar_hover_brush = QBrush(bar_color.lighter())
        self._bar_checked_brush = QBrush(self._checked_color)
        self._bar_checked_hover_brush = QBrush(self._checked_hover_color)
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(handle_color)
        self.isHover = False
        self.installEventFilter(self)
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0
        self.stateChanged.connect(self.handle_state_change)

    
    def setCheckedColor(self, color):
        '''
        设置开关启用且开启时的常态和悬停颜色。

        参数:
            color (QColor): 开关开启状态使用的颜色。
        返回:
            无
        '''
        checkedColor = QColor(color)
        self.checked_color = checkedColor
        self._checked_color = checkedColor
        self._checked_hover_color = checkedColor
        if self.isEnabled():
            self._bar_checked_brush = QBrush(self._checked_color)
            self._bar_checked_hover_brush = QBrush(self._checked_hover_color)
        self.update()

    
    def sizeHint(self):
        return QSize(58, 45)

    
    def hitButton(self = None, pos = None):
        return self.rect().contains(pos)

    
    def paintEvent(self = None, e = None):
        contRect = self.rect()
        handleRadius = round(0.4 * contRect.height())
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self._transparent_pen)
        barRect = QRectF(0, 0, contRect.width() - 2, contRect.height() - 2)
        barRect.moveCenter(QPointF(contRect.center()))
        rounding = barRect.height() / 2
        trailLength = contRect.width() - 2 * handleRadius
        xPos = contRect.x() + handleRadius + trailLength * self._handle_position
        if self.isChecked():
            if self.isHover:
                p.setBrush(self._bar_checked_hover_brush)
            else:
                p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
            xPos = xPos - 2
        elif self.isHover:
            p.setBrush(self._bar_hover_brush)
        else:
            p.setBrush(self._bar_brush)
        p.drawRoundedRect(barRect, rounding, rounding)
        p.setPen(self._light_grey_pen)
        p.setBrush(self._handle_brush)
        xPos = xPos + 2
        p.drawEllipse(QPointF(xPos, barRect.center().y()), handleRadius, handleRadius)
        p.end()

    
    def handle_state_change(self, value):
        self._handle_position = 1 if value else 0

    
    def handle_position(self):
        return self._handle_position

    handle_position = property(handle_position)
    
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    handle_position = handle_position.setter(handle_position)
    
    def pulse_radius(self):
        return self._pulse_radius

    pulse_radius = property(pulse_radius)
    
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()

    pulse_radius = pulse_radius.setter(pulse_radius)
    
    def eventFilter(self = None, obj = None, event = None):
        needRefresh = False
        if event.type() == QEvent.Type.Enter:
            if self.isHover is False:
                needRefresh = True
            self.isHover = True
            if needRefresh:
                self.update()
            return True
        if None.type() == QEvent.Type.Leave:
            if self.isHover is True:
                needRefresh = True
            self.isHover = False
            if needRefresh:
                self.update()
            return True
        return None(LPToggle, self).eventFilter(obj, event)

    
    def setEnabled(self = None, enabled = None):
        ''' 重载 setEnabled 方法，禁用时改变外观 '''
        super().setEnabled(enabled)
        if not enabled:
            self._bar_checked_brush = QBrush(LPGlobalUI.THEME_HIGH_HIGH_DISABLED_COLOR)
            self._bar_checked_hover_brush = QBrush(LPGlobalUI.THEME_HIGH_HIGH_DISABLED_COLOR)
        else:
            self._bar_checked_brush = QBrush(self._checked_color)
            self._bar_checked_hover_brush = QBrush(self._checked_hover_color)
        self.repaint()

    __classcell__ = None

