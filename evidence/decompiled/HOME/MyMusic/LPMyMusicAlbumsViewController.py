# Source Generated with Decompyle++
# File: LPMyMusicAlbumsViewController.pyc (Python 3.9)

from string import Template
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QCoreApplication
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
import LPGlobalUI
from HOME.LPMyMusicViewController import LPMyMusicViewController
from HOME.LPMyMusicViewController_ui import Ui_mymusicViewWidget
from HOME.MyMusic.LPMyMusicAlbumDetailViewController import LPMyMusicAlbumDetailViewController
from HOME.MyMusic.LPMyMusicAlbumDetailViewController_ui import Ui_mymusicAlbumDetailViewWidget
from HOME.MyMusic.LPMyMusicArtistDetailViewController import LPMyMusicArtistDetailViewController
from HOME.MyMusic.LPMyMusicArtistDetailViewController_ui import Ui_mymusicArtistDetailViewWidget
from LPClientFramework import LPUtility, LPBeetsWrapper
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Title, ItemCard_Subtitle, StackWidget_Title
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import logger
ALBUM_CARD_COVER_SIZE = 155

class LPMyMusicAlbumsListModel(QtCore.QAbstractListModel):
    
    def __init__(self = None, data = None, parent = None):
        super(LPMyMusicAlbumsListModel, self).__init__(parent)
        self._data = data

    
    def rowCount(self, parent = (None,)):
        return len(self._data)

    
    def data(self, index, role = (Qt.ItemDataRole.DisplayRole,)):
        row = index.row()
        if row >= self.rowCount() or row < 0:
            return None
        if None == Qt.ItemDataRole.DisplayRole:
            albumDict = self._data[row]
            return albumDict

    __classcell__ = None


class LPMyMusicAlbumDelegate(QStyledItemDelegate):
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
            superListView = option.widget
            if superListView.lastCursorActionIndex is not None:
                self.mouseClicked.emit(index, 'artist')
            elif playIconRect.contains(event.pos()):
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
        pixmap = LPUtility.coverImageForLocalPath(data['path'], ALBUM_CARD_COVER_SIZE)
        if pixmap is None:
            pixmap = QtGui.QPixmap(LPGlobalUI.imagePath('miniBar/trackDefault.png'))
        icon = QtGui.QIcon()
        icon.addPixmap(pixmap)
        icon.paint(painter, coverRect.x(), coverRect.y(), coverRect.width(), coverRect.height())
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
        title = data['album']
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10, 155, 25)
        painter.setPen(LPGlobalUI.THEME_DEFAULT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Title)
        font.setBold(True)
        painter.setFont(font)
        metrics = QtGui.QFontMetrics(font)
        title = QtGui.QFontMetrics(font).elidedText(title, Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop, title)
        artist = data['artist']
        rect = QtCore.QRect(cellRect.x() + 17, cellRect.y() + 22 + 155 + 10 + 25, 155, 50)
        painter.setPen(LPGlobalUI.THEME_LIGHT_COLOR)
        font = QtGui.QFont()
        font.setPointSizeF(ItemCard_Subtitle)
        painter.setFont(font)
        textLayout = QtGui.QTextLayout(artist, font)
        height = 0
        lineWidth = rect.width()
        textLayout.beginLayout()
        metrics = QtGui.QFontMetrics(font)
        leading = metrics.leading()
        height = -leading
        line = textLayout.createLine()
        if not line.isValid():
            pass
        else:
            line.setLineWidth(lineWidth)
            height += leading
            line.setPosition(QtCore.QPointF(0, height))
            height += line.height()
        textLayout.endLayout()
        if textLayout.lineCount() >= 3:
            line1 = textLayout.lineAt(0)
            line2 = textLayout.lineAt(1)
            line3 = textLayout.lineAt(2)
            lineText = artist[line2.textStart():line2.textStart() + line2.textLength()] + artist[line3.textStart():line3.textStart() + line3.textLength()]
            lineText = metrics.elidedText(lineText, Qt.TextElideMode.ElideRight, rect.width())
            artist = artist[0:line1.textLength()] + lineText
        boundingRect = painter.boundingRect(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.TextFlag.TextWordWrap, artist)
        if superListView.lastCursorPos and superListView.lastCursorPos in boundingRect:
            font.setUnderline(True)
            painter.setFont(font)
            superListView.lastCursorActionIndex = index
        else:
            font.setUnderline(False)
            painter.setFont(font)
            if superListView.lastCursorActionIndex == index:
                superListView.lastCursorActionIndex = None
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.TextFlag.TextWordWrap, artist)
        if superListView.lastCursorPos:
            if not cellRect.contains(superListView.lastCursorPos) and playIconRect.contains(superListView.lastCursorPos):
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                superListView.setCursor(QtGui.QCursor(Qt.CursorShape.ArrowCursor))

    __classcell__ = None


class LPMyMusicAlbumsViewController(QWidget):
    updateLibSignal = pyqtSignal(object)
    
    def __init__(self = None, showImportWaitingDialogMethod = None, updateImportWaitingDialogMethod = None):
        super(LPMyMusicAlbumsViewController, self).__init__()
        self.filterArray = [
            {
                'id': 'album',
                'title': QCoreApplication.translate('Albums', 'AlphaBetical') },
            {
                'id': 'artist',
                'title': QCoreApplication.translate('Albums', 'Artist') },
            {
                'id': 'dateadd',
                'title': QCoreApplication.translate('Albums', 'Date Added') }]
        self.showImportWaitingDialogMethod = showImportWaitingDialogMethod
        self.updateImportWaitingDialogMethod = updateImportWaitingDialogMethod
        
        def _updateLib():
            self.searchFieldClearAction.setVisible(True)
            self.searchField.setText('')
            playList = LPBeetsWrapper.queryAlbums('', self.filterArray[0]['id'], **('key', 'sortBy'))
            model = LPMyMusicAlbumsListModel(playList)
            self.listView.setModel(model)

        self.updateLibSignal.connect(_updateLib)

    
    def setupUi(self = None, ui = None):
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.addButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n\nQPushButton:hover {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}        ' % (LPGlobalUI.THEME_BUTTON_BACK_COLOR.name(), LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name()))
        self.addButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        None((lambda : LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.MyMusicViewControllerUI, Ui_mymusicViewWidget, LPMyMusicViewController, self.showImportWaitingDialogMethod, self.updateImportWaitingDialogMethod), 'mymusic')))
        self.searchField.textChanged.connect(self.searchFieldChanged)
        self.searchFieldClearAction = QAction('clear', self)
        self.searchFieldClearAction.setIcon(QtGui.QIcon(LPGlobalUI.imagePath('search_close.png')))
        self.searchField.addAction(self.searchFieldClearAction, QLineEdit.ActionPosition.TrailingPosition)
        None((lambda : self.searchField.clear()))
        self.searchFieldClearAction.setVisible(False)
        self.filterBox.setupUI()
        itemsArray = []
        for item in self.filterArray:
            itemsArray.append(item['title'])
        self.filterBox.addItems(itemsArray)
        self.filterBox.currentIndexChanged.connect(self.filterIndexChanged)
        self.listView.verticalScrollBar().setSingleStep(40)
        playList = LPBeetsWrapper.queryAlbums('', self.filterArray[0]['id'], **('key', 'sortBy'))
        model = LPMyMusicAlbumsListModel(playList)
        self.listView.setModel(model)
        delegate = LPMyMusicAlbumDelegate()
        delegate.mouseClicked.connect(self.itemClick)
        self.listView.setItemDelegate(delegate)
        stylesheetTemplate = Template('\n                QLabel#titleLabel {\n                    font-size: ${stackWidgetTiteFontSize}pt;\n                }\n                LPLineEdit {\n                    background-color: rgb(31, 31, 31); \n                    color: white; \n                    padding: 5px; \n                    border-radius: 5px; \n                    qproperty-placeholderColor: rgba(255, 255, 255, 89);\n                }\n        ')
        self.setStyleSheet(stylesheetTemplate.substitute(f'''{StackWidget_Title}''', **('stackWidgetTiteFontSize',)))

    
    def viewWillAppear(self):
        self.updateUI(LPGlobalUI.currentDevice)
        LPUtility.addNotificationObserver('LibUpdateNotify', self._libUpdateMethod)

    
    def viewWillDisappear(self):
        LPUtility.removeNotificationObserver('LibUpdateNotify', self._libUpdateMethod)

    
    def changeEvent(self = None, event = None):
        if event.type() == QEvent.Type.LanguageChange:
            self.noteLabel.setText(QCoreApplication.translate('Albums', 'Add some music to start experiencing WiiM Home!'))
            self.filterArray = [
                {
                    'id': 'album',
                    'title': QCoreApplication.translate('Albums', 'AlphaBetical') },
                {
                    'id': 'artist',
                    'title': QCoreApplication.translate('Albums', 'Artist') },
                {
                    'id': 'dateadd',
                    'title': QCoreApplication.translate('Albums', 'Date Added') }]
            self.filterBox.clear()
            itemsArray = []
            for item in self.filterArray:
                itemsArray.append(item['title'])
            self.filterBox.addItems(itemsArray)
        return super(LPMyMusicAlbumsViewController, self).changeEvent(event)

    
    def _libUpdateMethod(self, params):
        self.updateLibSignal.emit(params)

    
    def itemClick(self, index, clickType):
        data = index.data()
        albumName = data.get('album', None)
        if clickType == 'play':
            playList = LPBeetsWrapper.queryTracks(albumName, True, **('album', 'strict'))
            device = LPGlobalUI.currentDevice
            if not device:
                logger.error('error, no device found')
                return None
            
            def playFinishMethod(result = None):
                logger.debug('Mymusic album %s play result: %s' % (albumName, result))
                if result:
                    LPRecentlyManager.instance().addRecentlyPlayedWithMusicList(playList, {
                        'openMore': False,
                        'canNavigate': True })

            if albumName:
                headTitle = albumName
            else:
                headTitle = 'MyMusic Album'
            playList.header.headTitle = headTitle
            playList.header.headType = LPHeaderType.LP_HEADER_TYPE_ALBUM
            playList.header.imageUrl = data.get('imageUrl', None)
            if not data.get('mb_albumid'):
                if not albumName:
                    pass
                if not data.get('artist'):
                    pass
            playList.header.headId = '%s|%s' % ('', '')
            device.fastPlay(playList, playFinishMethod)
        elif clickType == 'enter':
            LPGlobalUI.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.MyMusicAlbumDetailViewControllerUI, Ui_mymusicAlbumDetailViewWidget, LPMyMusicAlbumDetailViewController, data), 'albumdetail')
        elif clickType == 'artist':
            artists = LPBeetsWrapper.queryAlbumArtists(data['artist'])
            if len(artists) == 0:
                return None
            None.navigationManager.push(LPGlobalUI.loadUI(LPUIPath.MyMusicArtistDetailViewControllerUI, Ui_mymusicArtistDetailViewWidget, LPMyMusicArtistDetailViewController, artists[0]), 'artistdetail')

    
    def updateUI(self, device):
        data = self.listView.model()._data
        if data is None or len(data) == 0:
            self.noteLabel.setText(QCoreApplication.translate('Albums', 'Add some music to start experiencing WiiM Home!'))
            self.stackedWidget.setCurrentIndex(1)
            self.filterBox.hide()
            self.searchField.hide()
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.filterBox.show()
            self.searchField.show()

    
    def itemDoubleClick(self, index):
        pass

    
    def searchFieldChanged(self, text):
        self.searchFieldClearAction.setVisible(len(text) > 0)
        itemId = self.filterArray[self.filterBox.currentIndex()]['id']
        playList = LPBeetsWrapper.queryAlbums(text, itemId, **('key', 'sortBy'))
        model = LPMyMusicAlbumsListModel(playList)
        self.listView.setModel(model)

    
    def filterIndexChanged(self, index):
        itemId = self.filterArray[index]['id']
        playList = LPBeetsWrapper.queryAlbums(self.searchField.text(), itemId, **('key', 'sortBy'))
        model = LPMyMusicAlbumsListModel(playList)
        self.listView.setModel(model)

    __classcell__ = None

