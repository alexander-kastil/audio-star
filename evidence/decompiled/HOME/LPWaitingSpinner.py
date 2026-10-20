# Source Generated with Decompyle++
# File: LPWaitingSpinner.pyc (Python 3.9)

import math
from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

class LPWaitingSpinner(QWidget):
    '''WaitingSpinner is a highly configurable, custom spinner widget.'''
    
    def __init__(self = None, parent = None, center_on_parent = None, disable_parent_when_spinning = None, modality = None, roundness = None, fade = None, lines = None, line_length = None, line_width = None, radius = None, speed = (True, False, Qt.WindowModality.NonModal, 100, 80, 20, 10, 2, 10, math.pi / 2, QColor(0, 0, 0)), color = ({
        'parent': QWidget,
        'center_on_parent': bool,
        'disable_parent_when_spinning': bool,
        'modality': Qt.WindowModality,
        'roundness': float,
        'fade': float,
        'lines': int,
        'line_length': int,
        'line_width': int,
        'radius': int,
        'speed': float,
        'color': QColor,
        'return': None },)):
        super().__init__(parent)
        self._center_on_parent = center_on_parent
        self._disable_parent_when_spinning = disable_parent_when_spinning
        self._color = color
        self._roundness = roundness
        self._minimum_trail_opacity = math.pi
        self._trail_fade_percentage = fade
        self._revolutions_per_second = speed
        self._number_of_lines = lines
        self._line_length = line_length
        self._line_width = line_width
        self._inner_radius = radius
        self._current_counter = 0
        self._is_spinning = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._update_size()
        self._update_timer()
        self.hide()
        self.setWindowModality(modality)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    
    def paintEvent(self = None, _ = None):
        '''Paint the WaitingSpinner.'''
        self._update_position()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if self._current_counter >= self._number_of_lines:
            self._current_counter = 0
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(self._number_of_lines):
            painter.save()
            painter.translate(self._inner_radius + self._line_length, self._inner_radius + self._line_length)
            rotate_angle = 360 * i / self._number_of_lines
            painter.rotate(rotate_angle)
            painter.translate(self._inner_radius, 0)
            distance = self._line_count_distance_from_primary(i, self._current_counter, self._number_of_lines)
            color = self._current_line_color(distance, self._number_of_lines, self._trail_fade_percentage, self._minimum_trail_opacity, self._color)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(0, -(self._line_width) // 2, self._line_length, self._line_width), self._roundness, self._roundness, Qt.SizeMode.RelativeSize)
            painter.restore()

    
    def start(self = None):
        '''Show and start spinning the WaitingSpinner.'''
        self._update_position()
        self._is_spinning = True
        self.show()
        if self.parentWidget and self._disable_parent_when_spinning:
            self.parentWidget().setEnabled(False)
        if not self._timer.isActive():
            self._timer.start()
            self._current_counter = 0

    
    def stop(self = None):
        '''Hide and stop spinning the WaitingSpinner.'''
        self._is_spinning = False
        self.hide()
        if self.parentWidget() and self._disable_parent_when_spinning:
            self.parentWidget().setEnabled(True)
        if self._timer.isActive():
            self._timer.stop()
            self._current_counter = 0

    
    def color(self = None):
        '''Return color of WaitingSpinner.'''
        return self._color

    color = None(color)
    
    def color(self = None, color = None):
        '''Set color of WaitingSpinner.'''
        self._color = QColor(color)

    color = None(color)
    
    def roundness(self = None):
        '''Return roundness of WaitingSpinner.'''
        return self._roundness

    roundness = None(roundness)
    
    def roundness(self = None, roundness = None):
        '''Set color of WaitingSpinner.'''
        self._roundness = max(0, min(100, roundness))

    roundness = None(roundness)
    
    def minimum_trail_opacity(self = None):
        '''Return minimum trail opacity of WaitingSpinner.'''
        return self._minimum_trail_opacity

    minimum_trail_opacity = None(minimum_trail_opacity)
    
    def minimum_trail_opacity(self = None, minimum_trail_opacity = None):
        '''Set minimum trail opacity of WaitingSpinner.'''
        self._minimum_trail_opacity = minimum_trail_opacity

    minimum_trail_opacity = None(minimum_trail_opacity)
    
    def trail_fade_percentage(self = None):
        '''Return trail fade percentage of WaitingSpinner.'''
        return self._trail_fade_percentage

    trail_fade_percentage = None(trail_fade_percentage)
    
    def trail_fade_percentage(self = None, trail = None):
        '''Set trail fade percentage of WaitingSpinner.'''
        self._trail_fade_percentage = trail

    trail_fade_percentage = None(trail_fade_percentage)
    
    def revolutions_per_second(self = None):
        '''Return revolutions per second of WaitingSpinner.'''
        return self._revolutions_per_second

    revolutions_per_second = None(revolutions_per_second)
    
    def revolutions_per_second(self = None, revolutions_per_second = None):
        '''Set revolutions per second of WaitingSpinner.'''
        self._revolutions_per_second = revolutions_per_second
        self._update_timer()

    revolutions_per_second = None(revolutions_per_second)
    
    def number_of_lines(self = None):
        '''Return number of lines of WaitingSpinner.'''
        return self._number_of_lines

    number_of_lines = None(number_of_lines)
    
    def number_of_lines(self = None, lines = None):
        '''Set number of lines of WaitingSpinner.'''
        self._number_of_lines = lines
        self._current_counter = 0
        self._update_timer()

    number_of_lines = None(number_of_lines)
    
    def line_length(self = None):
        '''Return line length of WaitingSpinner.'''
        return self._line_length

    line_length = None(line_length)
    
    def line_length(self = None, length = None):
        '''Set line length of WaitingSpinner.'''
        self._line_length = length
        self._update_size()

    line_length = None(line_length)
    
    def line_width(self = None):
        '''Return line width of WaitingSpinner.'''
        return self._line_width

    line_width = None(line_width)
    
    def line_width(self = None, width = None):
        '''Set line width of WaitingSpinner.'''
        self._line_width = width
        self._update_size()

    line_width = None(line_width)
    
    def inner_radius(self = None):
        '''Return inner radius size of WaitingSpinner.'''
        return self._inner_radius

    inner_radius = None(inner_radius)
    
    def inner_radius(self = None, radius = None):
        '''Set inner radius size of WaitingSpinner.'''
        self._inner_radius = radius
        self._update_size()

    inner_radius = None(inner_radius)
    
    def is_spinning(self = None):
        '''Return actual spinning status of WaitingSpinner.'''
        return self._is_spinning

    is_spinning = None(is_spinning)
    
    def _rotate(self = None):
        '''Rotate the WaitingSpinner.'''
        self._current_counter += 1
        if self._current_counter >= self._number_of_lines:
            self._current_counter = 0
        self.update()

    
    def _update_size(self = None):
        '''Update the size of the WaitingSpinner.'''
        size = (self._inner_radius + self._line_length) * 2
        self.setFixedSize(size, size)

    
    def _update_timer(self = None):
        '''Update the spinning speed of the WaitingSpinner.'''
        self._timer.setInterval(int(1000 / (self._number_of_lines * self._revolutions_per_second)))

    
    def _update_position(self = None):
        '''Center WaitingSpinner on parent widget.'''
        if self.parentWidget() and self._center_on_parent:
            self.move((self.parentWidget().width() - self.width()) // 2, (self.parentWidget().height() - self.height()) // 2)

    
    def _line_count_distance_from_primary(current = None, primary = None, total_nr_of_lines = staticmethod):
        '''Return the amount of lines from _current_counter.'''
        distance = primary - current
        if distance < 0:
            distance += total_nr_of_lines
        return distance

    _line_count_distance_from_primary = None(_line_count_distance_from_primary)
    
    def _current_line_color(count_distance, total_nr_of_lines = None, trail_fade_perc = None, min_opacity = staticmethod, color_input = {
        'count_distance': int,
        'total_nr_of_lines': int,
        'trail_fade_perc': float,
        'min_opacity': float,
        'color_input': QColor,
        'return': QColor }):
        '''Returns the current color for the WaitingSpinner.'''
        color = QColor(color_input)
        if count_distance == 0:
            return color
        min_alpha_f = None / 100
        distance_threshold = int(math.ceil((total_nr_of_lines - 1) * trail_fade_perc / 100))
        if count_distance > distance_threshold:
            color.setAlphaF(min_alpha_f)
        else:
            alpha_diff = color.alphaF() - min_alpha_f
            gradient = alpha_diff / float(distance_threshold + 1)
            result_alpha = color.alphaF() - gradient * count_distance
            result_alpha = min(1, max(0, result_alpha))
            color.setAlphaF(result_alpha)
        return color

    _current_line_color = None(_current_line_color)
    __classcell__ = None

