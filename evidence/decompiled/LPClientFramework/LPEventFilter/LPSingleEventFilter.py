# Source Generated with Decompyle++
# File: LPSingleEventFilter.pyc (Python 3.9)

from PyQt6.QtCore import QObject

class LPSingleEventFilter(QObject):
    
    def __init__(self = None, widget = None):
        super().__init__(widget)
        if hasattr(widget, 'lpEventFilter') and widget.lpEventFilter:
            if hasattr(widget.lpEventFilter, 'movie'):
                widget.lpEventFilter.movie.stop()
            widget.removeEventFilter(widget.lpEventFilter)
            widget.lpEventFilter.deleteLater()
        widget.installEventFilter(self)
        setattr(widget, 'lpEventFilter', self)

    __classcell__ = None

