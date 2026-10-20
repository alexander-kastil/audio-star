# Source Generated with Decompyle++
# File: LPTidalPlaylistManager.pyc (Python 3.9)

'''
TIDAL 歌单写操作管理器。
'''
from typing import Any, Dict, List, Optional
import LPGlobalUI
from PyQt6.QtCore import QObject, QCoreApplication, pyqtProperty, pyqtSignal, pyqtSlot
from HOME.StreamService.Tidal.data.LPTidalDataProvider import LPTidalDataProvider
from HOME.StreamService.Tidal.models.LPTidalListModel import LPTidalListModel
from HOME.StreamService.Tidal.services.LPTidalCollectionSortPreference import LPTidalCollectionSortPreference
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager import LPTidalLoginManager
from LPClientFramework.LPUtility import logger

class LPTidalAddToPlaylistState(QObject):
    '''Add-to-playlist 对话框状态，供 QML 绑定展示与提交。'''
    visibleChanged = pyqtSignal()
    trackIdChanged = pyqtSignal()
    trackTitleChanged = pyqtSignal()
    activeTabChanged = pyqtSignal()
    filterTextChanged = pyqtSignal()
    isSubmittingChanged = pyqtSignal()
    isLoadingPlaylistsChanged = pyqtSignal()
    selectedPlaylistIdChanged = pyqtSignal()
    writablePlaylistsChanged = pyqtSignal()
    createTitleChanged = pyqtSignal()
    createDescriptionChanged = pyqtSignal()
    errorMessageChanged = pyqtSignal()
    
    def __init__(self = None, parent = None):
        '''
        初始化对话框状态。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        self._visible = False
        self._track_id = ''
        self._track_title = ''
        self._active_tab = 'add'
        self._filter_text = ''
        self._is_submitting = False
        self._is_loading_playlists = False
        self._selected_playlist_id = ''
        self._create_title = ''
        self._create_description = ''
        self._error_message = ''
        self._writable_playlists = LPTidalListModel(self)

    
    def visible(self = None):
        '''
        返回对话框是否可见。

        :return: 可见返回 True。
        '''
        return self._visible

    visible = None(visible)
    
    def trackId(self = None):
        '''
        返回待添加曲目 ID。

        :return: 曲目 ID。
        '''
        return self._track_id

    trackId = None(trackId)
    
    def trackTitle(self = None):
        '''
        返回待添加曲目标题。

        :return: 曲目标题。
        '''
        return self._track_title

    trackTitle = None(trackTitle)
    
    def activeTab(self = None):
        '''
        返回当前 Tab（add/create）。

        :return: Tab 标识。
        '''
        return self._active_tab

    activeTab = None(activeTab)
    
    def filterText(self = None):
        '''
        返回歌单筛选文本。

        :return: 筛选文本。
        '''
        return self._filter_text

    filterText = None(filterText)
    
    def isSubmitting(self = None):
        '''
        返回是否正在提交。

        :return: 提交中返回 True。
        '''
        return self._is_submitting

    isSubmitting = None(isSubmitting)
    
    def isLoadingPlaylists(self = None):
        '''
        返回是否正在拉取可写歌单列表。

        :return: 加载中返回 True。
        '''
        return self._is_loading_playlists

    isLoadingPlaylists = None(isLoadingPlaylists)
    
    def selectedPlaylistId(self = None):
        '''
        返回当前选中的歌单 ID。

        :return: 歌单 UUID。
        '''
        return self._selected_playlist_id

    selectedPlaylistId = None(selectedPlaylistId)
    
    def createTitle(self = None):
        '''
        返回新建歌单标题。

        :return: 歌单标题。
        '''
        return self._create_title

    createTitle = None(createTitle)
    
    def createDescription(self = None):
        '''
        返回新建歌单描述。

        :return: 歌单描述。
        '''
        return self._create_description

    createDescription = None(createDescription)
    
    def errorMessage(self = None):
        '''
        返回对话框错误信息。

        :return: 错误文案。
        '''
        return self._error_message

    errorMessage = None(errorMessage)
    
    def writablePlaylists(self = None):
        '''
        返回可写歌单列表模型。

        :return: 歌单列表模型。
        '''
        return self._writable_playlists

    writablePlaylists = None(writablePlaylists)
    
    def open(self = None, trackId = None, trackTitle = None, playlists = ('', None)):
        '''
        打开对话框并填充待添加曲目与可写歌单列表。

        :param trackId: 曲目 ID。
        :param trackTitle: 曲目标题。
        :param playlists: 可写歌单列表。
        :return: None。
        '''
        if not trackId:
            pass
        self._track_id = str('').strip()
        if not trackTitle:
            pass
        self._track_title = str('').strip()
        self._active_tab = 'add'
        self._filter_text = ''
        self._selected_playlist_id = ''
        self._create_title = ''
        self._create_description = ''
        self._error_message = ''
        self._is_submitting = False
        self._is_loading_playlists = False
        if not playlists:
            pass
        self._writable_playlists.setItems([])
        self._visible = True
        self.visibleChanged.emit()
        self.trackIdChanged.emit()
        self.trackTitleChanged.emit()
        self.activeTabChanged.emit()
        self.filterTextChanged.emit()
        self.selectedPlaylistIdChanged.emit()
        self.createTitleChanged.emit()
        self.createDescriptionChanged.emit()
        self.errorMessageChanged.emit()
        self.isSubmittingChanged.emit()
        self.isLoadingPlaylistsChanged.emit()
        self.writablePlaylistsChanged.emit()

    
    def close(self = None):
        '''
        关闭对话框并重置提交状态。

        :return: None。
        '''
        self._visible = False
        self._is_submitting = False
        self._is_loading_playlists = False
        self._error_message = ''
        self.visibleChanged.emit()
        self.isSubmittingChanged.emit()
        self.isLoadingPlaylistsChanged.emit()
        self.errorMessageChanged.emit()

    
    def setSubmitting(self = None, submitting = None):
        '''
        更新提交状态。

        :param submitting: 是否提交中。
        :return: None。
        '''
        normalized = bool(submitting)
        if self._is_submitting == normalized:
            return None
        self._is_submitting = None
        self.isSubmittingChanged.emit()

    
    def setLoadingPlaylists(self = None, loading = None):
        '''
        更新可写歌单列表加载状态。

        :param loading: 是否加载中。
        :return: None。
        '''
        normalized = bool(loading)
        if self._is_loading_playlists == normalized:
            return None
        self._is_loading_playlists = None
        self.isLoadingPlaylistsChanged.emit()

    
    def setWritablePlaylists(self = None, playlists = None):
        '''
        更新对话框中的可写歌单列表。

        :param playlists: 歌单条目列表。
        :return: None。
        '''
        if not playlists:
            pass
        self._writable_playlists.setItems([])
        self.writablePlaylistsChanged.emit()

    
    def setErrorMessage(self = None, message = None):
        '''
        更新错误信息。

        :param message: 错误文案。
        :return: None。
        '''
        if not message:
            pass
        normalized = str('')
        if self._error_message == normalized:
            return None
        self._error_message = None
        self.errorMessageChanged.emit()

    
    def setActiveTab(self = None, tab = None):
        '''
        切换对话框 Tab。

        :param tab: Tab 标识。
        :return: None。
        '''
        if not tab:
            pass
        if not str('').strip().lower():
            pass
        normalized = 'add'
        if self._active_tab == normalized:
            return None
        self._active_tab = None
        self.activeTabChanged.emit()

    setActiveTab = None(setActiveTab)
    
    def setFilterText(self = None, text = None):
        '''
        设置歌单筛选文本。

        :param text: 筛选文本。
        :return: None。
        '''
        if not text:
            pass
        normalized = str('')
        if self._filter_text == normalized:
            return None
        self._filter_text = None
        self.filterTextChanged.emit()

    setFilterText = None(setFilterText)
    
    def setSelectedPlaylistId(self = None, playlistId = None):
        '''
        设置选中的歌单 ID。

        :param playlistId: 歌单 UUID。
        :return: None。
        '''
        if not playlistId:
            pass
        normalized = str('').strip()
        if self._selected_playlist_id == normalized:
            return None
        self._selected_playlist_id = None
        self.selectedPlaylistIdChanged.emit()

    setSelectedPlaylistId = None(setSelectedPlaylistId)
    
    def setCreateTitle(self = None, title = None):
        '''
        设置新建歌单标题。

        :param title: 歌单标题。
        :return: None。
        '''
        if not title:
            pass
        normalized = str('')
        if self._create_title == normalized:
            return None
        self._create_title = None
        self.createTitleChanged.emit()

    setCreateTitle = None(setCreateTitle)
    
    def setCreateDescription(self = None, description = None):
        '''
        设置新建歌单描述。

        :param description: 歌单描述。
        :return: None。
        '''
        if not description:
            pass
        normalized = str('')
        if self._create_description == normalized:
            return None
        self._create_description = None
        self.createDescriptionChanged.emit()

    setCreateDescription = None(setCreateDescription)
    __classcell__ = None


class LPTidalPlaylistManager(QObject):
    '''封装 TIDAL 歌单创建、添加、编辑、删除与刷新逻辑。'''
    playlistMutationFinished = pyqtSignal(bool, str, str)
    _instance: Optional['LPTidalPlaylistManager'] = None
    
    def __init__(self = None, parent = None):
        '''
        初始化歌单管理器。

        :param parent: 父级 QObject。
        :return: None。
        '''
        super().__init__(parent)
        if parent is not None:
            self._store = parent
        else:
            self._store = LPTidalStore.instance()
        self._provider = LPTidalDataProvider()
        self._add_to_playlist_state = LPTidalAddToPlaylistState(self)

    
    def instance(cls = None):
        '''
        返回歌单管理器单例。

        :return: 管理器单例。
        '''
        store = LPTidalStore.instance()
        manager = getattr(store, 'playlistManager', None)
        if manager is not None:
            return manager
        if None._instance is None:
            cls._instance = cls(store)
        return cls._instance

    instance = None(instance)
    
    def addToPlaylistState(self = None):
        '''
        返回 Add-to-playlist 对话框状态。

        :return: 对话框状态对象。
        '''
        return self._add_to_playlist_state

    addToPlaylistState = None(addToPlaylistState)
    
    def guardLoggedIn(self = None):
        '''
        校验 TIDAL 是否已登录。

        :return: 已登录返回 True。
        '''
        device = getattr(LPGlobalUI, 'currentDevice', None)
    # WARNING: Decompyle incomplete

    
    def writablePlaylistsFromCache(self = None):
        '''
        从收藏页缓存返回当前用户可写歌单列表。

        :return: 歌单条目列表。
        '''
        model = self._store.collectionState.userPlaylists
        items = (lambda .0 = None: [ dict(model.itemAt(index)) for index in .0 ])(range(model.count()))
        return self._provider.filterUserCreatedPlaylists(items)

    
    def _refreshWritablePlaylistsForDialog(self = None, state = None):
        '''
        实时分页拉取账号内用户自建歌单全量（跳过 API 缓存），刷新对话框列表。

        收藏页 userPlaylists 缓存不再由此副作用维护，由 Collection 页独立 loadCollection 刷新。

        :param state: Add-to-playlist 对话框状态。
        :return: None。
        '''
        account = self._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        if not account.get('countryCode', ''):
            pass
        country_code = str('').strip()
        if not user_id:
            state.setWritablePlaylists([])
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Failed to load playlists.'))
            return None
        sort_preferences = None.sortPreferencesForUser(user_id)
        result = self._provider.loadMyPlaylists(user_id, country_code, True, sort_preferences, **('skipCache', 'sortPreferences'))
        if not isinstance(result, dict) or bool(result.get('success')):
            state.setWritablePlaylists([])
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Failed to load playlists.'))
            return None
        payload = None.get('data', { })
        data = payload if isinstance(payload, dict) else { }
        user_created = data.get('userCreatedPlaylists', [])
        state.setWritablePlaylists(user_created if isinstance(user_created, list) else [])

    
    def openAddToPlaylist(self = None, trackId = None, trackTitle = pyqtSlot(str, str)):
        '''
        打开 Add-to-playlist 对话框，并实时拉取用户自建歌单列表。

        :param trackId: 曲目 ID。
        :param trackTitle: 曲目标题。
        :return: None。
        '''
        if not self.guardLoggedIn():
            return None
        if not trackId:
            pass
        normalized_track_id = None('').strip()
        if not normalized_track_id:
            return None
        state = None._add_to_playlist_state
        state.open(normalized_track_id, trackTitle, [])
        state.setErrorMessage('')
        state.setLoadingPlaylists(True)
        self._refreshWritablePlaylistsForDialog(state)
        state.setLoadingPlaylists(False)

    openAddToPlaylist = None(openAddToPlaylist)
    
    def openGlobalAddToPlaylist(self = None, trackId = None, trackTitle = pyqtSlot(str, str)):
        '''
        通过 app 级 QDialog 宿主打开 Add-to-playlist 对话框。

        :param trackId: 曲目 ID。
        :param trackTitle: 曲目标题。
        :return: None。
        '''
        if not trackId:
            pass
        normalized_track_id = str('').strip()
        if not normalized_track_id:
            return None
        LPTidalAddToPlaylistDialogHost = LPTidalAddToPlaylistDialogHost
        import HOME.StreamService.Tidal.widgets.LPTidalAddToPlaylistDialogHost
        host = LPTidalAddToPlaylistDialogHost.instance()
        if not trackTitle:
            pass
        host.showForTrack(normalized_track_id, str(''))

    openGlobalAddToPlaylist = None(openGlobalAddToPlaylist)
    
    def closeAddToPlaylist(self = None):
        '''
        关闭 Add-to-playlist 对话框。

        :return: None。
        '''
        self._add_to_playlist_state.close()

    closeAddToPlaylist = None(closeAddToPlaylist)
    
    def submitAddToExistingPlaylist(self = None):
        '''
        将当前曲目添加到选中的已有歌单。

        :return: None。
        '''
        if not self.guardLoggedIn():
            return None
        state = None._add_to_playlist_state
        if not state.selectedPlaylistId:
            pass
        playlist_id = str('').strip()
        if not state.trackId:
            pass
        track_id = str('').strip()
        if not playlist_id:
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Please select a playlist.'))
            return None
        if not None:
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'This track is not available.'))
            return None
        None.setErrorMessage('')
        state.setSubmitting(True)
        result = self._provider.addPlaylistItems(playlist_id, track_id)
        state.setSubmitting(False)
        if not isinstance(result, dict) or bool(result.get('success')):
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Failed to add track to playlist.'))
            self.playlistMutationFinished.emit(False, 'add', playlist_id)
            return None
        None.refreshCollectionAfterMutation()
        state.close()
        self._showToast(QCoreApplication.translate('Tidal', 'Added to Playlist'))
        self.playlistMutationFinished.emit(True, 'add', playlist_id)

    submitAddToExistingPlaylist = None(submitAddToExistingPlaylist)
    
    def submitCreatePlaylistAndAdd(self = None):
        '''
        创建新歌单并将当前曲目加入其中。

        :return: None。
        '''
        if not self.guardLoggedIn():
            return None
        account = None._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        if not account.get('countryCode', ''):
            pass
        country_code = str('').strip()
        state = self._add_to_playlist_state
        if not state.createTitle:
            pass
        title = str('').strip()
        if not state.trackId:
            pass
        track_id = str('').strip()
        if not title:
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Please enter a playlist name.'))
            return None
        if not None:
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'This track is not available.'))
            return None
        None.setErrorMessage('')
        state.setSubmitting(True)
        create_result = self._provider.createUserPlaylist(user_id, title, state.createDescription, country_code, **('description', 'countryCode'))
        if not isinstance(create_result, dict) or bool(create_result.get('success')):
            state.setSubmitting(False)
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Failed to create playlist.'))
            self.playlistMutationFinished.emit(False, 'create', '')
            return None
        playlist_uuid = None._provider.extractPlaylistUuid(create_result.get('data'))
        if not playlist_uuid:
            state.setSubmitting(False)
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Failed to create playlist.'))
            self.playlistMutationFinished.emit(False, 'create', '')
            return None
        add_result = None._provider.addPlaylistItems(playlist_uuid, track_id, country_code, **('countryCode',))
        state.setSubmitting(False)
        if not isinstance(add_result, dict) or bool(add_result.get('success')):
            self.refreshCollectionAfterMutation()
            state.setErrorMessage(QCoreApplication.translate('Tidal', 'Playlist created, but adding track failed.'))
            self.playlistMutationFinished.emit(False, 'create_add', playlist_uuid)
            return None
        None.refreshCollectionAfterMutation()
        state.close()
        self._showToast(QCoreApplication.translate('Tidal', 'Playlist Created'))
        self.playlistMutationFinished.emit(True, 'create', playlist_uuid)

    submitCreatePlaylistAndAdd = None(submitCreatePlaylistAndAdd)
    
    def createEmptyPlaylist(self = None, title = None, description = pyqtSlot(str, str)):
        '''
        创建空歌单。

        :param title: 歌单标题。
        :param description: 歌单描述。
        :return: None。
        '''
        if not self.guardLoggedIn():
            return None
        account = None._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        if not account.get('countryCode', ''):
            pass
        country_code = str('').strip()
        if not title:
            pass
        normalized_title = str('').strip()
        if not normalized_title:
            self._showToast(QCoreApplication.translate('Tidal', 'Please Enter a Playlist Name'))
            return None
        result = None._provider.createUserPlaylist(user_id, normalized_title, description, country_code, **('description', 'countryCode'))
        if not isinstance(result, dict) or bool(result.get('success')):
            self._showToast(QCoreApplication.translate('Tidal', 'Create Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'create_empty', '')
            return None
        playlist_uuid = None._provider.extractPlaylistUuid(result.get('data'))
        self.refreshCollectionAfterMutation()
        self._showToast(QCoreApplication.translate('Tidal', 'Playlist Created'))
        self.playlistMutationFinished.emit(True, 'create_empty', playlist_uuid)

    createEmptyPlaylist = None(createEmptyPlaylist)
    
    def updatePlaylistMetadata(self = None, playlistUuid = None, title = pyqtSlot(str, str, str), description = ('',)):
        '''
        更新歌单标题和描述。

        :param playlistUuid: 歌单 UUID。
        :param title: 歌单标题。
        :param description: 歌单描述。
        :return: 成功返回 True。
        '''
        if not self.guardLoggedIn():
            return False
        if not playlistUuid:
            pass
        playlist_id = None('').strip()
        if not title:
            pass
        normalized_title = str('').strip()
        if not playlist_id or normalized_title:
            self._showToast(QCoreApplication.translate('Tidal', 'Please Enter a Playlist Name'))
            return False
        result = None._provider.updatePlaylist(playlist_id, normalized_title, description, **('description',))
        if not isinstance(result, dict) or bool(result.get('success')):
            self._showToast(QCoreApplication.translate('Tidal', 'Update Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'update', playlist_id)
            return False
        None.refreshCollectionAfterMutation()
        self._showToast(QCoreApplication.translate('Tidal', 'Playlist Updated'))
        self.playlistMutationFinished.emit(True, 'update', playlist_id)
        return True

    updatePlaylistMetadata = None(updatePlaylistMetadata)
    
    def deleteUserPlaylist(self = None, playlistUuid = None):
        '''
        删除用户自建歌单。

        :param playlistUuid: 歌单 UUID。
        :return: 成功返回 True。
        '''
        if not self.guardLoggedIn():
            return False
        if not playlistUuid:
            pass
        playlist_id = None('').strip()
        if not playlist_id:
            return False
        result = None._provider.deletePlaylist(playlist_id)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._showToast(QCoreApplication.translate('Tidal', 'Remove Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'delete', playlist_id)
            return False
        None._showToast(QCoreApplication.translate('Tidal', 'Playlist Removed'))
        self.playlistMutationFinished.emit(True, 'delete', playlist_id)
        return True

    deleteUserPlaylist = None(deleteUserPlaylist)
    
    def removeTrackFromPlaylist(self = None, playlistUuid = None, playlistIndex = pyqtSlot(str, int)):
        '''
        从歌单移除指定索引的曲目。

        :param playlistUuid: 歌单 UUID。
        :param playlistIndex: 歌单内索引。
        :return: 成功返回 True。
        '''
        if not self.guardLoggedIn():
            return False
        if not playlistUuid:
            pass
        playlist_id = None('').strip()
        if not playlist_id:
            return False
        normalized_index = None(playlistIndex)
        if normalized_index < 0:
            self._showToast(QCoreApplication.translate('Tidal', 'Remove Track from Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'remove', playlist_id)
            return False
        result = None._provider.removePlaylistItems(playlist_id, normalized_index)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._showToast(QCoreApplication.translate('Tidal', 'Remove Track from Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'remove', playlist_id)
            return False
        None.playlistMutationFinished.emit(True, 'remove', playlist_id)
        return True

    removeTrackFromPlaylist = None(removeTrackFromPlaylist)
    
    def addTracksToPlaylist(self = None, playlistUuid = None, itemIds = pyqtSlot(str, str, int), toIndex = (-1,)):
        '''
        批量向歌单添加曲目。

        :param playlistUuid: 歌单 UUID。
        :param itemIds: 逗号分隔曲目 ID。
        :param toIndex: 插入位置，-1 表示追加。
        :return: 成功返回 True。
        '''
        if not self.guardLoggedIn():
            return False
        if not playlistUuid:
            pass
        playlist_id = None('').strip()
        if playlist_id:
            if not itemIds:
                pass
            if not str('').strip():
                return False
            account = None._store.accountState
            if not account.get('countryCode', ''):
                pass
        country_code = str('').strip()
        result = self._provider.addPlaylistItems(playlist_id, itemIds, toIndex, country_code, **('toIndex', 'countryCode'))
        if not isinstance(result, dict) or bool(result.get('success')):
            self._showToast(QCoreApplication.translate('Tidal', 'Add Tracks to Playlist Failed'))
            self.playlistMutationFinished.emit(False, 'batch_add', playlist_id)
            return False
        None.refreshCollectionAfterMutation()
        self._showToast(QCoreApplication.translate('Tidal', 'Tracks Added to Playlist'))
        self.playlistMutationFinished.emit(True, 'batch_add', playlist_id)
        return True

    addTracksToPlaylist = None(addTracksToPlaylist)
    
    def refreshCollectionAfterMutation(self = None):
        '''
        写操作后刷新 My Collection 歌单列表。

        :return: None。
        '''
        account = self._store.accountState
        if not account.get('userId', ''):
            pass
        user_id = str('').strip()
        if not user_id:
            return None
        None._store.collectionState.ensureCalibratedCoverUrlsLoaded(user_id)
        if not account.get('countryCode', ''):
            pass
        country_code = str('').strip()
        sort_preferences = LPTidalCollectionSortPreference.sortPreferencesForUser(user_id)
        result = self._provider.loadUserPlaylists(user_id, country_code, True, sort_preferences, **('skipCache', 'sortPreferences'))
        if isinstance(result, dict) and bool(result.get('success')):
            payload = result.get('data', { })
            playlists = payload.get('allPlaylists', []) if isinstance(payload, dict) else []
            self._store.collectionState.syncUserPlaylists(playlists)
        self._store.notifyCollectionChanged('userPlaylists')

    
    def isUserOwnedPlaylist(self = None, detailInfo = None):
        '''
        判断歌单详情是否属于当前用户。

        :param detailInfo: 歌单详情字典。
        :return: 用户自建返回 True。
        '''
        if not isinstance(detailInfo, dict):
            return False
        return None._provider.isUserOwnedPlaylist(detailInfo)

    
    def _showToast(self = None, text = None):
        '''
        显示全局 Toast。

        :param text: 提示文案。
        :return: None。
        '''
        toast = getattr(LPGlobalUI, 'toast', None)
        main_window = getattr(LPGlobalUI, 'mainWindow', None)
        if not toast is None or hasattr(toast, 'showToast'):
            return None
        if not text:
            pass
        None.showToast(str(''), main_window)

    __classcell__ = None

