# Source Generated with Decompyle++
# File: LPPlayViewFullScreenContentController.pyc (Python 3.9)

'''
@Time ： 2025/9/25 11:16
@Auth ： Chris
@File ：LPPlayViewFullScreenContentController.py
@Desc:
'''
from string import Template
from threading import Thread
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication, QVariantAnimation, QEasingCurve, QPoint, QSize, QTimer
from PyQt6.QtGui import QFont, QPixmap, QMovie, QFontMetricsF
from PyQt6.QtWidgets import QWidget, QButtonGroup, QLabel, QFrame, QHBoxLayout
import LPGlobalUI
from HOME.PlayView import LPPlayViewUtil
from HOME.LPPlaybackLayoutPolicy import useCompactPlayViewLayout
from HOME.PlayView.LPPlayViewQueueSectionController import LPPlayViewQueueSectionController
from HOME.PlayView.LPPlayViewTrackLabel import LPPlayViewTrackLabel
from HOME.PlayView.UI.LPPlayViewFullScreenQueueContent_ui import Ui_playviewFullScreenQueueWidget
from HOME.PlayView.UI.LPPlayViewQueueSection_ui import Ui_playviewQueueSection
from HOME.Queue.LPQueueViewController import LPQueueViewController
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import PlayView_Format_Title, scale, PlayView_Track_Title, Big_Title, Sub_Title, Main_Text
from LPClientFramework.LPUtility import logger
ALBUM_TITLE_BOTTOM_GAP = 16
TRACK_TITLE_ROW_WIDTH_RATIO = 0.8

class LPPlayViewFullScreenContentController(QWidget):
    updateUISignal = pyqtSignal(object)
    updateBGSignal = pyqtSignal(object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.playView = parent
        self.playingMovie = QMovie(LPGlobalUI.imagePath('write_playing.gif'))
        self.pausePixmap = QPixmap(LPGlobalUI.imagePath('write_pause.png'))
        self.updateUISignal.connect(self._updateContent)
        self.playView.updateCoverImageSignal.connect(self._updateQTCoverImage)
        self.playView.updateTitleSignal.connect(self._updateQTTitle)
        self.playView.updatePlayStateSignal.connect(self._updateQTMovie)
        self.playView.updateFullScreenSectionSignal.connect(self._updateSection)
        self.playView.updateFormatSignal.connect(self._updateFormat)
        self.queueListView = None
        self.currentPage = None
        self.isCompactLayout = False
        self.coverBaseSide = 0
        self.coverCurrentSide = 0
        self.currentCoverPixmap = None
        self.coverScaleAnimation = None

    
    def setupUi(self = None, ui = None):
