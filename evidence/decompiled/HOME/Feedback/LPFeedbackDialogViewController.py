# Source Generated with Decompyle++
# File: LPFeedbackDialogViewController.pyc (Python 3.9)

'''
@Time ： 2026/07/09
@Auth ： feedback
@File ：LPFeedbackDialogViewController.py
@Desc: 用户反馈弹窗的 Python 控制器。

职责：
- 作为 QQuickWidget 宿主，加载并显示 LPFeedbackDialog.qml。
- 跟随主窗口几何变化同步弹窗覆盖层位置。
- 收集 QML 表单（主题/邮箱/描述/附件），创建工单后启动一次后台日志上传。
- 通过 pyqtProperty/pyqtSignal 把提交状态（忙/错误/关闭）回传 QML。
'''
import os
import platform
from PyQt6.QtCore import QEvent, QPoint, Qt, QTimer, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QApplication, QFileDialog, QWidget
import LPGlobalUI
from LPClientFramework.LPConfig.LPFontConfig import Main_Text
from LPClientFramework.LPFeedback.LPFeedbackDraftStore import LPFeedbackDraftStore
from LPClientFramework.LPFeedback.LPFeedbackManager import LPFeedbackManager
from LPClientFramework.LPFeedback.LPFeedbackModels import LPFeedbackRequest
from LPClientFramework.LPFeedback.LPFeedbackPreferences import LPFeedbackPreferences
from LPClientFramework.LPUtility import appVersion, cacheDir, logDir, pcUUID, settings
from LPClientFramework.LPUtility import logger

class LPFeedbackDialogViewController(QWidget):
    '''用户反馈弹窗控制器。

    以覆盖整个宿主窗口的 QWidget 作为内嵌全屏遮罩层（宿主主窗口的子组件），
    内嵌 QQuickWidget 渲染全屏半透明遮罩 + 居中的反馈卡片；卡片圆角由 QML 原生处理。
    通过 setContextProperty("controller", self) 把自身暴露给 QML，QML 调用槽方法提交反馈。
    '''
    feedbackBusyChanged = pyqtSignal()
    savedEmailChanged = pyqtSignal()
    feedbackCloseRequested = pyqtSignal()
    attachmentCountChanged = pyqtSignal()
    attachmentPreviewUrlsChanged = pyqtSignal()
    _DIALOG_CARD_WIDTH = 540
    _MAX_ATTACHMENT_COUNT = 5
    
    def createForHostWindow(cls, parent = (None,)):
        '''工厂方法：创建控制器并完成 UI 初始化。

        参数:
            parent (QWidget|None): 宿主主窗口，用于几何同步与事件过滤。
        返回:
            LPFeedbackDialogViewController: 已初始化（已 setupUi）的控制器实例。
        '''
        controller = cls(parent, **('parent',))
        controller.setupUi()
        return controller

    createForHostWindow = classmethod(createForHostWindow)
    
    def __init__(self = None, parent = None):
        '''初始化覆盖整个宿主窗口的内嵌弹窗（全屏遮罩 + 居中卡片）。

        参数:
            parent (QWidget|None): 宿主主窗口，弹窗作为其子组件覆盖显示。
        '''
        super().__init__(parent)
        self.setObjectName('feedbackDialogWindow')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        if platform.system() == 'Darwin':
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        self._feedbackBusy = False
        self._feedbackPreferences = LPFeedbackPreferences(settings)
        self._savedEmail = self._feedbackPreferences.loadEmail()
        self._pendingEmail = ''
        self._attachmentCount = 0
        self._attachmentPaths = []
        self._draftStore = LPFeedbackDraftStore(settings, cacheDir / 'feedback_draft_attachments')
        self._draftSaveTimer = QTimer(self)
        self._draftSaveTimer.setSingleShot(True)
        self._draftSaveTimer.setInterval(400)
        self._draftSaveTimer.timeout.connect(self._flushDraftSave)
        self._pendingDraftText = None
        self._dialogQuickWidget = None
        self._dialogRootObject = None
        self._rootVisibleSignalBound = False
        self._rootHeightSignalBound = False
        self._hostWindow = None
        self._pendingHostWindow = parent
        self._syncingFromHostGeometry = False
        self._feedbackManager = LPFeedbackManager(self, self._provideDeviceList, **('parent', 'deviceListProvider'))
        self._feedbackManager.submissionCompleted.connect(self._onSubmissionCompleted)
        self._feedbackManager.submissionFailed.connect(self._onSubmissionFailure)
        self._feedbackManager.uploadFailed.connect(self._onUploadFailure)
        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(self._onApplicationStateChanged)

    
    def setupUi(self):
        '''创建 QQuickWidget 并加载反馈弹窗 QML，注入 controller 与主题色 token。'''
        quick = QQuickWidget(self)
        quick.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        quick.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        quick.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        quick.setClearColor(Qt.GlobalColor.transparent)
        ctx = quick.rootContext()
        ctx.setContextProperty('controller', self)
        self._applyThemeContext(ctx)
        quick.setSource(QUrl(LPGlobalUI.qmlPath('Feedback/LPFeedbackDialog.qml')))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error('FeedbackDialog QML load failed! status: %s' % quick.status())
            for err in quick.errors():
                logger.error('FeedbackDialog QML err: %s' % err.toString())
        else:
            logger.debug('FeedbackDialog QML loaded successfully!')
        None((lambda _status = None: self._bindRootSignals()))
        self._dialogQuickWidget = quick
        self._bindRootSignals()
        self._attachHostWindow(self._pendingHostWindow)
        self.hide()

    
    def _applyThemeContext(self, ctx):
        '''把全局主题色 token 注入 QML 上下文。

        参数:
            ctx (QQmlContext): QQuickWidget 的根上下文。
        '''
        ctx.setContextProperty('themeDialogBackColor', LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI)
        ctx.setContextProperty('themeButtonBackColor', LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI)
        ctx.setContextProperty('themeDefaultTextColor', LPGlobalUI.THEME_DEFAULT_COLOR)
        ctx.setContextProperty('themeLightTextColor', LPGlobalUI.THEME_LIGHT_COLOR_UI)
        ctx.setContextProperty('feedbackMainTextPointSize', float(Main_Text))

    
    def _attachHostWindow(self, hostWindow):
        '''绑定宿主窗口，安装事件过滤器以同步几何与生命周期。

        参数:
            hostWindow (QWidget|None): 宿主主窗口。
        '''
        if hostWindow is None:
            return None
        if None._hostWindow is hostWindow:
            return None
        if None._hostWindow is not None:
            self._hostWindow.removeEventFilter(self)
        self._hostWindow = hostWindow
        self._hostWindow.installEventFilter(self)
        self._syncToHostGeometry()

    
    def _syncToHostGeometry(self):
        '''同步内嵌弹窗（全屏遮罩层）几何到宿主窗口，并刷新卡片最大高度。'''
        host = self._hostWindow
        if host is None:
            return None
        if None._syncingFromHostGeometry:
            return None
        self._syncingFromHostGeometry = None
        
        try:
            top_left = host.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), host.width(), host.height())
            root = self._dialogRootObject
            if root is None:
                pass
        finally:
            self._syncingFromHostGeometry = False
            return None
            max_dialog_height = max(561, int(host.height() * 0.95))
            root.setProperty('maxDialogHeight', max_dialog_height)
            self._dialogQuickWidget.setGeometry(self.rect())
            self._syncingFromHostGeometry = False
        self._syncingFromHostGeometry = False
        return None


    
    def eventFilter(self = None, watched = None, event = None):
        '''监听宿主窗口事件，同步弹窗几何与生命周期。

        参数:
            watched (QObject): 被监听对象。
            event (QEvent): 事件。
        返回:
            bool: 是否拦截事件；其余交由父类处理。
        '''
        if watched is self._hostWindow and event is not None:
            et = event.type()
            if et in (QEvent.Type.Resize, QEvent.Type.Move, QEvent.Type.Show):
                self._syncToHostGeometry()
            elif et in (QEvent.Type.Hide, QEvent.Type.Close):
                self.closeDialog()
                self.hide()
            elif et == QEvent.Type.WindowStateChange and self._hostWindow.isMinimized():
                self.closeDialog()
                self.hide()
        return super().eventFilter(watched, event)

    
    def _onApplicationStateChanged(self, state):
        '''前后台切换回前台后，若弹窗仍打开则恢复显示并刷新层级与重绘。

        参数:
            state (Qt.ApplicationState): 应用状态。
        '''
        if state != Qt.ApplicationState.ApplicationActive:
            return None
        root = None._dialogRootObject
        if not root is None or bool(root.property('visible')):
            return None
        None._syncToHostGeometry()
        host = self._hostWindow
        if host is not None:
            host.raise_()
            host.update()
        if not self.isVisible():
            self.show()
        self.raise_()
        if self._dialogQuickWidget is not None:
            self._dialogQuickWidget.update()
        self.update()

    
    def _bindRootSignals(self):
        '''QML 加载完成后绑定根对象 visibleChanged 信号，驱动 QWidget 显隐。'''
        quick = self._dialogQuickWidget
        if quick is None or quick.status() != QQuickWidget.Status.Ready:
            return None
        root = None.rootObject()
        if root is None:
            return None
        self._dialogRootObject = None
        if not self._rootVisibleSignalBound:
            visible_changed = getattr(root, 'visibleChanged', None)
            if visible_changed:
                visible_changed.connect(self._onRootVisibleChanged)
            self._rootVisibleSignalBound = True
        if not self._rootHeightSignalBound:
            dialog_height_changed = getattr(root, 'dialogCardHeightChanged', None)
            if dialog_height_changed:
                dialog_height_changed.connect(self._onRootHeightChanged)
            self._rootHeightSignalBound = True

    
    def _onRootHeightChanged(self):
        '''QML 卡片高度变化时，重新居中内嵌弹窗。

        参数:
            无。
        返回:
            None。
        '''
        self._syncToHostGeometry()

    
    def _onRootVisibleChanged(self):
        '''QML 根 visible 变化时同步 QWidget 覆盖层的显隐。'''
        root = self._dialogRootObject
        if root is None:
            return None
        if None(root.property('visible')):
            self._syncToHostGeometry()
            if not self.isVisible():
                self.show()
            self.raise_()
            return None
        None.hide()

    
    def _setRootProperty(self, key, value):
        '''安全地设置 QML 根对象属性。

        参数:
            key (str): 属性名。
            value (object): 属性值。
        '''
        root = self._dialogRootObject
        if root is None:
            return None
        None.setProperty(key, value)

    
    def openDialog(self):
        '''打开反馈弹窗：几何同步后显示内嵌全屏遮罩 + 居中卡片。'''
        self._syncToHostGeometry()
        if self._dialogRootObject is None:
            return None
        None._setRootProperty('visible', True)
        self._syncToHostGeometry()
        if not self.isVisible():
            self.show()
        self.raise_()

    
    def closeDialog(self):
        '''关闭反馈弹窗，隐藏全屏遮罩 + 卡片。'''
        self._setRootProperty('visible', False)

    
    def feedbackBusy(self):
        '''bool: 提交是否进行中（True 时 QML 禁用按钮并显示 loading）。'''
        return self._feedbackBusy

    feedbackBusy = pyqtProperty(bool, feedbackBusyChanged, **('notify',))(feedbackBusy)
    
    def savedEmail(self):
        '''str: 上一次成功提交 Feedback 时使用的邮箱。'''
        return self._savedEmail

    savedEmail = pyqtProperty(str, savedEmailChanged, **('notify',))(savedEmail)
    
    def attachmentCount(self):
        '''int: 已选附件数量（供 QML 在附件按钮上显示角标）。'''
        return self._attachmentCount

    attachmentCount = pyqtProperty(int, attachmentCountChanged, **('notify',))(attachmentCount)
    
    def attachmentPreviewUrls(self):
        '''list[str]: 已选图片附件的本地 file URL 列表，供 QML 横向预览。'''
        return (lambda .0: [ QUrl.fromLocalFile(path).toString() for path in .0 ])(self._attachmentPaths)

    attachmentPreviewUrls = pyqtProperty('QStringList', attachmentPreviewUrlsChanged, **('notify',))(attachmentPreviewUrls)
    
    def _setBusy(self, busy):
        '''更新提交忙状态并发信号。

        参数:
            busy (bool): 是否忙。
        '''
        if self._feedbackBusy == busy:
            return None
        self._feedbackBusy = None
        self.feedbackBusyChanged.emit()

    
    def _showToast(self, message):
        '''通过应用通用 Toast 显示非邮箱校验错误。

        参数:
            message (str): 要显示的错误提示文本。
        返回:
            None。
        '''
        LPGlobalUI.toast.showToast(self.tr(message), self, 5000, **('timeout',))

    
    def _setAttachmentCount(self, count):
        '''更新附件计数并发信号。

        参数:
            count (int): 附件数量。
        '''
        if self._attachmentCount == count:
            return None
        self._attachmentCount = None
        self.attachmentCountChanged.emit()

    
    def _setAttachmentPaths(self, paths):
        '''更新图片附件路径列表，并同步计数与预览 URL 变更信号。

        参数:
            paths (list[str]): 已通过图片类型校验的本地文件路径列表。
        返回:
            None
        '''
        self._attachmentPaths = list(paths)
        self._setAttachmentCount(len(self._attachmentPaths))
        self.attachmentPreviewUrlsChanged.emit()

    
    def _attachmentPathKey(self, path):
        '''生成图片附件去重使用的归一化路径 key。

        参数:
            path (str): 本地图片文件路径。
        返回:
            str: 归一化后的真实路径 key，用于判断是否为同一张图片。
        '''
        return os.path.normcase(os.path.realpath(path))

    
    def _deduplicateImageAttachmentPaths(self, paths):
        '''按本地真实路径对图片附件去重，并保留首次出现的顺序。

        参数:
            paths (list[str]): 待去重的图片附件路径列表。
        返回:
            list[str]: 去重后的图片附件路径列表。
        '''
        deduplicatedPaths = []
        seenPathKeys = set()
        for path in paths:
            pathKey = self._attachmentPathKey(path)
            if pathKey in seenPathKeys:
                continue
            seenPathKeys.add(pathKey)
            deduplicatedPaths.append(path)
        return deduplicatedPaths

    
    def _isImageAttachmentPath(self, path):
        '''判断文件路径是否属于反馈弹窗允许上传的图片格式。

        参数:
            path (str): 本地文件路径。
        返回:
            bool: True 表示允许作为图片附件上传，否则 False。
        '''
        imageSuffixes = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
        return str(path).lower().endswith(imageSuffixes)

    
    def chooseAttachment(self):
        '''打开文件选择器，让用户选择一个或多个图片附件。

        已选满上限（5 张）时直接 Toast 提示并返回，不再打开文件选择器；
        否则选择的图片路径累加到 self._attachmentPaths，并同步附件计数和预览列表到 QML。

        参数:
            无。
        返回:
            None。
        '''
        remainCount = self._MAX_ATTACHMENT_COUNT - len(self._attachmentPaths)
        if remainCount <= 0:
            self._showToast('Maximum 5 images allowed.')
            return None
        (filePaths, _) = None.getOpenFileNames(self, self.tr('Select Images'), '', self.tr('Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)'))
        if not filePaths:
            return None
        imagePaths = (lambda .0 = None: [ path for path in .0 if self._isImageAttachmentPath(path) ])(filePaths)
        if not imagePaths:
            self._showToast('Please select image files only.')
            return None
        if None(imagePaths) > remainCount:
            self._showToast('Only the first 5 images can be attached.')
        newPaths = []
        for path in imagePaths[:remainCount]:
            cachedPath = self._draftStore.copyAttachment(path)
            newPaths.append(cachedPath if cachedPath else path)
        deduplicatedPaths = self._deduplicateImageAttachmentPaths(self._attachmentPaths + newPaths)
        self._setAttachmentPaths(deduplicatedPaths)
        self._persistDraft()
        logger.info('[Feedback] attachment selected: count=%d' % len(self._attachmentPaths))

    chooseAttachment = pyqtSlot()(chooseAttachment)
    
    def removeAttachmentAt(self, index):
        '''按索引移除一个已选图片附件。

        参数:
            index (int): QML 图片预览列表中的附件索引。
        '''
        if index < 0 or index >= len(self._attachmentPaths):
            return None
        paths = None(self._attachmentPaths)
        removedPath = paths.pop(index)
        self._setAttachmentPaths(paths)
        self._draftStore.removeAttachment(removedPath)
        self._persistDraft()
        logger.info('[Feedback] attachment removed: index=%d path=%s' % (index, removedPath))

    removeAttachmentAt = pyqtSlot(int)(removeAttachmentAt)
    
    def submitFeedback(self, subject, email, description):
        '''提交用户反馈：创建工单后启动一次后台日志上传。

        参数:
            subject (str): 反馈主题。
            email (str): 用户邮箱。
            description (str): 问题描述。
        返回:
            None。
        '''
        if not description.strip():
            self._showToast('Please enter a description.')
            return None
        None._setBusy(True)
        currentDevice = LPGlobalUI.currentDevice
        if not getattr(currentDevice, 'uuid', ''):
            pass
        deviceUuid = str('unknow')
        if not getattr(currentDevice, 'name', ''):
            pass
        request = LPFeedbackRequest(subject.strip(), email.strip(), description.strip(), list(self._attachmentPaths), str(appVersion), platform.system(), pcUUID(), deviceUuid, str(logDir), 'FeedbackDebug', self._collectOsVersion(), self._collectDeviceName(), str(''), self._collectDeviceNames(), **('subject', 'email', 'description', 'attachmentPaths', 'appVersion', 'platformName', 'appUuid', 'deviceUuid', 'logDirectory', 'feedbackType', 'osVersion', 'deviceName', 'currentDeviceName', 'deviceList'))
        self._pendingEmail = request.email
        self._feedbackManager.submit(request)

    submitFeedback = pyqtSlot(str, str, str)(submitFeedback)
    
    def saveDraft(self, subject, email, description):
        '''暂存 QML 最新草稿文本并重启防抖定时器，避免每次按键都落盘。

        参数:
            subject (str): 反馈主题。
            email (str): 用户邮箱。
            description (str): 问题描述。
        返回:
            None。
        '''
        self._pendingDraftText = (subject, email, description)
        self._draftSaveTimer.start()

    saveDraft = pyqtSlot(str, str, str)(saveDraft)
    
    def _flushDraftSave(self):
        '''防抖定时器到点：把暂存的最新草稿文本与附件一起写入存储。

        参数:
            无。
        返回:
            None。
        '''
        if self._pendingDraftText is None:
            return None
        (subject, email, description) = None._pendingDraftText
        self._persistDraftCore(subject, email, description)

    
    def flushDraft(self):
        '''关闭弹窗前强制写入最新草稿（防抖定时器尚未触发时兜底）。

        参数:
            无。
        返回:
            None。
        '''
        if self._pendingDraftText is not None:
            (subject, email, description) = self._pendingDraftText
            self._persistDraftCore(subject, email, description)
        self._draftSaveTimer.stop()

    flushDraft = pyqtSlot()(flushDraft)
    
    def discardDraft(self):
        '''用户手动关闭弹窗时丢弃填写未提交的内容。

        用于 QML 右上角 close 按钮：停止防抖写盘、丢弃待写草稿、清空磁盘草稿
        （含附件图片副本），并清空已选附件列表。下次打开弹窗回到默认预填邮箱的空表单。

        参数:
            无。
        返回:
            None。
        '''
        self._draftSaveTimer.stop()
        self._pendingDraftText = None
        self._draftStore.clear()
        self._setAttachmentPaths([])
        logger.info('[Feedback] draft discarded by manual close')

    discardDraft = pyqtSlot()(discardDraft)
    
    def _persistDraft(self):
        '''附件变化后立即写盘最新草稿（文本取最近一次暂存值，未暂存视为空）。

        参数:
            无。
        返回:
            None。
        '''
        if not self._pendingDraftText:
            pass
        (subject, email, description) = ('', '', '')
        self._persistDraftCore(subject, email, description)

    
    def _persistDraftCore(self, subject, email, description):
        '''把草稿文本与附件写入存储；仅剩预填邮箱等无实际内容时清除草稿。

        参数:
            subject (str): 反馈主题。
            email (str): 用户邮箱。
            description (str): 问题描述。
        返回:
            None。
        '''
        if not subject:
            pass
        if not bool(''.strip()):
            if not description:
                pass
        hasCustomText = bool(''.strip())
        if not email:
            pass
        if not self._savedEmail:
            pass
        emailChanged = ''.strip() != ''.strip()
        if not hasCustomText and emailChanged and self._attachmentPaths:
            self._draftStore.clear()
            return None
        None._draftStore.save(subject, email, description, list(self._attachmentPaths))

    
    def restoreDraft(self):
        '''恢复草稿：恢复附件副本到控制器并返回文本字典给 QML 回填；无草稿返回 None。

        附件恢复时校验副本文件仍存在，已丢失的副本自动跳过。

        参数:
            无。
        返回:
            dict|None: 含 subject/email/description 的字典；无有效草稿时返回 None。
        '''
        record = self._draftStore.load()
        if record is None:
            self._setAttachmentPaths([])
            return None
        restoredPaths = (lambda 