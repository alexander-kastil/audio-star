# Source Generated with Decompyle++
# File: LPMacSparkleUpdater.pyc (Python 3.9)

'''
macOS Sparkle 更新管理模块。

该模块负责：
1. 加载 Sparkle.framework；
2. 初始化 Sparkle Updater Controller；
3. 根据架构选择 appcast feed；
4. 提供自动检查与手动检查更新入口。
'''
import json
import os
import platform
import sys
import logging
import threading
import xml.etree.ElementTree
ET = ElementTree
etree
from pathlib import Path
import requests
logger = logging.getLogger('linkplay')
_SparkleUpdaterDelegateClass = None

def _ensureSparkleDelegateClasses():
    '''
    创建并缓存 Sparkle 所需的 updater delegate / user driver delegate 类。

    参数:
        无
    返回:
        type: updater delegate 类
    '''
    global _SparkleUpdaterDelegateClass
    if _SparkleUpdaterDelegateClass is not None:
        return _SparkleUpdaterDelegateClass
    import objc
    NSObject = NSObject
    import Foundation
    
    def LPSparkleUpdaterDelegate():
        '''_ensureSparkleDelegateClasses.<locals>.LPSparkleUpdaterDelegate'''
        __doc__ = 'Sparkle updater delegate 桥接类。'
        
        def initWithOwner_(self = None, owner = None):
            '''
            以 owner 对象初始化 delegate。

            参数:
                owner (LPMacSparkleUpdater): 当前 macOS Sparkle 更新器实例
            返回:
                object: 初始化后的 delegate 实例
            '''
            self = objc.super(LPSparkleUpdaterDelegate, self).init()
            if self is None:
                return None
            self._owner = None
            return self

        
        def updater_didFindValidUpdate_(self, updater, item):
            '''
            Sparkle 发现可用更新时触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 可用更新对应的 appcast item
            返回:
                无
            '''
            version_string = None
        # WARNING: Decompyle incomplete

        
        def updater_willDownloadUpdate_withRequest_(self, updater, item, request):
            '''
            Sparkle 即将开始下载更新包时触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 待下载更新对应的 appcast item
                request (object): Sparkle 将用于下载的请求对象
            返回:
                无
            '''
            version_string = self._owner._extractDisplayVersionFromItem(item)
            logger.info('[sparkle.delegate] willDownloadUpdate updater=%s version=%s', type(updater).__name__, version_string)
            detail = self._owner._setLastCheckDetail('found', 'sparkle_delegate_download_start', version_string, self._owner._currentAppVersion(), **('resultKind', 'source', 'latestVersion', 'currentVersion'))
            self._owner.notifyDownloadLifecycle('download_started', detail)

        
        def updater_didDownloadUpdate_(self, updater, item):
            '''
            Sparkle 成功下载更新包后触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 已下载更新对应的 appcast item
            返回:
                无
            '''
            version_string = self._owner._extractDisplayVersionFromItem(item)
            logger.info('[sparkle.delegate] didDownloadUpdate updater=%s version=%s', type(updater).__name__, version_string)
            detail = self._owner._setLastCheckDetail('found', 'sparkle_delegate_download_success', version_string, self._owner._currentAppVersion(), **('resultKind', 'source', 'latestVersion', 'currentVersion'))
            self._owner.notifyDownloadLifecycle('download_succeeded', detail)

        
        def updater_failedToDownloadUpdate_error_(self, updater, item, error):
            '''
            Sparkle 下载更新包失败时触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 下载失败更新对应的 appcast item
                error (object): 下载失败错误对象
            返回:
                无
            '''
            version_string = self._owner._extractDisplayVersionFromItem(item)
            if not error:
                pass
            error_message = str('')
            error_code = self._owner._extractNSErrorCode(error)
            error_category = self._owner._classifyCheckError(error_message)
            logger.warning('[sparkle.delegate] failedToDownloadUpdate updater=%s version=%s error=%s code=%s category=%s', type(updater).__name__, version_string, error_message, error_code, error_category)
            detail = self._owner._setLastCheckDetail('error', 'sparkle_delegate_download_failed', version_string, self._owner._currentAppVersion(), error_category, error_code, error_message, **('resultKind', 'source', 'latestVersion', 'currentVersion', 'errorCategory', 'errorCode', 'errorMessage'))
            self._owner.notifyDownloadLifecycle('download_failed', detail)

        
        def userDidCancelDownload_(self, updater):
            '''
            Sparkle 下载阶段被用户取消时触发。

            参数:
                updater (object): Sparkle updater 对象
            返回:
                无
            '''
            logger.info('[sparkle.delegate] userDidCancelDownload updater=%s', type(updater).__name__)
            detail = self._owner._setLastCheckDetail('error', 'sparkle_delegate_download_cancelled', self._owner._currentAppVersion(), 'user_cancelled', '', 'user cancelled download', **('resultKind', 'source', 'currentVersion', 'errorCategory', 'errorCode', 'errorMessage'))
            self._owner.notifyDownloadLifecycle('download_cancelled', detail)

        
        def updater_willInstallUpdate_(self, updater, item):
            '''
            Sparkle 即将安装更新时触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 即将安装的 appcast item
            返回:
                无
            '''
            version_string = self._owner._extractDisplayVersionFromItem(item)
            logger.info('[sparkle.delegate] willInstallUpdate updater=%s version=%s', type(updater).__name__, version_string)
            detail = self._owner._setLastCheckDetail('found', 'sparkle_delegate_install', version_string, self._owner._currentAppVersion(), **('resultKind', 'source', 'latestVersion', 'currentVersion'))
            self._owner.notifyInstallWillStart(detail)

        
        def updater_willInstallUpdateOnQuit_immediateInstallationBlock_(self, updater, item, immediateInstallHandler):
            '''
            Sparkle 计划在退出时安装更新时触发。

            参数:
                updater (object): Sparkle updater 对象
                item (object): 待安装更新对应的 appcast item
                immediateInstallHandler (object): 立即安装回调句柄
            返回:
                bool: 返回 False 表示继续由 Sparkle 默认流程处理安装。
            '''
            version_string = self._owner._extractDisplayVersionFromItem(item)
            logger.info('[sparkle.delegate] willInstallUpdateOnQuit updater=%s version=%s', type(updater).__name__, version_string)
            detail = self._owner._setLastCheckDetail('found', 'sparkle_delegate_install_on_quit', version_string, self._owner._currentAppVersion(), **('resultKind', 'source', 'latestVersion', 'currentVersion'))
            self._owner.notifyInstallWillStart(detail)
            return False

        
        def updaterDidNotFindUpdate_(self, updater):
            '''
            Sparkle 未发现可用更新时触发。

            参数:
                updater (object): Sparkle updater 对象
            返回:
                无
            '''
            logger.info('[sparkle.delegate] updaterDidNotFindUpdate updater=%s', type(updater).__name__)
            detail = self._owner._setLastCheckDetail('no_update', 'sparkle_delegate', self._owner._currentAppVersion(), **('resultKind', 'source', 'currentVersion'))
            self._owner.notifyNoUpdateFound(detail)

        
        def updater_didNotFindUpdateWithLatestAppcastItem_hostToLatestAppcastItemComparisonResult_background_(self, updater, appcastItem, comparisonResult, background):
            '''
            Sparkle 以标准 no-update selector 返回“当前已是最新版本”时触发。

            参数:
                updater (object): Sparkle updater 对象
                appcastItem (object): 最新 appcast item
                comparisonResult (object): 本地版本与最新版本比较结果
                background (bool): 是否后台检查
            返回:
                无
            '''
            version_string = None
        # WARNING: Decompyle incomplete

        
        def updaterDidNotFindUpdate_error_(self, updater, error):
            '''
            Sparkle 未发现可用更新且携带错误信息时触发。

            参数:
                updater (object): Sparkle updater 对象
                error (object): Sparkle 返回的错误对象
            返回:
                无
            '''
            error_desc = str(error)
            if 'You’re up to date!' in error_desc or "You're up to date!" in error_desc:
                logger.info('[sparkle.delegate] no update found updater=%s detail=%s', type(updater).__name__, error_desc)
                detail = self._owner._setLastCheckDetail('no_update', 'sparkle_delegate', self._owner._currentAppVersion(), error_desc, **('resultKind', 'source', 'currentVersion', 'errorMessage'))
            else:
                logger.warning('[sparkle.delegate] update cycle finished with non-fatal no-update error updater=%s error=%s', type(updater).__name__, error_desc)
                detail = self._owner._setLastCheckDetail('error', 'sparkle_delegate', self._owner._currentAppVersion(), 'updater_sdk', error_desc, **('resultKind', 'source', 'currentVersion', 'errorCategory', 'errorMessage'))
            self._owner.notifyNoUpdateFound(detail)

        
        def updater_didFinishLoadingAppcast_(self, updater, appcast):
            '''
            Sparkle 完成 appcast 加载时触发，仅用于调试。

            参数:
                updater (object): Sparkle updater 对象
                appcast (object): Sparkle appcast 对象
            返回:
                无
            '''
            logger.info('[sparkle.delegate] didFinishLoadingAppcast updater=%s appcast=%s', type(updater).__name__, type(appcast).__name__)

        
        def updater_didFinishUpdateCycleForUpdateCheck_error_(self, updater, updateCheck, error):
            '''
            Sparkle 完成一次更新周期时触发，仅用于调试收尾。

            参数:
                updater (object): Sparkle updater 对象
                updateCheck (object): 本轮检查类型
                error (object): 检查错误对象
            返回:
                无
            '''
            logger.info('[sparkle.delegate] didFinishUpdateCycle updater=%s updateCheck=%s error=%s', type(updater).__name__, updateCheck, error)


    LPSparkleUpdaterDelegate = None(LPSparkleUpdaterDelegate, 'LPSparkleUpdaterDelegate', NSObject)
    _SparkleUpdaterDelegateClass = LPSparkleUpdaterDelegate
    return _SparkleUpdaterDelegateClass


class LPMacSparkleUpdater:
    '''封装 Sparkle 更新流程，提供初始化和触发检查更新能力。'''
    
    def __init__(self):
        '''
        初始化 Sparkle 更新器状态。

        参数:
            无
        返回:
            无
        '''
        self._objc = None
        self._updater_controller = None
        self._updater = None
        self._updater_delegate = None
        self._sparkle_loaded = False
        self._ready = False
        self._config = self._loadConfig()
        self._backgroundCheckThread = None
        self._onUpdateFoundCallback = None
        self._onNoUpdateFoundCallback = None
        self._onInstallWillStartCallback = None
        self._onDownloadLif