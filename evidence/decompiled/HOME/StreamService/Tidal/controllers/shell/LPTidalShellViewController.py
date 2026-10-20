# Source Generated with Decompyle++
# File: LPTidalShellViewController.pyc (Python 3.9)

'''
TIDAL Shell 控制器。
'''
from typing import Optional
from PyQt6.QtCore import QObject, QPoint, QRectF, Qt, pyqtSlot
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtQml import QQmlContext
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget
import LPGlobalUI
from HOME.LPToggle import LPToggle
from HOME.StreamService.Tidal.controllers.shell.LPTidalShellRouter import LPTidalShellRouteStack, isTidalShellHomeTabsVisible
from HOME.StreamService.Tidal.services.LPTidalQmlContext import applyTidalCursorBridge, applyTidalSharedQmlContext, clearTidalCursorBridge, resolveTidalQmlUrl
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from HOME.StreamService.Tidal.services.LPTidalNetworkDiagnostics import installTidalQmlNetworkDiagnostics
from LPClientFramework.LPConfig import LPUIPath
from LPClientFramework.LPConfig.LPFontConfig import getFontFamily
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPPlayList.LPTidalPlayList import tidalNormalizeQualityValue, tidalQualityLabel, tidalQualityOptions, tidalReadLocalQualityValue, tidalSaveLocalQualityValue, tidalSubscriptionLabel, tidalSubscriptionSupportsMax
from LPClientFramework.LPUtility import logger

class LPTidalAccountMenuDialog(QDialog):
    '''TIDAL 账户菜单弹窗，负责展示账户信息和本地播放偏好 UI。'''
    
    def __init__(self = None, controller = None, anchorWidget = None):
        '''
        初始化账户菜单弹窗。

        :param controller: Shell 控制器。
        :param anchorWidget: 菜单定位参考控件。
        :return: None。
        '''
        super().__init__(controller)
        self._controller = controller
        self._anchor_widget = anchorWidget
        self._quality_box = None
        self._replay_gain_box = None
        self._auto_play_toggle = None
        self._setup_ui()

    
    def _setup_ui(self = None):
        '''
        创建账户菜单 UI。

        :return: None。
        '''
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName('tidalAccountMenuDialog')
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        main_frame = QFrame(self)
        main_frame.setObjectName('mainFrame')
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(12, 12, 12, 18)
        main_layout.setSpacing(18)
        root_layout.addWidget(main_frame)
        main_layout.addWidget(self._create_info_row('Subscription', self._controller._subscription_label(), True, **('highlighted',)))
        main_layout.addWidget(self._create_info_row('Email', self._controller._account_value('email', '')))
        main_layout.addWidget(self._create_info_row('Account Name', self._controller._account_value('userName', 'userId')))
        main_layout.addWidget(self._create_combo_row('Quality', self._quality_options(), self._controller._selected_quality_label(), self._on_quality_changed))
        main_layout.addWidget(self._create_combo_row('Replay Gain', [
            'Disabled',
            'Track Gain',
            'Album Gain'], self._controller._selected_replay_gain, self._on_replay_gain_changed, 104, **('combo_width',)))
        main_layout.addWidget(self._create_auto_play_row())
        logout_button = QPushButton('Log out', main_frame)
        logout_button.setObjectName('logoutButton')
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        logout_button.setFixedHeight(34)
        logout_button.clicked.connect(self._on_logout_clicked)
        main_layout.addWidget(logout_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self.setStyleSheet(self._style_sheet())
        self.resize(350, self.sizeHint().height())
        self._apply_round_mask()

    
    def _create_info_row(self = None, title = None, value = None, highlighted = (False,)):
        '''
        创建只读信息行。

        :param title: 左侧标题。
        :param value: 右侧值。
        :param highlighted: 是否使用订阅高亮样式。
        :return: 信息行控件。
        '''
        row = QFrame(self)
        row.setObjectName('highlightRow' if highlighted else 'plainRow')
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        title_label = QLabel(title, row)
        title_label.setObjectName('rowTitle')
        if not value:
            pass
        value_label = QLabel('--', row)
        value_label.setObjectName('rowValue')
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_label.setMinimumWidth(0)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(title_label, 0)
        layout.addWidget(value_label, 1)
        row.setFixedHeight(46 if highlighted else 44)
        return row

    
    def _create_combo_row(self, title = None, options = None, selectedValue = None, callback = (216,), combo_width = {
        'title': str,
        'options': list,
        'selectedValue': str,
        'combo_width': int,
        'return': QFrame }):
        '''
        创建下拉选择行。

        :param title: 左侧标题。
        :param options: 下拉选项。
        :param selectedValue: 当前选中项。
        :param callback: 选中变化回调。
        :param combo_width: 下拉框宽度。
        :return: 下拉行控件。
        '''
        row = QFrame(self)
        row.setObjectName('plainRow')
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        title_label = QLabel(title, row)
        title_label.setObjectName('rowTitle')
        combo = QComboBox(row)
        combo.setObjectName('accountComboBox')
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setFixedWidth(combo_width)
        combo.setFixedHeight(28)
        for option in options:
            if isinstance(option, tuple):
                combo.addItem(str(option[1]), option[0])
                continue
            combo.addItem(str(option))
        index = combo.findText(selectedValue)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.currentIndexChanged.connect(callback)
        combo.view().window().setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.FramelessWindowHint)
        combo.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout.addWidget(title_label, 1)
        layout.addWidget(combo, 0)
        row.setFixedHeight(50)
        if title == 'Quality':
            self._quality_box = combo
        else:
            self._replay_gain_box = combo
        return row

    
    def _create_auto_play_row(self = None):
        '''
        创建 Auto Play 开关行。

        :return: Auto Play 行控件。
        '''
        row = QFrame(self)
        row.setObjectName('autoPlayRow')
        layout = QVBoxLayout(row)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        top = QFrame(row)
        top.setObjectName('autoPlayInfoFrame')
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        title_label = QLabel('Auto Play', top)
        title_label.setObjectName('rowTitle')
        toggle = LPToggle(top)
        toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle.setFixedSize(42, 24)
        toggle.setChecked(self._controller._auto_play_enabled)
        toggle.clicked.connect(self._on_auto_play_clicked)
        self._auto_play_toggle = toggle
        top_layout.addWidget(title_label, 1)
        top_layout.addWidget(toggle, 0)
        tip_label = QLabel('Similar tracks will play when your queue ends', row)
        tip_label.setObjectName('tipLabel')
        layout.addWidget(top)
        layout.addWidget(tip_label)
        row.setFixedHeight(64)
        return row

    
    def _quality_options(self = None):
        '''
        返回音质下拉选项。

        :return: 音质选项列表。
        '''
        return tidalQualityOptions(self._controller._supports_max_quality())

    
    def _on_quality_changed(self = None, index = None):
        '''
        处理音质选项变化。

        :param index: 当前选中索引。
        :return: None。
        '''
        quality = self._quality_box.itemData(index, Qt.ItemDataRole.UserRole, **('role',)) if self._quality_box is not None else None
        self._controller._set_selected_quality(quality)

    
    def _on_replay_gain_changed(self = None, index = None):
        '''
        处理 Replay Gain 选项变化。

        :param index: 当前选中索引。
        :return: None。
        '''
        replayGain = self._replay_gain_box.itemText(index) if self._replay_gain_box is not None else ''
        self._controller._set_selected_replay_gain(replayGain)

    
    def _on_auto_play_clicked(self = None, checked = None):
        '''
        处理 Auto Play 开关点击。

        :param checked: 是否开启 Auto Play。
        :return: None。
        '''
        self._controller._set_auto_play_enabled(checked)

    
    def _on_logout_clicked(self = None):
        '''
        处理登出按钮点击。

        :return: None。
        '''
        self.close()
        self._controller.onLogoutClicked()

    
    def showDialog(self = None):
        '''
        按顶部账户按钮位置显示弹窗。

        :return: None。
        '''
        anchor_bottom_right = self._anchor_widget.mapToGlobal(self._anchor_widget.rect().bottomRight())
        self.adjustSize()
        self.resize(350, self.sizeHint().height())
        x = anchor_bottom_right.x() - self.width()
        y = anchor_bottom_right.y() + 10
        self.move(x, y)
        self._apply_round_mask()
        self.show()

    
    def _apply_round_mask(self = None):
        '''
        应用圆角遮罩。

        :return: None。
        '''
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 20, 20)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    
    def _style_sheet(self = None):
        '''
        返回账户菜单样式表。

        :return: QSS 样式。
        '''
        font_family = getFontFamily()
        font_family_rule = f'''font-family: "{font_family}";''' if font_family else ''
        dialog_bg = LPGlobalUI.THEME_DIALOG_BACK_COLOR_UI.name()
        font_color = LPGlobalUI.THEME_FONT_COLOR_UI.name()
        disabled_color = LPGlobalUI.THEME_DISABLE_COLOR.name()
        combo_bg = LPGlobalUI.THEME_TABLE_HOVER_BACK_COLOR.name()
        combo_selected = LPGlobalUI.THEME_TABLE_HIGHLIGHT_BACK_COLOR.name()
        high_bg = LPGlobalUI.QSS_THEME_BUTTON_BACK_PRESS_COLOR
        high_font = LPGlobalUI.THEME_BUTTON_BACK_COLOR_UI.name()
        arrow_path = LPGlobalUI.imagePath('arrow_down.png')
        return f'''\n            QDialog#tidalAccountMenuDialog {{\n                background-color: transparent;\n            }}\n            QFrame#mainFrame {{\n                border: none;\n                border-radius: 20px;\n                background-color: {dialog_bg};\n                min-width: 350px;\n                max-width: 350px;\n            }}\n            QFrame#highlightRow {{\n                border: none;\n                border-radius: 10px;\n                background-color: {high_bg};\n            }}\n            QFrame#plainRow, QFrame#autoPlayRow, QFrame#autoPlayInfoFrame {{\n                border: none;\n                background-color: transparent;\n            }}\n            QLabel#rowTitle {{\n                color: {font_color};\n                font-weight: 600;\n                background-color: transparent;\n            }}\n            QLabel#rowValue {{\n                color: {font_color};\n                font-weight: 600;\n                background-color: transparent;\n            }}\n            QFrame#highlightRow QLabel {{\n                color: {high_font};\n            }}\n            QLabel#tipLabel {{\n                color: {disabled_color};\n                font-weight: 600;\n                background-color: transparent;\n            }}\n            QComboBox#accountComboBox {{\n                background-color: {combo_bg};\n                color: {font_color};\n                border: none;\n                border-radius: 5px;\n                padding-left: 10px;\n                padding-right: 24px;\n                font-weight: 600;\n                combobox-popup: 0;\n            }}\n            QComboBox#accountComboBox::drop-down {{\n                border: 0px;\n                width: 22px;\n            }}\n            QComboBox#accountComboBox::down-arrow {{\n                image: url("{arrow_path}");\n                width: 14px;\n                height: 14px;\n                padding-right: 8px;\n            }}\n            QComboBox#accountComboBox QAbstractItemView {{\n                background-color: {combo_bg};\n                color: {font_color};\n                border: none;\n                selection-background-color: {combo_selected};\n                padding-top: 4px;\n                padding-bottom: 4px;\n            }}\n            QPushButton#logoutButton {{\n                color: red;\n                background-color: transparent;\n                border: none;\n                {font_family_rule}\n                font-size: 13px;\n                font-weight: 600;\n                padding: 0px 18px;\n            }}\n            QPushButton#logoutButton:hover, QPushButton#logoutButton:pressed, QPushButton#logoutButton:focus {{\n                color: red;\n                background-color: transparent;\n                border: none;\n                outline: none;\n            }}\n        '''

    __classcell__ = None


class LPTidalShellViewController(QWidget):
    '''TIDAL Shell 容器，负责持久顶部导航和内部内容页栈。'''
    
    def __init__(self = None, parent = None):
        '''
        初始化 TIDAL Shell。

        :param parent: 父级 QWidget。
        :return: None。
        '''
        super().__init__(parent)
        self._store = LPTidalStore.instance()
        self._login_manager = LPTidalLoginManager.instance(self)
        self._login_manager.logoutSucceeded.connect(self._on_logout_succeeded)
        self._route_stack = LPTidalShellRouteStack()
        self._current_tab = 0
        self._selected_quality = self._current_quality_value()
        self._selected_replay_gain = 'Disabled'
        self._auto_play_enabled = False
        self._home_page = None
        self.quickWidget = None
        self.deleteOnPrune = False
        self.reuseOnPush = True
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._content_stack = QStackedWidget(self)
        self.destroyed.connect(self._onDestroyed)
        self._store.accountStateChanged.connect(self._on_account_state_changed)
        self._setup_qml_navigation()
        self._main_layout.addWidget(self._content_stack, 1)
        self._bootstrapHomeRoot()

    
    def _onDestroyed(self = None, destroyedObject = None):
        '''
        QObject 销毁回调，通知当前内容页隐藏。

        :param destroyedObject: Qt 销毁信号透传对象。
        :return: None。
        '''
        _ = destroyedObject
        clearTidalCursorBridge(self)
        current = self._content_stack.currentWidget()
        if current is not None:
            method = getattr(current, 'viewWillDisappear', None)
            if method and callable(method):
                method()

    
    def viewWillAppear(self = None):
        '''
        Shell 显示时同步账号状态并转发给当前内容页。

        :return: None。
        '''
        if not self._login_manager.ensureTidalLoggedInOrShowLogin():
            return None
        if None.quickWidget is not None:
            applyTidalCursorBridge(self.quickWidget.rootContext(), self, self.quickWidget)
        current = self._content_stack.currentWidget()
        if current is not None:
            method = getattr(current, 'viewWillAppear', None)
            if method and callable(method):
                method()
        self._sync_navigation_state()
        self._sync_quality_selection_to_qml()

    
    def viewWillDisappear(self = None):
        '''
        Shell 隐藏时转发给当前内容页。

        :return: None。
        '''
        clearTidalCursorBridge(self)
        current = self._content_stack.currentWidget()
        if current is not None:
            method = getattr(current, 'viewWillDisappear', None)
            if method and callable(method):
                method()

    
    def openHomeTab(self = None, tabIndex = None):
        '''
        打开 Shell 根页的 Home 或 My Collection tab。

        :param tabIndex: 0 表示 Home，1 表示 My Collection。
        :return: None。
        '''
        if self._closeCurrentContentTransientMenus():
            return None
        if not tabIndex:
            pass
        normalized_tab = 1 if None(0) == 1 else 0
        tab_changed = normalized_tab != self._current_tab
        self._current_tab = normalized_tab
        home_page = self._ensure_home_page()
        removed = self._route_stack.replaceRoot(home_page) if self._route_stack.current() is not None else self._route_stack.resetRoot(home_page)
        self._remove_content_pages(removed)
        self._activate_content_page(home_page, tab_changed, **('refresh',))
        self._set_home_tab(normalized_tab)
        self._sync_navigation_state()

    openHomeTab = None(openHomeTab)
    
    def openGlobalSearch(self = None, text = None):
        '''
        通过全局导航栈打开 TIDAL 搜索页，支持应用全局返回按钮返回。

        :param text: 初始搜索文本。
        :return: None。
        '''
        if self._closeCurrentContentTransientMenus():
            return None
        LPTidalSearchViewController = LPTidalSearchViewController
        import HOME.StreamService.Tidal.controllers.pages.LPTidalSearchViewController
        page = LPTidalSearchViewController(None, False, **('shellEmbedded',))
        if not text:
            pass
        query = str('').strip()
        if query:
            page.setSearchText(query)
            page.triggerSearch()
        LPGlobalUI.navigationManager.push(page, 'tidal_search')

    openGlobalSearch = None(openGlobalSearch)
    
    def onAccountClicked(self = None):
        '''
        处理顶部账户按钮点击，已登录菜单由 QML 内联弹窗负责。

        :return: None。
        '''
        if self._closeCurrentContentTransientMenus():
            return None
        if not None._store.accountState.get('isLoggedIn', False):
            self.onLoginClicked()
            return None
        home_page = None._home_page
        if home_page is None:
            return None
        method = None(home_page, 'openEmbeddedAccountMenu', None)
        if method and callable(method):
            method()

    onAccountClicked = None(onAccountClicked)
    
    def consumeTransientMenuClick(self = None):
        '''
        供 Shell QML 顶栏调用：若内容页有临时菜单则关闭并消费本次点击。

        :return: 已关闭临时菜单并需要吞掉本次点击时返回 True。
        '''
        return self._closeCurrentContentTransientMenus()

    consumeTransientMenuClick = None(consumeTransientMenuClick)
    
    def onAccountMenuRequestedAt(self, anchorX = None, anchorY = None, anchorWidth = pyqtSlot(float, float, float, float), anchorHeight = {
        'anchorX': float,
        'anchorY': float,
        'anchorWidth': float,
        'anchorHeight': float,
        'return': None }):
        '''
        处理顶部账户菜单定位请求，并将锚点转发给 Home 页 QML 菜单。

        :param anchorX: 账户按钮相对 Shell 顶栏的 X。
        :param anchorY: 账户按钮相对 Shell 顶栏的 Y。
        :param anchorWidth: 账户按钮宽度。
        :param anchorHeight: 账户按钮高度。
        :return: None。
        '''
        home_page = self._home_page
        if home_page is None and self.quickWidget is None or home_page.quickWidget is None:
            return None
        shell_top_left = None.quickWidget.mapToGlobal(QPoint(int(anchorX), int(anchorY)))
        home_top_left = home_page.quickWidget.mapFromGlobal(shell_top_left)
        update_anchor = getattr(home_page, 'updateEmbeddedAccountMenuAnchor', None)
        if update_anchor and callable(update_anchor):
            update_anchor(float(home_top_left.x()), float(home_top_left.y()), float(anchorWidth), float(anchorHeight))

    onAccountMenuRequestedAt = None(onAccountMenuRequestedAt)
    
    def onLoginClicked(self = None):
        '''
        打开 TIDAL 登录页。

        :return: None。
        '''
        LPTidalLoginViewController = LPTidalLoginViewController
        import HOME.StreamService.Tidal.controllers.pages.LPTidalLoginViewController
        page = LPTidalLoginViewController(True, **('enterHomeOnSuccess',))
        LPGlobalUI.navigationManager.push(page, 'tidal_login')

    onLoginClicked = None(onLoginClicked)
    
    def onLogoutClicked(self = None):
        '''
        登出当前 TIDAL 账号。
        由 logoutSucceeded 信号统一触发页面导航恢复。

        :return: None。
        '''
        self._login_manager.logout()

    onLogoutClicked = None(onLogoutClicked)
    
    def _on_logout_succeeded(self = None):
        '''
        登出成功后清除导航页并跳转到登录页。

        登录页 push 到栈顶成为当前页后，销毁旧 Shell 实例以彻底释放
        Shell 与 Home 页两个 QQuickWidget 持有的 QML pixmap 内存。

        :return: None。
        '''
        self._login_manager.clearTidalNavigationPages()
        LPTidalLoginViewController = LPTidalLoginViewController
        import HOME.StreamService.Tidal.controllers.pages.LPTidalLoginViewController
        page = LPTidalLoginViewController(True, **('enterHomeOnSuccess',))
        LPGlobalUI.navigationManager.push(page, 'tidal_login')
        stack = getattr(LPGlobalUI, 'rootStackedWidget', None)
        if stack is not None and stack.indexOf(self) >= 0:
            stack.removeWidget(self)
        self.deleteLater()

    _on_logout_succeeded = None(_on_logout_succeeded)
    
    def debugLog(self = None, message = None):
        '''
        输出 Shell QML 调试日志。

        :param message: 调试信息。
        :return: None。
        '''
        logger.debug(f'''[TIDAL][Shell][QML] {message}''')

    debugLog = None(debugLog)
    
    def _closeCurrentContentTransientMenus(self = None):
        '''
        关闭当前内容页中打开的临时菜单。

        :return: 当前内容页关闭了临时菜单时返回 True。
        '''
        current = self._content_stack.currentWidget()
        if current is None:
            return False
        method = None(current, 'closeTransientMenus', None)
        if not method or callable(method):
            return False
        :
            current = self._content_stack.currentWidget()
            if current is None:
                return False
            method = None(current, 'closeTransientMenus', None)
            if not method or callable(method):
                return False
            
            return bool(method())
        return bool(method())
    # WARNING: Decompyle incomplete

    
    def pushContentPage(self = None, widget = None, itemId = None):
        '''
        推入 Shell 内部内容页。

        :param widget: 目标内容页。
        :param itemId: 内容页标识。
        :return: None。
        '''
        if widget is None:
            return None
        widget.stackedItemId = None
        self._route_stack.push(widget)
        self._activate_content_page(widget)
        self._sync_navigation_state()

    
    def popContentPage(self = None, widget = None):
        '''
        弹出 Shell 内部当前内容页。

        :param widget: 当前内容页。
        :return: None。
        '''
        _ = widget
        removed = self._route_stack.pop()
        if removed is None:
            return None
        None._remove_content_page(removed)
        previous = self._route_stack.current()
        if previous is not None:
            self._activate_content_page(previous)
        self._sync_navigation_state()

    
    def _setup_qml_navigation(self = None):
        '''
        创建顶部导航 QQuickWidget。

        :return: None。
        '''
        if self.quickWidget is not None:
            return None
        quick = None(self)
        quick.setFixedHeight(58)
        quick.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        quick.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        quick.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        quick.setMouseTracking(True)
        quick.setClearColor(LPGlobalUI.THEME_BACKGROUND_COLOR_UI)
        quick.setStyleSheet(f'''background-color: {LPGlobalUI.THEME_BACKGROUND_COLOR_UI.name()};''')
        ctx = quick.rootContext()
        applyTidalSharedQmlContext(ctx)
        applyTidalCursorBridge(ctx, self, quick)
        ctx.setContextProperty('tidalShellActions', self)
        ctx.setContextProperty('tidalStore', self._store)
        ctx.setContextProperty('sharedStore', self._store)
        installTidalQmlNetworkDiagnostics(quick, 'shell')
        quick.setSource(resolveTidalQmlUrl(LPUIPath.TidalShellQML, 'pages/TidalShell.qml'))
        if quick.status() != QQuickWidget.Status.Ready:
            logger.error(f'''[TIDAL] Shell QML load failed, status={quick.status()}''')
            for err in quick.errors():
                logger.error(f'''[TIDAL] {err.toString()}''')
        self.quickWidget = quick
        self._main_layout.addWidget(quick, 0)
        self._sync_navigation_state()
        self._sync_quality_selection_to_qml()

    
    def _on_account_state_changed(self = None):
        '''
        处理账号状态变化，刷新 Shell 顶栏音质回显。

        :param: 无。
        :return: None。
        '''
        self._selected_quality = self._current_quality_value()
        self._sync_quality_selection_to_qml()

    
    def _sync_quality_selection_to_qml(self = None):
        '''
        将当前账号本地音质设置同步到 Shell 顶栏。

        :param: 无。
        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is None:
            return None
        top_nav_bar = None.findChild(QObject, 'topNavBar')
        if top_nav_bar is not None:
            top_nav_bar.setProperty('selectedQuality', self._selected_quality_menu_label())

    
    def _ensure_home_page(self = None):
        '''
        返回 Shell 根页，没有时创建。

        :return: Home 内容页。
        '''
        if self._home_page is None:
            LPTidalHomeViewController = LPTidalHomeViewController
            import HOME.StreamService.Tidal.controllers.pages.LPTidalHomeViewController
            self._home_page = LPTidalHomeViewController(self, True, **('shellEmbedded',))
            self._home_page.stackedItemId = 'tidal_home'
            self._content_stack.addWidget(self._home_page)
        return self._home_page

    
    def _bootstrapHomeRoot(self = None):
        '''
        构造期创建 Home 根页并设为当前 content，但不触发 viewWillAppear。

        构造期 Shell 尚未完成 push，此时回调 viewWillAppear 会引发账号同步和首页加载。
        首次激活交由 pushWidget 触发的 Shell.viewWillAppear 转发，避免登录后重复加载首页。

        :return: None。
        '''
        self._current_tab = 0
        home_page = self._ensure_home_page()
        self._route_stack.resetRoot(home_page)
        if self._content_stack.currentWidget() is not home_page:
            self._content_stack.setCurrentWidget(home_page)

    
    def _activate_content_page(self = None, widget = None, refresh = None):
        '''
        激活指定内容页。

        :param widget: 目标内容页。
        :param refresh: 目标页已是当前页时，True 触发 viewWillAppear 刷新，False 直接返回。
        :return: None。
        '''
        current = self._content_stack.currentWidget()
        if current is widget:
            if refresh:
                method = getattr(widget, 'viewWillAppear', None)
                if method and callable(method):
                    method()
            return None
        if None is not None:
            method = getattr(current, 'viewWillDisappear', None)
            if method and callable(method):
                method()
        if self._content_stack.indexOf(widget) < 0:
            self._content_stack.addWidget(widget)
        self._content_stack.setCurrentWidget(widget)
        method = getattr(widget, 'viewWillAppear', None)
        if method and callable(method):
            method()

    
    def _remove_content_pages(self = None, widgets = None):
        '''
        移除一组内容页。

        :param widgets: 待移除内容页列表。
        :return: None。
        '''
        for widget in widgets:
            self._remove_content_page(widget)

    
    def _remove_content_page(self = None, widget = None):
        '''
        从内容栈移除单个页面。

        :param widget: 待移除页面。
        :return: None。
        '''
        if widget is None or widget is self._home_page:
            return None
        if None._content_stack.currentWidget() is widget:
            method = getattr(widget, 'viewWillDisappear', None)
            if method and callable(method):
                method()
        if self._content_stack.indexOf(widget) >= 0:
            self._content_stack.removeWidget(widget)
        widget.deleteLater()

    
    def _set_home_tab(self = None, tabIndex = None):
        '''
        同步 Home 内容页内部 tab。

        :param tabIndex: 0 表示 Home，1 表示 My Collection。
        :return: None。
        '''
        page = self._home_page
        if page is None:
            return None
        method = None(page, 'setShellCurrentTab', None)
        if method and callable(method):
            method(tabIndex)

    
    def _sync_navigation_state(self = None):
        '''
        同步顶部导航 QML 的选中态和页签可见性。

        :return: None。
        '''
        root = self.quickWidget.rootObject() if self.quickWidget is not None else None
        if root is None:
            return None
        None.setProperty('currentTab', self._current_tab)
        root.setProperty('showHomeTabs', isTidalShellHomeTabsVisible(self._route_stack.entries()))

    
    def _show_account_menu(self = None):
        '''
        显示 TIDAL 账户菜单。

        :return: None。
        '''
        dialog = LPTidalAccountMenuDialog(self, self.quickWidget)
        dialog.showDialog()

    
    def _set_selected_quality(self = None, quality = None):
        '''
        更新并持久化音质菜单选中态。

        :param quality: 音质数值。
        :return: None。
        '''
        normalized = tidalNormalizeQualityValue(quality, self._supports_max_quality())
        self._selected_quality = normalized
        self._save_quality_value(normalized)

    
    def _selected_quality_label(self = None):
        '''
        返回当前音质展示文案。

        :param: 无。
        :return: 音质展示文案。
        '''
        self._selected_quality = self._current_quality_value()
        return tidalQualityLabel(self._selected_quality)

    
    def _selected_quality_menu_label(self = None):
        '''
        返回当前音质在 QML 菜单中的长文案。

        :param: 无。
        :return: QML 菜单文案。
        '''
        self._selected_quali