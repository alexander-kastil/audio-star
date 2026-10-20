# Source Generated with Decompyle++
# File: LPTidalQmlContext.pyc (Python 3.9)

'''TIDAL QML 共享上下文注入工具。'''
from pathlib import Path
from PyQt6.QtCore import QUrl, QObject
from PyQt6.QtQml import QQmlContext
from typing import Optional
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import Big_Title, Main_Text, Min_Text, Small_Title, Sub_Text, Sub_Title, getFontFamily, getMonospaceFontFamily
_TIDAL_QML_BASE = Path(__file__).resolve().parents[4] / 'resources' / 'qml' / 'Tidal'

def resolveTidalQmlUrl(qrcPath = None, relativeFileName = None):
    '''
    优先返回仓库内本地 QML 文件（开发态热改），缺失时回退 qrc 资源。

    :param qrcPath: qrc 资源路径，例如 LPUIPath.TidalHomeQML。
    :param relativeFileName: 相对 resources/qml/Tidal 的路径，例如 "pages/TidalHome.qml"。
    :return: 可直接传给 QQuickWidget.setSource 的 QUrl。
    '''
    local_path = _TIDAL_QML_BASE / relativeFileName
    if local_path.exists():
        return QUrl.fromLocalFile(str(local_path))
    return None(qrcPath)


def resolveTidalQmlPath(relativeFileName = None):
    '''
    返回本地 QML 文件绝对路径，供需要本地路径的场景使用。

    :param relativeFileName: 相对 resources/qml/Tidal 的路径。
    :return: 本地 QML 文件 Path 对象。
    '''
    return _TIDAL_QML_BASE / relativeFileName


def applyTidalSharedQmlContext(ctx = None):
    '''
    向 TIDAL QML 注入共享背景色和全局字体 token。

    :param ctx: 待写入的 QML 上下文对象。
    :return: None。
    '''
    if ctx is None:
        return None
    None.setContextProperty('tidalBgColor', LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name())
    ctx.setContextProperty('tidalBgColorUI', LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name())
    ctx.setContextProperty('tidalFontFamily', getFontFamily())
    ctx.setContextProperty('tidalMonospaceFontFamily', getMonospaceFontFamily())
    ctx.setContextProperty('tidalFontColor', LPGlobalUI.THEME_FONT_COLOR_UI.name())
    ctx.setContextProperty('tidalToastBackColor', LPGlobalUI.THEME_TOAST_BACK_COLOR.name())
    ctx.setContextProperty('tidalToastErrorBackColor', LPGlobalUI.THEME_CLOSE_BACK_COLOR.name())
    ctx.setContextProperty('tidalDefaultPointSize', 13)
    ctx.setContextProperty('tidalBigTitlePointSize', float(Big_Title))
    ctx.setContextProperty('tidalSubTitlePointSize', float(Sub_Title))
    ctx.setContextProperty('tidalSmallTitlePointSize', float(Small_Title))
    ctx.setContextProperty('tidalMainTextPointSize', float(Main_Text))
    ctx.setContextProperty('tidalSubTextPointSize', float(Sub_Text))
    ctx.setContextProperty('tidalMinTextPointSize', float(Min_Text))


def applyTidalCursorBridge(ctx = None, owner = None, quickWidget = None):
    '''
    创建并向 TIDAL QML 上下注入宿主光标同步桥。

    :param ctx: QML 上下文对象。
    :param owner: 持有 QQuickWidget 的页面控制器。
    :param quickWidget: 当前页面承载 QML 的 QQuickWidget。
    :return: None。
    '''
    if ctx is None:
        return None
    LPTidalCursorBridge = LPTidalCursorBridge
    import HOME.StreamService.Tidal.services.LPTidalCursorBridge
    cursor_bridge = getattr(owner, '_tidal_cursor_bridge', None) if owner is not None else None
    if cursor_bridge is None:
        cursor_bridge = LPTidalCursorBridge(owner)
        if owner is not None:
            setattr(owner, '_tidal_cursor_bridge', cursor_bridge)
    cursor_bridge.setQuickWidget(quickWidget)
    ctx.setContextProperty('tidalCursorBridge', cursor_bridge)


def clearTidalCursorBridge(owner = None):
    '''
    清理页面控制器持有的宿主光标状态。

    :param owner: 持有宿主光标同步桥的页面控制器。
    :return: None。
    '''
    cursor_bridge = getattr(owner, '_tidal_cursor_bridge', None) if owner is not None else None
    if cursor_bridge is None:
        return None
    None.clearHoverCursorStates()

