# Source Generated with Decompyle++
# File: LPRecentlyPlayedViewController.pyc (Python 3.9)

__doc__ = '\nRecently Played 页面主控制器。\n\n职责：\n- 懒加载 QML 页面（LPRecentlyPlayed.qml）\n- 监听 Recently 变更通知和当前设备媒体信息变化，刷新数据与播放态高亮\n- 维护 List / Card 两套数据模型\n- 处理点击与右键菜单删除流程\n- 把点击事件经 LPStreamServiceManager.recentlyDidSelect 分发给对应音源\n'
import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QCoreApplication, QModelIndex, QPoint, pyqtSignal, pyqtProperty, pyqtSlot, Qt, QUrl, QTimer
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPMusicLibrary.LPRecentlyManager import LPRecentlyManager, RECENTLY_PLAYED_CHANGED_NOTIFY
from LPClientFramework.LPUtility import getCacheImageUrl, logger
from LPClientFramework.LPDeviceStreamServiceManager import DEVICE_ACCOUNT_UNKNOWN
from LPClientFramework.LPStreamServiceManager import canFavorite, favoriteState, favoriteStateNeedsResync, favoriteStatus, recentlyCanPreset, recentlyDidSelect, recentlyFavoriteItemData, recentlyFavoriteTarget, recentlyOpensDetail, recentlyPlayListFromDetail, recentlyResourceUnavailable, playRecently, requestFavoriteResync, setFavorite, supportContents
from HOME.RecentlyPlayed.LPRecentlyViewPreference import LPRecentlyViewPreference
# WARNING: Decompyle incomplete
