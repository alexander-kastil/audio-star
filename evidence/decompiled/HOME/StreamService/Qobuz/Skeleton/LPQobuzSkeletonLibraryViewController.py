# Source Generated with Decompyle++
# File: LPQobuzSkeletonLibraryViewController.pyc (Python 3.9)

'''
@Time ： 2025/6/6 14:33
@Auth ： Chris
@File ：LPQobuzLibraryViewController.py
@Desc:
'''
import re
from string import Template
from PyQt6.QtCore import QTimer, Qt, QRectF, QObject
from PyQt6.QtGui import QLinearGradient, QBrush, QPainterPath, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QFrame
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class ShimmerEffect(QObject):
    
    def __init__(self = None, widgets = None, parent = None):
        super().__init__(parent)
        self.widgets = widgets
        self.gradient_pos = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(30)

    
    def update_animation(self):
