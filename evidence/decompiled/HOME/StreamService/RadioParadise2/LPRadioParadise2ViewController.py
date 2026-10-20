# Source Generated with Decompyle++
# File: LPRadioParadise2ViewController.pyc (Python 3.9)

'''
@Time ： 2025/01/05 13:33
@Auth ： Chris
@File ：LPRadioParadise2ViewController.py
@Desc:
'''
import json
import queue
import threading
import time
from string import Template
from threading import Thread
import requests_cache
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QRect, QRectF, QTimer, pyqtSlot, QCoreApplication, QPoint, QAbstractListModel
from PyQt6.QtGui import QIcon, QPixmap, QBitmap, QPainter, QCursor, QImage, QColor, QBrush, QPainterPath, QFontMetrics, QFont, QMouseEvent, QMovie
from PyQt6.QtWidgets import QWidget, QToolTip, QStyledItemDelegate, QStyle
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPConfig.LPFontConfig import StackWidget_Title, ItemCard_Title
from LPClientFramework.LPConfig.LPUIPath import LoginDialogUI
from LPClientFramework.LPDataModel.NetWorkDataModel.LPRadioParadise2NetworkDataModel import LPRadioParadise2NetworkDataModel
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPPlayList.LPRadioParadise2PlayList import LPRadioParadise2PlayList, LPRadioParadise2PlayHeader, LPRadioParadise2Account, LPRadioParadise2PlayItem
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPUtility import logger
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource, LPHeaderType
from LPCommonWidgets.dialog.LPLoginDialog import LPLoginDialog
from LPCommonWidgets.dialog.LPLoginDialog_ui import Ui_LoginDialog
from LPCommonWidgets.menu.LPLogoutMenu import LogoutMenu
from LPCommonWidgets.skeleton.LPListViewSkeleton import LPListViewSkeletonListModel, LPListViewSkeletonDelegate
from LPGlobalUI import uiConfig

class LPRadioParadise2ListModel(QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        super().__init__(parent)
        self._data = data
        self.channelImageQueue = queue.Queue()
        self.fetchImageThread = None

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            imageUrl = self._data[row]['image']
            if imageUrl and len(imageUrl) > 0:
                pixmap = LPUtility.getCachedPixmapWithUrl(imageUrl, 155)
                if pixmap is None:
                    
                    def _fetchImageMethod():
                        if self.channelImageQueue.empty():
                            time.sleep(1)
                            continue
                        dataDict = self.channelImageQueue.get()
                        url = dataDict.get('value', None)
                        indexObj = dataDict.get('index', None)
                        respDict = LPUtility.fetchUrlQPixmap(url, False, 155)
                        pixmap = respDict.get('image', None)
                        if pixmap:
                            self.dataChanged.emit(indexObj, indexObj)
                        self.channelImageQueue.task_done()
                        continue

                    self.channelImageQueue.put({
                        'value': imageUrl,
                        'index': index })
                    if self.fetchImageThread is None:
                        self.fetchImageThread = threading.Thread(_fetchImageMethod, True, **('target', 'daemon'))
                        self.fetchImageThread.start()
            chanDict = self._data[row]
            isCurrentPlay = LPGlobalUI.currentDevice.deviceStreamServiceManager.isCurrentPlayChannel(LPPlayListSource.RadioParadise2.value, LPGlobalUI.currentDevice, chanDict)
            return (chanDict, isCurrentPlay)

    __classcell__ = None


class LPRadioParadise2Delegate(QStyledItemDelegate):
    
    def __init__(self = None, list_view = None):
        super().__init__(list_view)
        self.config = uiConfig.stackedWidget.radioParadise2
        self.list_view = list_view
        self.play_movie = QMovie(LPGlobalUI.imagePath('dark_playing.gif'))
        self.play_movie.start()
        self.play_movie.frameChanged.connect(self.update_view)

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QSize(190, 265)
        return result

    
    def paint(self, painter, option, index):
        data = index.data()
        if data is None:
            return None
        cellRect = None.rect
        superListView = option.styleObject
        itemData = data[0]
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        if option.state & QStyle.StateFlag.State_Selected:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        else:
            brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QPainterPath()
        path.addRoundedRect(QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        coverRect = QRect(cellRect.x() + 17, cellRect.y() + 22, 155, 155)
        icon = QIcon()
        if len(itemData['image']) > 0:
            pixmap = LPUtility.getCachedPixmapWithUrl(itemData['image'], 155)
            if pixmap:
                pass
            else:
                pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        else:
            pixmap = QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
        playIconRect = QRect(cellRect.x() + 115, cellRect.y() + 120, 50, 50)
        if option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(QColor(0, 0, 0, 20))
            path = QPainterPath()
            path.addRect(coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
            painter.fillPath(path, brush)
            icon = QIcon(LPGlobalUI.imagePath('WiiMRadio/play.svg'))
            if superListView.lastCursorPos and playIconRect.contains(superListView.lastCursorPos):
                icon.paint(painter, playIconRect.x() - 1, playIconRect.y() - 1, playIconRect.width() + 2, playIconRect.height() + 2)
            else:
                icon.paint(painter, playIconRect.x(), playIconRect.y(), playIconRect.width(), playIconRect.height())
        title = itemData['title']
        rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, 155, 25)
        font = QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        play_state = LPGlobalUI.currentDevice.mediaInfo.playState
        isPlayingItem = data[1]
        play_ani_size = 13
        if isPlayingItem:
            ani_rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25 + 4, play_ani_size, play_ani_size)
            if play_state == 'PLAYING':
                current_frame = self.play_movie.currentPixmap()
                painter.drawPixmap(ani_rect, current_frame)
            else:
                play_icon = QIcon()
                pixmap = QPixmap(LPGlobalUI.imagePath('dark_pause.png'))
                play_icon.addPixmap(pixmap)
                play_icon.paint(painter, ani_rect.x(), ani_rect.y(), play_ani_size, play_ani_size)
            title_rect = QRect(cellRect.x() + 17 + play_ani_size + 6, cellRect.y() + 22 + 155 + 25, cellRect.width() - 17 - play_ani_size - 4, 25)
            painter.setPen(LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        else:
            title_rect = QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 25, cellRect.width(), 25)
            painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        metrics = QFontMetrics(font)
        title = QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        if superListView.lastCursorPos:
            if cellRect.contains(superListView.lastCursorPos) or superListView.cursor() != Qt.CursorShape.PointingHandCursor:
                superListView.lastCursorActionIndex = index
                superListView.setCursor(Qt.CursorShape.PointingHandCursor)
            elif superListView.cursor() != Qt.CursorShape.ArrowCursor and superListView.lastCursorActionIndex == index:
                superListView.lastCursorActionIndex = None
                superListView.setCursor(Qt.CursorShape.ArrowCursor)

    
    def update_view(self):
        if self.list_view:
            self.list_view.viewport().update()

    
    def cleanup_list_view(self):
        if self.play_movie:
            self.play_movie.stop()

    __classcell__ = None


class LPRadioParadise2ViewController(QWidget):
    stream_url_formatter = 'https://api.radioparadise.com/api/gapless?C_user_id={}&player_id={}&chan={}&bitrate=4'
    updateUISignal = pyqtSignal()
    updateAccountSignal = pyqtSignal()
    updateLoginButtonSignal = pyqtSignal()
    updateListChanSignal = pyqtSignal()
    loadSkeletonSignal = pyqtSignal()
    unsupportedSignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        self.channelList = None
        self.updateUISignal.connect(self._updateUI)
        self.account = None
        self.source = LPPlayListSource.RadioParadise2.value
        self.updateAccountSignal.connect(self.updateAccount)
        self.updateLoginButtonSignal.connect(self.updateLoginButtonUI)
        self.updateListChanSignal.connect(self._fetchChannelList)
        self.unsupportedSignal.connect(self._unsupported)
        self.networkModel = LPRadioParadise2NetworkDataModel()
        self.networkModel.timeoutSignal.connect(self.time_out)
        self.networkModel.loadSkeletonSignal.connect(self._loadSkeleton)
        self.upnpModel = LPUpnpAsyncDataModel()

    
    def _loadSkeleton(self):
        self.add_skeleton_items()

    
    def time_out(self):
        self.noteLabel.setText(QCoreApplication.translate('RadioParadise2', 'Unexpected error, please try later!'))
        self.stackedWidget.setCurrentIndex(1)

    time_out = pyqtSlot()(time_out)
    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.listView.doubleClicked.connect(self.itemDoubleClick)
        self.listView.clicked.connect(self.itemClick)
        self.listView.setGridSize(QSize(205, 285))
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.loginButton.installEventFilter(self)
        self.loginButton.setCursor(Qt.CursorShape.PointingHandCursor)
        stylesheetTemplate = Template('\n                QLabel#label {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n                QToolTip {\n                    background-color: #333333;\n                    color: white;\n                    border: none;\n                    border-radius: 5px;\n                    font-weight: bold;\n                    padding: 5px;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))
        self.loginButton.setVisible(False)

    
    def add_skeleton_items(self):
        '''
        添加骨架屏占位符 固定为 8个
        '''
        logger.debug('radio paradise2 add_skeleton_items')
        skeletonConfig = uiConfig.stackedWidget.radioParadise2.skeleton
        model = LPListViewSkeletonListModel(skeletonConfig.number)
        delegate = LPListViewSkeletonDelegate(self, skeletonConfig)
        self.listView.setModel(model)
        self.listView.setItemDelegate(delegate)

    
    def viewWillAppear(self):
        logger.debug('radio paradise2 viewWillAppear')
        LPUtility.registerDeviceInfoChanged(self)
        LPUtility.addNotificationObserver('accountChangedForSource', self.accountChanged)
        self.updateUI(LPGlobalUI.currentDevice)

    
    def viewWillDisappear(self):
        LPUtility.deRegisterDeviceInfoChanged(self)
        LPUtility.removeNotificationObserver('accountChangedForSource', self.accountChanged)

    
    def updateUI(self, device):
        if LPGlobalUI.currentDevice and device.uuid == LPGlobalUI.currentDevice.uuid:
            if self.source not in LPGlobalUI.currentDevice.deviceStreamServiceManager.streamServiceCapability.keys():
                self.unsupportedSignal.emit()
                return None
            None.updateAccountSignal.emit()

    
    def _fetchChannelList(self):
        '''load data'''
        
        def finishedMethod(response = None, *args):
            pass
        # WARNING: Decompyle incomplete

        if isinstance(self.account, LPRadioParadise2Account):
            self.networkModel.fetchChannelData(self.account.cUserId, finishedMethod)

    _fetchChannelList = pyqtSlot()(_fetchChannelList)
    
    def _updateUI(self):
        logger.debug('chris _updateUI')
        self.stackedWidget.setCurrentIndex(0)
        delegate = LPRadioParadise2Delegate(self.listView)
        self.listView.setItemDelegate(delegate)
        model = LPRadioParadise2ListModel(self.channelList)
        self.listView.setModel(model)
        self.listView.setCursor(Qt.CursorShape.ArrowCursor)

    
    def getPlayList(self, item):
        playList = LPRadioParadise2PlayList()
        header = LPRadioParadise2PlayHeader()
        header.headTitle = item['title']
        header.searchUrl = self.stream_url_formatter.format(self.account.cUserId, LPGlobalUI.currentDevice.uuid, item['chan'])
        header.headType = LPHeaderType.LP_HEADER_TYPE_STATION
        header.imageUrl = item['image']
        playList.header = header
        playList.account = self.account
        playItem = LPRadioParadise2PlayItem()
        playItem.trackId = str(item.get('chan', ''))
        if not item.get('title', ''):
            pass
        playItem.trackName = item.get('stream_name', '')
        playItem.trackImage = item.get('image', '')
        playItem.trackArtist = ''
        playList.list = [
            playItem]
        playList.index = 0
        return playList

    
    def loginButtonClicked(self):
        if self.account and self.account.userId:
            logoutMenu = LogoutMenu(self.loginButton, self)
            logoutMenu.showMenu()
        else:
            picUrl = LPGlobalUI.imagePath('streamservice/radioparadise_flat.png')
            loginDialog = LPGlobalUI.loadUI(LoginDialogUI, Ui_LoginDialog, LPLoginDialog, self.source, picUrl, self)
            loginDialog.exec()

    loginButtonClicked = pyqtSlot()(loginButtonClicked)
    
    def updateAccount(self):
        self.account = LPGlobalUI.currentDevice.deviceStreamServiceManager.accountForSource(self.source)
        if self.account:
            logger.debug('radio paradise2 updateAccount ==== account')
            self.updateListChanSignal.emit()
            self.updateLoginButtonSignal.emit()
        else:
            logger.debug('radio paradise2 updateAccount ==== anonUserId')
            self.getUserInfo()

    updateAccount = pyqtSlot()(updateAccount)
    
    def getUserInfo(self):
        
        def finishedMethod(response = None, *args):
            pass
        # WARNING: Decompyle incomplete

        self.upnpModel.getUserInfo(LPGlobalUI.currentDevice, self.source, finishedMethod)

    
    def updateLoginButtonUI(self):
        self.loginButton.setVisible(True)
        if self.account and self.account.userId:
            logger.debug('radio paradise2 updateLoginButtonUI ==== self.account')
            firstLetter = self.account.showName[:1].upper()
            avatarPixmap = LPUtility.generate_avatar(firstLetter)
            self.loginButton.setIcon(QIcon(avatarPixmap))
            self.loginButton.setFixedSize(40, 40)
            self.loginButton.setIconSize(QSize(40, 40))
        else:
            logger.debug('radio paradise2 updateLoginButtonUI ==== anonUserId')
            tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('login.png'), LPGlobalUI.THEME_LIGHT_COLOR)
            self.loginButton.setIcon(QIcon(tintImage))
            self.loginButton.setFixedSize(40, 40)
            self.loginButton.setIconSize(QSize(40, 40))

    updateLoginButtonUI = pyqtSlot()(updateLoginButtonUI)
    
    def eventFilter(self = None, source = None, event = None):
        if source == self.loginButton:
            if event.type().name == 'Enter':
                if self.account and self.account.userId:
                    self.showAccountTooltip()
                self.loginButton.setIconSize(QSize(self.loginButton.iconSize().width() + 2, self.loginButton.iconSize().height() + 2))
            elif event.type().name == 'Leave':
                QToolTip.hideText()
                self.loginButton.setIconSize(QSize(self.loginButton.iconSize().width() - 2, self.loginButton.iconSize().height() - 2))
        return super().eventFilter(source, event)

    
    def showAccountTooltip(self):
        button_rect = self.loginButton.rect()
        global_pos = self.loginButton.mapToGlobal(button_rect.bottomLeft())
        font_metrics = QFontMetrics(QToolTip.font())
        tooltip_width = font_metrics.horizontalAdvance(self.account.showName) + 10
        button_width = self.loginButton.width()
        x_offset = (button_width - tooltip_width) // 2 - 8
        y_offset = -5
        tooltip_pos = global_pos + QPoint(x_offset, y_offset)
        QToolTip.showText(tooltip_pos, self.account.showName, self.loginButton)

    
    def deviceInfoUpdate(self, device, infoType, detail):
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None == 'accountRegister' and self.source == detail.get('source', None):
            self.updateUI(device)
        if infoType == 'media' and detail.get('queueName', None) is not None:
            self.listView.update()
        if detail.get('playState', None) is not None:
            self.listView.update()

    
    def accountChanged(self, params):
        device = params.get('device', None)
        notify = params.get('notify', None)
        if device.uuid != LPGlobalUI.currentDevice.uuid:
            return None
        if None.get('source', None) != self.source:
            return None
        None.updateAccountSignal.emit()
        self.updateLoginButtonSignal.emit()

    
    def itemDoubleClick(self, index):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        data = None.data()
        if not data or data[0]:
            return None
        item = None[0]
        playList = self.getPlayList(item)
        xml = playList.generateXML()
        
        def finishedMethod(response = None, *args):
            if response:
                logger.debug('[radio paradise2] %s play result: success' % item.get('stream_name', item.get('title', '')))
                LPRecentlyManager.instance().addRecentlyPlayedWithMusicList(playList, {
                    'openMore': True,
                    'canNavigate': False })
            else:
                logger.debug('[radio paradise2] %s play result: failed' % item.get('stream_name', item.get('title', '')))

        device.deviceStreamServiceManager.updateMediaInfoForSource(device, self.source, item)
        device.guardMediaInfoRollback()
        self.upnpModel.palyWithSearchUrl(device, xml, finishedMethod)

    
    def itemClick(self, index):
        device = LPGlobalUI.currentDevice
        if not device:
            logger.error('error, no device found')
            return None
        data = None.data()
        if not data or data[0]:
            return None
        item = None[0]
        playList = self.getPlayList(item)
        xml = playList.generateXML()
        
        def finishedMethod(response = None, *args):
            if response:
                logger.debug('[radio paradise2] %s play result: success' % item.get('stream_name', item.get('title', '')))
                LPRecentlyManager.instance().addRecentlyPlayedWithMusicList(playList, {
                    'openMore': True,
                    'canNavigate': False })
            else:
                logger.debug('[radio paradise2] %s play result: failed' % item.get('stream_name', item.get('title', '')))

        device.deviceStreamServiceManager.updateMediaInfoForSource(device, self.source, item)
        device.guardMediaInfoRollback()
        self.upnpModel.palyWithSearchUrl(device, xml, finishedMethod)

    
    def _unsupported(self):
        logger.debug("Current device doesn't support Radio Paradise2")
        self.loginButton.hide()
        self.noteLabel.setText(QCoreApplication.translate('RadioParadise2', "Current device doesn't support Radio Paradise"))
        self.stackedWidget.setCurrentIndex(1)

    _unsupported = pyqtSlot()(_unsupported)
    __classcell__ = None

