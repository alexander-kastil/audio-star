# Source Generated with Decompyle++
# File: LPPlayViewQueueSectionController.pyc (Python 3.9)

'''
@Time ： 2025/9/24 13:31
@Auth ： Chris
@File ：LPPlayViewQueueSectionController.py
@Desc:
'''
import threading
from html import escape
from string import Template
from PyQt6.QtCore import pyqtSignal, QCoreApplication, pyqtSlot, QTimer, QPoint, Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QWidget, QAbstractItemView
import LPGlobalUI
from HOME.LPWaitingSpinner import LPWaitingSpinner
from HOME.Queue.LPQueueListView import LPQueueListModel, LPQueueDelegate
from HOME.Queue.LPQueueOptionMenu import LPQueueOptionMenu
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, Main_Text, Sub_Title
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPQueueManager import LPQueueState
from LPClientFramework.LPShuffleManager import LPShuffleManager
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPCustomMenu import LPMenuItem

class LPPlayViewQueueSectionController(QWidget):
    updateUISignal = pyqtSignal()
    updateLoopModeSignal = pyqtSignal()
    updateShuffleButtonSignal = pyqtSignal(bool)
    updateDeviceInfoSignal = pyqtSignal()
    checkQueueNameSignal = pyqtSignal(object, object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.loadingSpinner = None
        self.updateUISignal.connect(self._updateUI)
        self.updateLoopModeSignal.connect(self._updateLoopMode)
        self.updateShuffleButtonSignal.connect(self._updateShuffleButton)
        self.updateDeviceInfoSignal.connect(self._updateDeviceInfo)
        self.checkQueueNameSignal.connect(self.checkQueueNameChanged)
        self.currentQueueName = None
        self.queueLocked = False
        self.delayTimer = QTimer(self)
        self.delayTimer.setInterval(5000)
        self.delayTimer.timeout.connect(self.onLockTimeout)
        self.firstTimeEnterQueue = True
        self.model = None

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.queueListView.setupUi()
        self.delegate = LPQueueDelegate(self.queueListView)
        self.queueListView.setItemDelegate(self.delegate)
        self.queueListView.queueLockSignal.connect(self.queueLockSlot)
        self.delegate.optClicked.connect(self.onOptClicked)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/shuffle.png'), LPGlobalUI.THEME_LIGHT_COLOR)
        LPButtonEventFilter(self.shuffleButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath('miniBar/shuffle.png')), QIcon(tintImage), 'image')
        self.shuffleButton.clicked.connect(self.onShuffleButtonPressed)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/repeat.png'), LPGlobalUI.THEME_LIGHT_COLOR)
        LPButtonEventFilter(self.loopButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath('miniBar/repeat.png')), QIcon(tintImage), 'image')
        self.loopButton.clicked.connect(self.onLoopButtonPressed)
        stylesheetTemplate = Template('\n                QListView#queueListView {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                    background-color: transparent;\n                }\n                QLabel{\n                    color: rgba(255, 255, 255, 192);\n                }\n                QLabel#queueTitleLabel{\n                    color: rgba(255, 255, 255, 192);\n                    font-size: ${queueTitleLabelFontSize}pt;\n                }\n                QLabel#noteLabel{\n                    color: rgba(255, 255, 255, 192);\n                    font-size: ${noteLabelFontSize}pt;\n                }\n                QPushButton#loopButton, #shuffleButton{\n                    background-color: rgba(255, 255, 255, 27);\n                    border-radius: 8px;                        \n                }\n\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', f'''{Sub_Title}''', f'''{Main_Text}''', **('stackWidgetTiteFontSize', 'queueTitleLabelFontSize', 'noteLabelFontSize')))

    
    def _updateLoopMode(self):
        status = LPGlobalUI.currentDevice.queueManager.status
        if status.value > 0:
            self.loopButton.hide()
            self.shuffleButton.hide()
        else:
            self.loopButton.show()
            self.shuffleButton.show()
            LPShuffleManager.updateLoopShuffleButton(LPGlobalUI.currentDevice, self.loopButton, self.shuffleButton)

    
    def _updateTracksNum(self):
        '''队列曲目数变更时，更新共享基线的队列标题。'''
        logger.debug('queue removed, update tracks num')
        rowCount = self.model.rowCount()
        logger.debug(f'''[update_tracks_num_label] row_count={rowCount}''')
        self._setQueueTitle(rowCount)

    
    def _setQueueTitle(self, rowCount):
        '''
        使用单个富文本标签显示共享基线的队列标题和曲目数。

        :param rowCount: 当前队列曲目数量；传入 None 时清空标题。
        :return: 无。
        '''
        if rowCount is None:
            self.queueTitleLabel.clear()
            return None
        title = None(QCoreApplication.translate('Queue', 'Queue'))
        trackCount = escape(QCoreApplication.translate('Queue', ' (%n tracks)', '', rowCount))
        self.queueTitleLabel.setText(f'''<span style="font-size: {Sub_Title}pt;">{title}</span><span style="font-size: {Main_Text}pt;">{trackCount}</span>''')

    
    def queueLockSlot(self):
        self.queueLocked = True
        self.resetTimer()

    queueLockSlot = pyqtSlot()(queueLockSlot)
    
    def resetTimer(self):
        logger.debug('start timing for 5 seconds')
        self.delayTimer.start()

    
    def onLockTimeout(self):
        self.delayTimer.stop()
        self.queueLocked = False
        logger.debug('timing for 5 seconds have stopped!')
        if LPGlobalUI.currentDevice:
            LPGlobalUI.currentDevice.queueManager.requestQueue()

    onLockTimeout = pyqtSlot()(onLockTimeout)
    
    def onEnter(self):
        logger.debug('[playview queue] onEnter')
        self.firstTimeEnterQueue = True
        LPUtility.registerDeviceInfoChanged(self)
        LPUtility.addNotificationObserver('DeviceChanged', self.onDeviceChanged)
        self.updateUI(LPGlobalUI.currentDevice)

    
    def onLeave(self):
        logger.debug('[playview queue] onLeave')
        LPUtility.deRegisterDeviceInfoChanged(self)
        LPUtility.removeNotificationObserver('DeviceChanged', self.onDeviceChanged)

    
    def onDeviceChanged(self, params):
        logger.debug('[play view queue section]  onDeviceChanged')
        self._setQueueTitle(None)
        self.showLoading()

    
    def updateUI(self, device):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            LPGlobalUI.currentDevice.queueManager.requestQueue()
            self.updateUISignal.emit()

    
    def _updateDeviceInfo(self):
        playList = LPGlobalUI.currentDevice.queueManager.playList
        if playList and playList.list:
            self.model = LPQueueListModel(playList, self.queueListView)
            self.queueListView.setModel(self.model)

    
    def _updateUI(self):
        status = LPGlobalUI.currentDevice.queueManager.status
        if status == LPQueueState.queueEmpty:
            self._setQueueTitle(None)
            self.loadingButton.hide()
            self.noteLabel.setText(QCoreApplication.translate('Queue', 'Nothing here yet'))
            self.stackedWidget.setCurrentIndex(1)
        elif status == LPQueueState.queueNotReady:
            self._setQueueTitle(None)
            self.showLoading()
        elif status == LPQueueState.sourceNotSupportQueue:
            self._setQueueTitle(None)
            self.loadingButton.hide()
            self.noteLabel.setText(QCoreApplication.translate('Queue', "Current music doesn't support queue"))
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stopLoading()
            self.showContent()
        self.updateLoopModeSignal.emit()

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if not LPGlobalUI.mainWindow.isPlayViewShow:
            return None
        if None.currentDevice or device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if not None:
            pass
        detail = { }
        if infoType == 'queue':
            self.updateUISignal.emit()
        if infoType == 'media':
            if 'mediaType' in detail or 'trackSource' in detail:
                if getattr(device.queueManager, 'needsQueueRefresh', False):
                    self._setQueueTitle(None)
                    self.showLoading()
                    device.queueManager.requestQueue()
                else:
                    self.updateUISignal.emit()
        if detail.get('trackId', None) is not None:
            self.updateDeviceInfoSignal.emit()
        if detail.get('queueName', None) is not None:
            newQueueName = detail.get('queueName')
            self.checkQueueNameSignal.emit(device, newQueueName)
        if detail.get('playState', None) is not None:
            self.queueListView.update()

    
    def checkQueueNameChanged(self, device, newQueueName):
        logger.debug('[play view queue section] checkQueueNameChanged')
        oldQueueName = self.currentQueueName
        self.currentQueueName = newQueueName
        if oldQueueName and oldQueueName != newQueueName:
            device.queueManager.playList = None
            self._setQueueTitle(None)
            self.showLoading()
        LPGlobalUI.currentDevice.queueManager.requestQueue()

    
    def _updateShuffleButton(self, enabled):
        self.shuffleButton.canClick = enabled
        if enabled:
            self.shuffleButton.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.shuffleButton.setCursor(Qt.CursorShape.ForbiddenCursor)

    
    def showWithDelay(self, delay_ms = (500,)):
        '''延迟显示 Loading，避免闪烁'''
        self.showLoadingTimer = QTimer(self)
        self.showLoadingTimer.setSingleShot(True)
        self.showLoadingTimer.timeout.connect(self.showLoading)
        self.showLoadingTimer.start(delay_ms)

    
    def stopLoading(self):
        '''请求结束时调用'''
        if hasattr(self, 'showLoadingTimer'):
            self.showLoadingTimer.stop()

    
    def showLoading(self):
        self.noteLabel.setText(QCoreApplication.translate('Queue', 'Loading'))
        self.stackedWidget.setCurrentIndex(1)
        self.loadingButton.show()
        if self.loadingSpinner is None:
            self.loadingSpinner = LPWaitingSpinner(self.loadingButton, 30, 40, 6, 50, 3, 1, 1.5, QColor(255, 255, 255), **('roundness', 'fade', 'radius', 'lines', 'line_length', 'line_width', 'speed', 'color'))
        if not self.loadingSpinner.is_spinning:
            self.loadingSpinner.show()
            self.loadingSpinner.start()

    
    def showContent(self):
        if self.loadingSpinner and self.loadingSpinner.is_spinning:
            self.loadingSpinner.stop()
        playList = LPGlobalUI.currentDevice.queueManager.playList
        if playList and playList.list:
            self.updateShuffleButtonSignal.emit(True)
            self.model = LPQueueListModel(playList, self.queueListView)
            self.queueListView.setModel(self.model)
            self.model.rowsInserted.connect(self._updateTracksNum)
            self.model.rowsRemoved.connect(self._updateTracksNum)
            self._setQueueTitle(self.model.rowCount())
            logger.debug(f'''[_updateUI] row_count={self.model.rowCount()}''')
            if self.firstTimeEnterQueue:
                index = self.model.index(playList.index, 0)
                self.queueListView.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)
                self.firstTimeEnterQueue = False
            else:
                self._setQueueTitle(None)
                self.model = None
                self.queueListView.setModel(self.model)
        self.stackedWidget.setCurrentIndex(0)

    
    def onLoopButtonPressed(self):
        nextMode = LPShuffleManager.nextLoopMode()
        LPGlobalUI.currentDevice.updateMediaInfo({
            'loopMode': int(nextMode) })
        self.updateLoopModeSignal.emit()
        LPGlobalUI.currentDevice.asyncUpnpPost('SetQueueLoopMode', {
            'LoopMode': int(nextMode) })

    
    def onShuffleButtonPressed(self):
        if not self.shuffleButton.canClick:
            return None
        None.showWithDelay()
        nextMode = LPShuffleManager.nextShuffleMode()
        LPGlobalUI.currentDevice.updateMediaInfo({
            'loopMode': int(nextMode) })
        self.updateLoopModeSignal.emit()
        self.updateShuffleButtonSignal.emit(False)
        LPGlobalUI.currentDevice.asyncUpnpPost('SetQueueLoopMode', {
            'LoopMode': int(nextMode) })

    
    def onOptClicked(self, index, globalPos):
        print('hahahha')
        itemList = []
        if self.queueListView.canItemDelete(index):
            deleteMenuItem = LPMenuItem(QCoreApplication.translate('queue menu', 'Delete'), LPGlobalUI.imagePath('delete.png'))
            None((lambda : self.onQueueItemDelete(index)))
            itemList.append(deleteMenuItem)
        if itemList:
            menu = LPQueueOptionMenu(itemList, self)
            menu_x = globalPos.x() - menu.sizeHint().width()
            menu_y = globalPos.y() + 5
            self.queueListView.showMoreMenu(index, menu, QPoint(menu_x, menu_y))

    
    def onQueueItemDelete(self, index):
        if not index.isValid():
            return None
        None.queueListView.deleteItem(index)

    __classcell__ = None

