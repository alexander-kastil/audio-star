# Source Generated with Decompyle++
# File: LPQueueDialog.pyc (Python 3.9)

'''
@Time ： 2025/9/29 13:38
@Auth ： Chris
@File ：LPQueueDialog.py
@Desc:
'''
import threading
from string import Template
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QPoint, QEvent, QTimer
from PyQt6.QtGui import QIcon, QCursor, QColor
from PyQt6.QtWidgets import QDialog, QAbstractItemView, QApplication
import LPGlobalUI
from HOME.LPWaitingSpinner import LPWaitingSpinner
from HOME.Queue.LPQueueListView import LPQueueListModel, LPQueueDelegate
from HOME.Queue.LPQueueOptionMenu import LPQueueOptionMenu
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import Sub_Title, Sub_Text, Main_Text
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPQueueManager import LPQueueState
from LPClientFramework.LPShuffleManager import LPShuffleManager
from LPClientFramework.LPUtility import logger
from LPCommonWidgets.menu.LPCustomMenu import LPMenuItem

class LPQueueDialog(QDialog):
    updateUISignal = pyqtSignal()
    updateDeviceInfoSignal = pyqtSignal()
    updateShuffleButtonSignal = pyqtSignal(bool)
    updateLoopModeSignal = pyqtSignal()
    checkQueueNameSignal = pyqtSignal(object, object)
    closedSignal = pyqtSignal()
    
    def __init__(self = None, parent = None):
        '''
        初始化队列弹窗控制器。

        参数:
            parent: 弹窗所属的 minibar 控制器宿主。
        返回值:
            None。
        '''
        super().__init__(parent)
        self.parent = parent
        self.updateUISignal.connect(self._updateUI)
        self.updateDeviceInfoSignal.connect(self._updateDeviceInfo)
        self.updateShuffleButtonSignal.connect(self._updateShuffleButton)
        self.updateLoopModeSignal.connect(self._updateLoopMode)
        self.checkQueueNameSignal.connect(self.checkQueueNameChanged)
        self.currentQueueName = None
        self.firstTimeEnterQueue = True
        QApplication.instance().installEventFilter(self)
        self.loadingSpinner = None
        self.model = None

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleLabel.setText(QCoreApplication.translate('queue dialog', 'Queue'))
        self.queueListView.setupUi()
        self.delegate = LPQueueDelegate(self.queueListView)
        self.queueListView.setItemDelegate(self.delegate)
        self.delegate.optClicked.connect(self.onOptClicked)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/shuffle.png'), LPGlobalUI.THEME_LIGHT_COLOR)
        LPButtonEventFilter(self.shuffleButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath('miniBar/shuffle.png')), QIcon(tintImage), 'image')
        self.shuffleButton.clicked.connect(self.onShuffleButtonPressed)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('miniBar/repeat.png'), LPGlobalUI.THEME_LIGHT_COLOR)
        LPButtonEventFilter(self.loopButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath('miniBar/repeat.png')), QIcon(tintImage), 'image')
        self.loopButton.clicked.connect(self.onLoopButtonPressed)
        LPGlobalUI.currentDevice.queueManager.requestQueue()
        qssTemplate = Template('\n                QFrame{\n                    border:none;\n                    background-color: transparent;\n                }\n                QFrame#mainFrame{\n                    border-radius: 8px;\n                    background-color: rgb(27, 27, 27);\n                }\n                QLabel#noteLabel{\n                    color: rgba(255, 255, 255, 192);\n                    font-size: ${noteLabelFontSize}pt;\n                }\n                QLabel#titleLabel {\n                    color: $fontColor;\n                    background-color: transparent;\n                    font-size: ${titleLabelFontSize}pt;\n                }\n                QLabel#trackNumLabel {\n                    color: $trackNumLabelFontColor;\n                    background-color: transparent;\n                    font-size: ${trackNumLabelFontSize}pt;\n                }\n                \n                QPushButton#shuffleButton, #loopButton {\n                    background-color: transparent;\n                    color: $fontColor;\n                }\n                ')
        self.setStyleSheet(qssTemplate.substitute(LPGlobalUI.THEME_FONT_COLOR_UI.name(), LPGlobalUI.THEME_DISABLE_COLOR.name(), f'''{Sub_Title}''', f'''{Sub_Text}''', f'''{Main_Text}''', **('fontColor', 'trackNumLabelFontColor', 'titleLabelFontSize', 'trackNumLabelFontSize', 'noteLabelFontSize')))

    
    def _updateUI(self):
        status = LPGlobalUI.currentDevice.queueManager.status
        if status == LPQueueState.queueEmpty:
            self.trackNumLabel.setText('')
            self.loadingButton.hide()
            self.noteLabel.setText(QCoreApplication.translate('Queue', 'Nothing here yet'))
            self.stackedWidget.setCurrentIndex(1)
        elif status == LPQueueState.queueNotReady:
            self.trackNumLabel.setText('')
            self.showLoading()
        elif status == LPQueueState.sourceNotSupportQueue:
            self.trackNumLabel.setText('')
            self.loadingButton.hide()
            self.noteLabel.setText(QCoreApplication.translate('Queue', "Current music doesn't support queue"))
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stopLoading()
            self.showContent()
        self.updateLoopModeSignal.emit()

    
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
            self.trackNumLabel.setText(QCoreApplication.translate('Queue', '(%n tracks)', None, self.model.rowCount()))
            logger.debug(f'''[_updateUI] row_count={self.model.rowCount()}''')
            if self.firstTimeEnterQueue:
                index = self.model.index(playList.index, 0)
                self.queueListView.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)
                self.firstTimeEnterQueue = False
            else:
                self.model = None
                self.queueListView.setModel(self.model)
        self.stackedWidget.setCurrentIndex(0)

    
    def _updateDeviceInfo(self):
        playList = LPGlobalUI.currentDevice.queueManager.playList
        if playList and playList.list:
            self.model = LPQueueListModel(playList, self.queueListView)
            self.queueListView.setModel(self.model)
            self.trackNumLabel.setText(QCoreApplication.translate('Queue', '(%n tracks)', None, self.model.rowCount()))

    
    def _updateShuffleButton(self, enabled):
        self.shuffleButton.canClick = enabled
        if enabled:
            self.shuffleButton.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.shuffleButton.setCursor(Qt.CursorShape.ForbiddenCursor)

    
    def focusOutEvent(self = None, event = None):
        new_focus = QApplication.focusWidget()
        if new_focus and self.isAncestorOf(new_focus):
            return None
        mousePos = None.pos()
        if self.parent.queueButton.geometry().contains(self.parent.queueButton.mapFromGlobal(mousePos)) or self.queueListView.jumpButton.geometry().contains(self.queueListView.jumpButton.mapFromGlobal(mousePos)):
            event.ignore()
            return None
        None().focusOutEvent(event)
        self.close()

    
    def eventFilter(self = None, obj = None, event = None):
        if obj == self.parent and event.type() == QEvent.Type.Move:
            self.updatePosition()
        if event.type() == QEvent.Type.MouseButtonPress:
            mouse_pos = QCursor.pos()
            if self.geometry().contains(mouse_pos):
                return False
            pos_global = None.globalPosition().toPoint()
            widget = QApplication.widgetAt(pos_global)
            if widget is self.parent.queueButton:
                return super().eventFilter(obj, event)
            None.close()
        return super().eventFilter(obj, event)

    
    def updatePosition(self):
        if self.parent:
            minibar_geom = self.parent.miniBarFrame.geometry()
            top_left_global = self.parent.mapToGlobal(minibar_geom.topLeft())
            top_margin = 40
            dialog_height = minibar_geom.top() - top_margin
            dialog_width = self.width()
            dialog_x = top_left_global.x() + minibar_geom.width() - dialog_width - 10
            dialog_y = top_margin + top_left_global.y() - minibar_geom.top()
            self.setGeometry(dialog_x, dialog_y, dialog_width, dialog_height)

    
    def showEvent(self = None, event = None):
        super().showEvent(event)
        self.updatePosition()
        self.onDialogShown()

    
    def onDialogShown(self):
        logger.debug('[queue dialog] onDialogShown =====')
        LPUtility.addNotificationObserver('DeviceChanged', self.onDeviceChanged)
        LPUtility.registerDeviceInfoChanged(self)
        self.updateUI(LPGlobalUI.currentDevice)

    
    def onDialogClosed(self):
        logger.debug('[queue dialog] onDialogClosed =====')
        LPUtility.removeNotificationObserver('DeviceChanged', self.onDeviceChanged)
        LPUtility.deRegisterDeviceInfoChanged(self)

    
    def closeEvent(self = None, event = None):
        '''
        处理队列弹窗关闭并通知 minibar 同步按钮状态。

        参数:
            event: Qt 关闭事件。
        返回值:
            None。
        '''
        print('Popup closed')
        mousePos = QCursor.pos()
        super().closeEvent(event)
        self.onDialogClosed()
        self.closedSignal.emit()

    
    def onDeviceChanged(self, params):
        logger.debug('[queue dialog] onDeviceChanged')
        currentDevice = LPGlobalUI.currentDevice
        newDevice = params.get('device', None)
        if currentDevice.uuid != newDevice.uuid:
            return None
        None.updateUI(newDevice)

    
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

    
    def updateUI(self, device):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            LPGlobalUI.currentDevice.queueManager.requestQueue()
            self.updateUISignal.emit()

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if device or device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None == 'queue':
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
            self.trackNumLabel.setText('')
            self.showLoading()
        LPGlobalUI.currentDevice.queueManager.requestQueue()

    
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
        logger.debug('queue removed, update tracks num')
        rowCount = self.model.rowCount()
        logger.debug(f'''[update_tracks_num_label] row_count={rowCount}''')
        self.trackNumLabel.setText(QCoreApplication.translate('Queue', '(%n tracks)', '', rowCount))

    
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

    __classcell__ = None

