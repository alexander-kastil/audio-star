# Source Generated with Decompyle++
# File: LPMyMusicGenresViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
import LPGlobalUI
from HOME.LPMyMusicViewController import LPMyMusicViewController
from HOME.LPMyMusicViewController_ui import Ui_mymusicViewWidget
from HOME.MyMusic.LPMyMusicGenreDetailViewController import LPMyMusicGenreDetailViewController
from HOME.MyMusic.LPMyMusicGenreDetailViewController_ui import Ui_mymusicGenreDetailViewWidget
from LPClientFramework import LPBeetsWrapper, LPUtility
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle, StackWidget_Title
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
GENRE_CARD_COVER_SIZE = 155
GENRE_CARD_COMPOSITE_COUNT = 4
GENRE_CARD_COMPOSITE_IMAGE_SIZE = 80

class LPMyMusicGenresListModel(QtCore.QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        super(LPMyMusicGenresListModel, self).__init__(parent)
        self._data = data

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            itemDict = self._data[row]
            return itemDict

    __classcell__ = None


class LPMyMusicGenreDelegate(QStyledItemDelegate):
    mouseClicked = QtCore.pyqtSignal(object, object)
    
    def __init__(self = None, parent = None):
        super().__init__(parent)

    
    def sizeHint(self = None, option = None, index = None):
        result = super().sizeHint(option, index)
        result = QtCore.QSize(190, 265)
        return result

    
    def editorEvent(self = None, event = None, model = None, option = None, index = None):
        cellRect = option.rect
        playIconRect = QtCore.QRect(cellRect.x() + 115, cellRect.y() + 120, 50, 50)
        if event.type() == QEvent.Type.MouseButtonPress:
            if playIconRect.contains(event.pos()):
                self.mouseClicked.emit(index, 'play')
            else:
                self.mouseClicked.emit(index, 'enter')
        return super().editorEvent(event, model, option, index)

    
    def paint(self, painter, option, index):
        data = index.data()
        if data is None:
            return None
        cellRect = None.rect
        superListView = option.styleObject
        brush = QtGui.QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        if option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR)
        else:
            brush.setColor(LPGlobalUI.THEME_ITEM_BACK_COLOR)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(cellRect), 5, 5)
        painter.fillPath(path, brush)
        coverRect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22, 155, 155)
        coverPixmapArray = []
        coverPathArray = []
        for path in data['path']:
            if len(coverPixmapArray) >= GENRE_CARD_COMPOSITE_COUNT:
                pass
            else:
                pixmap = LPUtility.coverImageForLocalPath(path, GENRE_CARD_COMPOSITE_IMAGE_SIZE)
                if pixmap is not None:
                    coverPixmapArray.append(pixmap)
                    coverPathArray.append(path)
                    continue
                    if len(coverPixmapArray) >= GENRE_CARD_COMPOSITE_COUNT:
                        icon = QtGui.QIcon()
                        icon.addPixmap(coverPixmapArray[0])
                        icon.paint(painter, coverRect.x(), coverRect.y(), int(coverRect.width() / 2), int(coverRect.height() / 2))
                        icon.addPixmap(coverPixmapArray[1])
                        icon.paint(painter, coverRect.x() + int(coverRect.width() / 2), coverRect.y(), int(coverRect.width() / 2), int(coverRect.height() / 2))
                        icon.addPixmap(coverPixmapArray[2])
                        icon.paint(painter, coverRect.x(), coverRect.y() + int(coverRect.height() / 2), int(coverRect.width() / 2), int(coverRect.height() / 2))
                        icon.addPixmap(coverPixmapArray[3])
                        icon.paint(painter, coverRect.x() + int(coverRect.width() / 2), coverRect.y() + int(coverRect.height() / 2), int(coverRect.width() / 2), int(coverRect.height() / 2))
                    elif len(coverPathArray) == 0:
                        pixmap = QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
                    else:
                        pixmap = LPUtility.coverImageForLocalPath(coverPathArray[0], GENRE_CARD_COVER_SIZE)
                        if pixmap is None:
                            pixmap = coverPixmapArray[0]
        icon = QtGui.QIcon()
        icon.addPixmap(pixmap)
        icon.paint(painter, cellRect.x() + 17, cellRect.y() + 22, 155, 155)
        playIconRect = QtCore.QRect(cellRect.x() + 115, cellRect.y() + 120, 50, 50)
        if option.state & QStyle.StateFlag.State_MouseOver:
            brush.setColor(QtGui.QColor(0, 0, 0, 20))
            path = QtGui.QPainterPath()
            path.addRect(coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
            painter.fillPath(path, brush)
            pixmap = QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/play.png'))
            icon = QtGui.QIcon()
            icon.addPixmap(pixmap)
            if superListView.lastCursorPos and playIconRect.contains(superListView.lastCursorPos):
                icon.paint(painter, playIconRect.x() - 1, playIconRect.y() - 1, playIconRect.width() + 2, playIconRect.height() + 2)
            else:
                icon.paint(painter, playIconRect.x(), playIconRect.y(), playIconRect.width(), playIconRect.height())
        title = data['genre']
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10, 155, 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        metrics = QtGui.QFontMetrics(font)
        title = QtGui.QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop, title)
        genre = QCoreApplication.translate('Genre', 'Genre')
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10 + 25, 155, 50)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.TextFlag.TextWordWrap, genre)
        if superListView.lastCursorPos:
            if not cellRect.contains(superListView.lastCursorPos) and playIconRect.contains(superListView.lastCursorPos):
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.ArrowCursor))

    __classcell__ = None


class LPMyMusicGenresViewController(QWidget):
    updateLibSignal = pyqtSignal(object)
    
    def __init__(self = None, showImportWaitingDialogMethod = None, updateImportWaitingDialogMethod = None):
        super(LPMyMusicGenresViewController, self).__init__()
        self.showImportWaitingDialogMethod = showImportWaitingDialogMethod
        self.updateImportWaitingDialogMethod = updateImportWaitingDialogMethod
        
        def _updateLib():
            playList = LPBeetsWrapper.queryGenres()
            model = LPMyMusicGenresListModel(playList)
            self.listView.setModel(model)

        self.updateLibSignal.connect(_updateLib)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.addButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n\nQPushButton:hover {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}        ' % (LPGlobalUI.THEME_BUTTON_BACK_COLOR.name(), LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name()))
        self.addButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        None((lambda : LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.MyMusicViewControllerUI, Ui_mymusicViewWidget, LPMyMusicViewController, self.showImportWaitingDialogMethod, self.updateImportWaitingDialogMethod), 'mymusic')))
        self.listView.verticalScrollBar().setSingleStep(40)
        playList = LPBeetsWrapper.queryGenres()
        model = LPMyMusicGenresListModel(playList)
        self.listView.setModel(model)
        delegate = LPMyMusicGenreDelegate()
        delegate.mouseClicked.connect(self.itemClick)
        self.listView.setItemDelegate(delegate)
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))

    
    def viewWillAppear(self):
        LPUtility.addNotificationObserver('LibUpdateNotify', self._libUpdateMethod)
        self.updateUI(LPGlobalUI.currentDevice)

    
    def viewWillDisappear(self):
        LPUtility.removeNotificationObserver('LibUpdateNotify', self._libUpdateMethod)

    
    def _libUpdateMethod(self, params):
        self.updateLibSignal.emit(params)

    
    def itemClick(self, index, clickType):
        data = index.data()
        genreName = data.get('genre', None)
        if clickType == 'play':
            playList = LPBeetsWrapper.queryTracks(genreName, True, **('genre', 'strict'))
            device = LPGlobalUI.currentDevice
            if not device:
                logger.error('error, no device found')
                return None
            
            def playFinishMethod(result = None):
                logger.debug('Mymusic genre %s play result: %s' % (genreName, result))
                if result:
                    LPRecentlyManager.instance().addRecentlyPlayedWithMusicList(playList, {
                        'openMore': False,
                        'canNavigate': True })

            if genreName:
                headTitle = genreName
            else:
                headTitle = 'MyMusic Genre'
            playList.header.headTitle = headTitle
            playList.header.headType = LPHeaderType.LP_HEADER_TYPE_COLLECTION
            if not genreName:
                pass
            playList.header.headId = ''
            device.fastPlay(playList, playFinishMethod)
        elif clickType == 'enter':
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.MyMusicGenreDetailViewControllerUI, Ui_mymusicGenreDetailViewWidget, LPMyMusicGenreDetailViewController, data), 'genredetail')

    
    def updateUI(self, device):
        data = self.listView.model()._data
        if data is None or len(data) == 0:
            self.noteLabel.setText(QCoreApplication.translate('Genre', 'Add some music to start experiencing WiiM Home!'))
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

    
    def itemDoubleClick(self, index):
        pass

    __classcell__ = None

