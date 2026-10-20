# Source Generated with Decompyle++
# File: LPSignalBus.pyc (Python 3.9)

'''
@Time ： 2025/12/9 11:36
@Auth ： Chris
@File ：LPSignalBus.py
@Desc:
'''
from PyQt6.QtCore import QObject, pyqtSignal

class LPSignalBus(QObject):
    Network_Changed_Signal = pyqtSignal(object, object)
    Clear_Device_Dashboard_Signal = pyqtSignal()
    DeviceDashboardProjectionChanged = pyqtSignal(object)

