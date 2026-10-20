# Source Generated with Decompyle++
# File: LPQobuzUtil.pyc (Python 3.9)

'''
@Time ： 2025/6/19 14:57
@Auth ： Chris
@File ：LPQobuzUtil.py
@Desc:
'''
import hashlib
import os
import re
import threading
import time
from datetime import datetime
from enum import Enum
import requests
from PyQt6 import QtGui
from PyQt6.QtCore import QRect, Qt, QModelIndex, QSortFilterProxyModel, QObject, QEvent, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap, QPainter, QFontMetrics, QIcon
from PyQt6.QtWidgets import QListView, QPushButton
from urllib3.exceptions import InsecureRequestWarning
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPCache.LPFileCache import FileCache
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType
from LPClientFramework.LPUtility import requestSession
qobuzHeadTypeMapping = {
    LPHeaderType.LP_HEADER_TYPE_ARTIST: 'artists',
    LPHeaderType.LP_HEADER_TYPE_SONG: 'tracks',
    LPHeaderType.LP_HEADER_TYPE_PLAYLIST: 'playlists',
    LPHeaderType.LP_HEADER_TYPE_ALBUM: 'albums' }
playlistPixMapRequestingArray = []
playlistPixMapRequestingArrayLock = threading.Lock()

class QListViewWheelBlocker(QObject):
    
    def eventFilter(self, obj, event):
        if isinstance(obj, QListView) and event.type() == QEvent.Type.Wheel:
            return True



def getMyPlaylistCustomCoverImage(imageUrlList = None, width = None):
    '''
    1 2
    3 4
    imageUrlList    有四张不同的直接按上面顺序拼
                    有三张不同的，4的位置放第一张
                    有两张不同的， 中心对称
                    只有一张，4个位置都一样
    '''
    hasDone = True
    pixmapList = []
    for url in imageUrlList:
        pixmap = LPUtility.getCachedPixmapWithUrl(url, 155)
        if not pixmap:
            hasDone = False
        else:
            pixmapList.append(pixmap)
        if hasDone:
            pix = composeFourPixmaps(pixmapList, width)
        else:
            pix = QPixmap(LPGlobalUI.imagePath('playlist_l.png'))
    return pix


def composeFourPixmaps(pixmaps = None, width = None):
    if not pixmaps:
        logger.debug('[composeFourPixmaps] empty pixmaps')
        return QPixmap(LPGlobalUI.imagePath('playlist_l.png'))
    if None(pixmaps) > 4:
        pixmaps = pixmaps[:4]
    length = len(pixmaps)
    if length == 3:
        pixmaps.append(pixmaps[0])
    elif length == 2:
        pixmaps.extend(reversed(pixmaps))
    elif length == 1:
        pixmaps.extend(pixmaps * 3)
    targetPixmap = QPixmap(width, width)
    targetPixmap.fill()
    painter = QPainter(targetPixmap)
    cellSize = width // 2 + 1
    for i in range(2):
        for j in range(2):
            index = i * 2 + j
            pixmap = pixmaps[index].scaled(cellSize, cellSize)
            targetRect = QRect(j * cellSize, i * cellSize, cellSize, cellSize)
            painter.drawPixmap(targetRect, pixmap)
    painter.end()
    return targetPixmap


def formatAlbumDuration(duration):
    '''
    duration: int ms detail header展示
    '''
    seconds = duration / 1000
    seconds = seconds % 86400
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if hour != 0:
        return '%02dh %02dm %02ds' % (hour, minutes, seconds)
    return None % (minutes, seconds)


def formatTrackDuration(duration):
    '''
    duration: int ms
    '''
    seconds = duration / 1000
    seconds = seconds % 86400
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if hour != 0:
        return '%d:%02d:%02d' % (hour, minutes, seconds)
    return None % (minutes, seconds)


def formatDate(dateStr):
    dateObj = datetime.strptime(dateStr, '%Y-%m-%d')
    return dateObj.strftime('%B %d, %Y')


def setElidedText(label, text):
    metrics = QFontMetrics(label.font())
    elided = metrics.elidedText(text, Qt.TextElideMode.ElideRight, label.width())
    label.setText(elided)


def cacheShuffleId(fileCache = None, type = None, ItemId = None, opt = {
    'fileCache': FileCache,
    'type': Enum }):
    fileCache.updateCache(type, updateShuffleIdData, ItemId, opt)


def updateShuffleIdData(type = None, oldData = None, ItemId = None, opt = {
    'type': Enum }):
    key = type.value
    ids = set(oldData[key])
    if opt == 'add':
        ids.add(ItemId)
    else:
        ids.discard(ItemId)
    oldData[key] = list(ids)
    return oldData


def cachePlaylistId(fileCache = None, type = None, cachePlaylistId = None):
    logger.debug(f'''cache playlist id len = {len(cachePlaylistId)}''')
    data = {
        'time': int(time.time()),
        type.value: cachePlaylistId }
    fileCache.writeCache(type, data)


def cacheWeeklyShuffle(fileCache = None, type = None, isShuffle = None):
    logger.debug(f'''cache weeklyQ isShuffle = {isShuffle}''')
    data = {
        type.value: [
            isShuffle] }
    fileCache.writeCache(type, data)


def scrollByItems(direction = None, listView = None, step = None):
    '''
    每次点击滑动 3 个 item
    :param direction: +1 向右, -1 向左
    '''
    bar = listView.horizontalScrollBar()
    change = direction * step
    newValue = bar.value() + change
    newValue = max(0, min(newValue, bar.maximum()))
    bar.setValue(newValue)


def updateListViewNavButtons(bar, leftButton, rightButton):
    leftButton.setEnabled(bar.value() > bar.minimum())
    rightButton.setEnabled(bar.value() < bar.maximum())
    if leftButton.isEnabled():
        leftButton.setCursor(Qt.CursorShape.PointingHandCursor)
        leftButton.setIcon(QIcon(LPGlobalUI.imagePath('nav_prev.png')))
    else:
        leftButton.setCursor(Qt.CursorShape.ArrowCursor)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('nav_prev.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        leftButton.setIcon(QIcon(tintImage))
    if rightButton.isEnabled():
        rightButton.setCursor(Qt.CursorShape.PointingHandCursor)
        rightButton.setIcon(QIcon(LPGlobalUI.imagePath('nav_next.png')))
    else:
        rightButton.setCursor(Qt.CursorShape.ArrowCursor)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath('nav_next.png'), LPGlobalUI.THEME_DISABLE_COLOR)
        rightButton.setIcon(QIcon(tintImage))


def _setCategoryOffset(container, contentWidget, offset):
    '''
    设置按钮行偏移并移动内容,按内容宽度与容器宽度联动更新箭头。

    按钮行偏移保存在容器属性 _qobuzNavOffset 上;最大偏移 = 内容宽度 -
    容器宽度。箭头显隐直接由偏移判断,不再依赖 QScrollArea 滚动条。

    参数:
        container (QWidget): 裁剪分类按钮行的普通容器
        contentWidget (QWidget): 按钮行容器(buttonFrame)
        offset (int): 期望的偏移量(会被夹到 [0, 最大偏移])
    返回:
        int: 实际生效的偏移量
    '''
    maxOffset = max(0, contentWidget.width() - container.width())
    offset = min(max(offset, 0), maxOffset)
    setattr(container, '_qobuzNavOffset', offset)
    contentWidget.move(-offset, 0)
    contentWidget.resize(contentWidget.width(), container.height())
    navPrevButton = getattr(container, '_qobuzNavPrevButton', None)
    navNextButton = getattr(container, '_qobuzNavNextButton', None)
    if navPrevButton is not None:
        navPrevButton.setVisible(offset > 0)
    if navNextButton is not None:
        navNextButton.setVisible(offset < maxOffset)
    return offset


def createCategoryNavButton(container, contentWidget, direction):
    '''
    创建分类按钮行的翻页箭头按钮,并插入分类容器所在的父布局。

    按钮本身不依靠滚动条:点击后按"内容宽度减容器宽度"的最大偏移量翻
    一页(页宽 = 容器宽),偏移保存在容器属性 _qobuzNavOffset 上,由
    _setCategoryOffset 统一移动按钮行并更新左右箭头。

    参数:
        container (QWidget): 裁剪分类按钮行的普通容器(须已加入父布局)
        contentWidget (QWidget): 按钮行容器(buttonFrame),作为 container 的子控件
        direction (int): -1 创建左侧(向前)箭头并插入布局首位, +1 创建右侧(向后)箭头并追加到布局末尾
    返回:
        QPushButton: 创建的箭头按钮
    '''
    iconPath = 'nav_prev.png' if direction < 0 else 'nav_next.png'
    button = QPushButton()
    pixmap = LPUtility.tintImage(LPGlobalUI.imagePath(iconPath), LPGlobalUI.THEME_BUTTON_DEFAULT_COLOR_UI)
    button.setIcon(QIcon(pixmap))
    button.setFixedSize(25, 25)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setStyleSheet('background-color: transparent; border: none;')
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    None((lambda : scrollCategoryByPage(container, contentWidget, direction)))
    parentLayout = container.parentWidget().layout() if container.parentWidget() else None
    if parentLayout is not None:
        if direction < 0:
            parentLayout.insertWidget(0, button, 0, Qt.AlignmentFlag.AlignVCenter)
        else:
            parentLayout.addWidget(button, 0, Qt.AlignmentFlag.AlignVCenter)
    return button


def updateCategoryNavButtons(container, contentWidget):
    '''
    根据按钮行内容宽度与容器宽度更新左右翻页箭头可见性,并校正偏移。

    左侧箭头:偏移大于 0(已向右移动)时显示;
    右侧箭头:偏移小于最大偏移(右侧仍有未显示内容)时显示;
    隐藏的箭头不占用布局空间。窗口尺寸或按钮行内容变化后调用即可。

    参数:
        container (QWidget): 裁剪分类按钮行的普通容器
        contentWidget (QWidget): 按钮行容器(buttonFrame)
    返回:
        None
    '''
    offset = getattr(container, '_qobuzNavOffset', 0)
    _setCategoryOffset(container, contentWidget, offset)


def scrollCategoryByPage(container, contentWidget, direction):
    '''
    分类按钮行按页偏移:一页 = 容器宽度(视口)。

    参数:
        container (QWidget): 裁剪分类按钮行的普通容器
        contentWidget (QWidget): 按钮行容器(buttonFrame)
        direction (int): +1 向后(右)翻页, -1 向前(左)翻页
    返回:
        None
    '''
    viewWidth = max(1, container.width())
    offset = getattr(container, '_qobuzNavOffset', 0)
    maxOffset = max(0, contentWidget.width() - container.width())
    if direction > 0:
        newOffset = min(offset + viewWidth, maxOffset)
    else:
        newOffset = max(offset - viewWidth, 0)
    _setCategoryOffset(container, contentWidget, newOffset)


def deleteRow(tableView = None, proxyIndex = None):
    model = tableView.model()
    if isinstance(model, QSortFilterProxyModel):
        sourceIndex = model.mapToSource(proxyIndex)
        sourceModel = model.sourceModel()
        sourceModel.removeRow(sourceIndex.row())
    else:
        model.removeRow(proxyIndex.row())


def adjustTableViewHeight(tableView):
    total = tableView.horizontalHeader().height()
    for row in range(tableView.model().rowCount()):
        total += tableView.rowHeight(row)
    tableView.setFixedHeight(total)


def clearSpecificWidgetsFromLayout(layout, targetTypes):
