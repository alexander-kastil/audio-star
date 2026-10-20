# Source Generated with Decompyle++
# File: LPTidalPlaylistDetailViewController.pyc (Python 3.9)

'''
TIDAL 歌单详情页控制器。
'''
from typing import Optional
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QPixmapCache
from PyQt6.QtWidgets import QWidget
from HOME.StreamService.Tidal.controllers.base.LPTidalDetailViewControllerBase import LPTidalDetailViewControllerBase
from HOME.StreamService.Tidal.services.LPTidalRequestScheduler import LPTidalRequest
from HOME.StreamService.Tidal.state.LPTidalStore import LPTidalStore
from LPClientFramework.LPConfig import LPUIPath
import LPGlobalUI

class LPTidalPlaylistDetailViewController(LPTidalDetailViewControllerBase):
    '''TIDAL 歌单详情页，负责加载歌单信息和曲目列表。'''
    PAGE_LIMIT = 50
    
    def __init__(self = None, itemId = None, parent = None):
        '''
        初始化歌单详情页。

        :param itemId: 歌单 ID。
        :param parent: 父级 QWidget。
        :return: None。
        '''
        store = LPTidalStore.instance()
        self._playlist_manager = store.playlistManager
        self._playlist_manager.playlistMutationFinished.connect(self._onPlaylistMutationFinished)
        super().__init__(itemId, 'playlist', store.acquirePlaylistDetailState(itemId), LPUIPath.TidalPlaylistDetailQML, 'pages/TidalPlaylistDetail.qml', 'tidalPlaylistDetailState', parent, **('itemId', 'itemType', 'state', 'qmlPath', 'qmlFileName', 'specificContextName', 'parent'))

    
    def _fetchDetailData(self):
        '''
        拉取歌单详情数据。

        :return: 请求结果字典。
        '''
        return self._provider.loadPlaylistDetail(self._item_id, 0, self.PAGE_LIMIT, **('offset', 'limit'))

    
    def viewWillDisappear(self = None):
        '''
        歌单详情页即将隐藏时清理资源。在基类清理基础上额外清空 QPixmapCache，
        释放虚拟化列表已加载的 QML 图片纹理缓存，缓解多图片页面内存累积。

        :return: None。
        '''
        super().viewWillDisappear()
        QPixmapCache.clear()

    
    def setPlaylistFilterText(self = None, text = None):
        '''
        设置歌单当前已加载曲目的本地过滤文本。

        :param text: 过滤文本。
        :return: None。
        '''
        self._state.setFilterText(text)

    setPlaylistFilterText = None(setPlaylistFilterText)
    
    def loadMorePlaylistItems(self = None):
        '''
        加载下一页歌单曲目。

        :return: None。
        '''
        if not self._state.isLoading and self._state.isLoadingMore or self._state.hasMore:
            return None
        None._state.setLoadingMore(True)
        offset = self._state.offset
        request = None(None, None, (lambda : self._provider.loadPlaylistItems(self._item_id, offset, self.PAGE_LIMIT, True, **('offset', 'limit', 'skipCache'))), self._handlePlaylistItemsResult, **('key', 'tag', 'task', 'callback'))
        self._ensure_scheduler().enqueue(request, 1, **('priority',))

    loadMorePlaylistItems = None(loadMorePlaylistItems)
    
    def updatePlaylistVisibleRange(self = None, firstIndex = None, lastIndex = pyqtSlot(int, int)):
        '''
        更新歌单曲目可见范围。

        :param firstIndex: 首个可见索引。
        :param lastIndex: 最后一个可见索引。
        :return: None。
        '''
        self._state.updateTrackVisibleRange(firstIndex, lastIndex)

    updatePlaylistVisibleRange = None(updatePlaylistVisibleRange)
    
    def _handlePlaylistItemsResult(self = None, result = None):
        '''
        处理歌单曲目分页请求结果。

        :param result: 请求结果。
        :return: None。
        '''
        self._state.setLoadingMore(False)
        if not isinstance(result, dict) or bool(result.get('success')):
            self._state.setErrorMessage('Load more failed. Please try again.')
            return None
        payload = None.get('data', { })
        self._state.appendTracks(payload if isinstance(payload, dict) else { })

    
    def openAddToPlaylist(self = None, trackId = None, trackTitle = pyqtSlot(str, str)):
        '''
        打开 Add-to-playlist 对话框。

        :param trackId: 曲目 ID。
        :param trackTitle: 曲目标题。
        :return: None。
        '''
        self._playlist_manager.openGlobalAddToPlaylist(trackId, trackTitle)

    openAddToPlaylist = None(openAddToPlaylist)
    
    def deleteCurrentPlaylist(self = None):
        '''
        删除当前用户自建歌单。

        :return: None。
        '''
        detail_info = self._state.detailInfo
        if not self._playlist_manager.isUserOwnedPlaylist(detail_info):
            return None
        if not None._playlist_manager.deleteUserPlaylist(self._item_id):
            return None
        None._store.removeDeletedUserPlaylistFromSeeAll(self._item_id)
        top_widget = LPGlobalUI.getTopWidget()
        if top_widget is not None:
            LPGlobalUI.navigationManager.pop(top_widget)

    deleteCurrentPlaylist = None(deleteCurrentPlaylist)
    
    def onShowDeletePlaylistConfirm(self = None):
        '''
        通过 app 级 QDialog 宿主弹出删除歌单确认弹窗，确认后删除当前歌单。

        :return: None。
        '''
        detail_info = self._state.detailInfo
        if not self._playlist_manager.isUserOwnedPlaylist(detail_info):
            return None
        LPTidalConfirmDialogHost = LPTidalConfirmDialogHost
        import HOME.StreamService.Tidal.widgets.LPTidalConfirmDialogHost
        host = LPTidalConfirmDialogHost.instance()
        host._on_confirm_callback = self.deleteCurrentPlaylist
        host.show('Delete Playlist', 'Are you sure you want to delete this playlist? This action cannot be undone.', 'Delete', 'Cancel', LPGlobalUI.THEME_ACCENT_COLOR.name())

    onShowDeletePlaylistConfirm = None(onShowDeletePlaylistConfirm)
    
    def updateCurrentPlaylist(self = None, title = None, description = pyqtSlot(str, str)):
        '''
        更新当前用户自建歌单元数据。

        :param title: 歌单标题。
        :param description: 歌单描述。
        :return: None。
        '''
        detail_info = self._state.detailInfo
        if not self._playlist_manager.isUserOwnedPlaylist(detail_info):
            return None
        if None._playlist_manager.updatePlaylistMetadata(self._item_id, title, description):
            self.reload()

    updateCurrentPlaylist = None(updateCurrentPlaylist)
    
    def removeTrackFromCurrentPlaylist(self = None, playlistIndex = None):
        '''
        从当前用户自建歌单移除曲目。

        :param playlistIndex: 歌单内索引。
        :return: None。
        '''
        detail_info = self._state.detailInfo
        if not self._playlist_manager.isUserOwnedPlaylist(detail_info):
            return None
        if None._playlist_manager.removeTrackFromPlaylist(self._item_id, int(playlistIndex)):
            self.reload()

    removeTrackFromCurrentPlaylist = None(removeTrackFromCurrentPlaylist)
    
    def _onPlaylistMutationFinished(self = None, success = None, action = None, playlistId = {
        'success': bool,
        'action': str,
        'playlistId': str,
        'return': None }):
        '''
        歌单写操作完成后的详情页刷新回调。

        :param success: 是否成功。
        :param action: 操作类型。
        :param playlistId: 本次写操作的目标歌单 ID。
        :return: None。
        '''
        if not success:
            return None
        if not playlistId:
            pass
        normalized_playlist_id = None('').strip()
        if normalized_playlist_id and normalized_playlist_id != self._item_id:
            return None
        if not action:
            pass
        normalized_action = None('')
        if normalized_action != 'delete':
            self._playlist_manager.refreshCollectionAfterMutation()
        if normalized_action in frozenset({'update', 'batch_add', 'remove', 'add'}):
            self.reload()

    __classcell__ = None

