# Source Generated with Decompyle++
# File: LPTidalNetworkDiagnostics.pyc (Python 3.9)

'''
TIDAL QML 网络缓存诊断工具。
'''
from pathlib import Path
import logging
from typing import Optional
from PyQt6.QtCore import QObject
from PyQt6.QtNetwork import QNetworkDiskCache, QNetworkReply, QNetworkRequest
from PyQt6.QtQuickWidgets import QQuickWidget
logger = logging.getLogger('linkplay')

class _LPTidalQmlNetworkDiagnostics(QObject):
    '''记录 TIDAL QML 网络回复的缓存命中和图片加载信息。'''
    
    def __init__(self = None, tag = None, parent = None):
        '''
        初始化 QML 网络诊断对象。

        :param tag: 页面标识。
        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        if not tag:
            pass
        self._tag = str('tidal_qml')

    
    def logReply(self = None, reply = None):
        '''
        记录一次 QML 网络回复。

        :param reply: Qt 网络回复对象。
        :return: None。
        '''
        if reply is None:
            return None
        url = None.url().toString()
        content_type = self._raw_header(reply, b'Content-Type')
        if not content_type.lower().startswith('image/'):
            pass
        is_image = self._looks_like_image_url(url)
        if not is_image:
            return None
        status_code = None.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        from_cache = bool(reply.attribute(QNetworkRequest.Attribute.SourceIsFromCacheAttribute))
        content_length = self._raw_header(reply, b'Content-Length')
        cache_control = self._raw_header(reply, b'Cache-Control')
        error_code = int(reply.error().value)
        error_text = '' if reply.error() == QNetworkReply.NetworkError.NoError else reply.errorString()
        logger.debug('[TidalQmlImage][CacheTrace] tag=%s url=%s status=%s from_cache=%s content_type=%s content_length=%s cache_control=%s bytes_available=%s error_code=%s error=%s', self._tag, url, status_code, from_cache, content_type, content_length, cache_control, reply.bytesAvailable(), error_code, error_text)

    
    def _raw_header(self = None, reply = None, headerName = None):
        '''
        读取网络回复原始头。

        :param reply: Qt 网络回复对象。
        :param headerName: Header 名称。
        :return: Header 字符串。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _looks_like_image_url(self = None, url = None):
        '''
        判断 URL 是否像图片资源。

        :param url: 资源 URL。
        :return: 像图片资源返回 True。
        '''
        if not url:
            pass
        suffix = Path(str('').split('?', 1)[0]).suffix.lower()
        return suffix in frozenset({'.jpeg', '.gif', '.svg', '.webp', '.jpg', '.png'})

    __classcell__ = None


def installTidalQmlNetworkDiagnostics(quickWidget = None, tag = None):
    '''
    为 TIDAL QQuickWidget 安装图片磁盘缓存和诊断日志。

    :param quickWidget: TIDAL QQuickWidget。
    :param tag: 页面标识。
    :return: None。
    '''
    if quickWidget is None:
        return None
    cacheCoverDir = cacheCoverDir
    import LPClientFramework.LPUtility
    img_cache = QNetworkDiskCache(quickWidget)
    img_cache.setCacheDirectory(str(cacheCoverDir))
    img_cache.setMaximumCacheSize(209715200)
    manager = quickWidget.engine().networkAccessManager()
    manager.setCache(img_cache)
    diagnostics = _LPTidalQmlNetworkDiagnostics(tag, quickWidget)
    manager.finished.connect(diagnostics.logReply)
    quickWidget._tidal_network_diagnostics = diagnostics
    if not tag:
        pass
    logger.debug('[TidalQmlImage][CacheTrace] installed tag=%s cache_dir=%s max_bytes=%s', str('tidal_qml'), str(cacheCoverDir), img_cache.maximumCacheSize())

