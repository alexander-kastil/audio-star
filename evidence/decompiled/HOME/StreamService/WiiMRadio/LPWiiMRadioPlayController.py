# Source Generated with Decompyle++
# File: LPWiiMRadioPlayController.pyc (Python 3.9)

'''
WiiMRadio 播放逻辑 Mixin。

用法：让 WiiMRadio 的各页控制器（Home / SeeAll / CategoryDetail）继承此类，
即可直接调用 playStation(stationItem) 触发电台播放，无需重复实现 XML 构建与
UPnP 指令发送逻辑。

stationItem 格式（由 LPWiiMRadioDataProvider 归一化后的字典）：
    {
        "stationId": str,   # 电台唯一 ID
        "name":      str,   # 电台名称
        "favicon":   str,   # 封面图地址
        "streamUrl": str,   # 音频流地址
    }
'''
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import LPGlobalUI
from PyQt6.QtCore import QCoreApplication, Qt, QUrl, pyqtSlot
from PyQt6.QtQml import QQmlContext
from LPClientFramework.LPConfig.LPFontConfig import ItemCard_Subtitle, ItemCard_Title, Main_Text, getFontFamily, Small_Title, StackWidget_Title, Sub_Text, Sub_Title
from LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel import LPUpnpAsyncDataModel
from LPClientFramework.LPMusicLibrary import LPRecentlyManager
from LPClientFramework.LPPlayList.LPPlayList import LPHeaderType, LPPlayListSource
from LPClientFramework.LPPublicDefine import MEDIATYPE_RADIO
from LPClientFramework.LPPlayList.LPWiiMRadioPlayList import LPWiiMRadioPlayHeader, LPWiiMRadioPlayItem, LPWiiMRadioPlayList
from LPClientFramework.LPUtility import logger

class LPWiiMRadioPlayController:
    '''
    WiiMRadio 播放逻辑 Mixin。

    继承此类的控制器需保证在第一次调用 playStation 前已完成 QWidget 初始化，
    因为 _upnp_model 延迟创建，无需在 __init__ 中手动调用 super().__init__()。
    '''
    _source: str = LPPlayListSource.WiiMRadio.value
    _upnp_model: Optional[LPUpnpAsyncDataModel] = None
    
    def playStation(self = None, stationItem = None):
        '''
        播放指定电台。

        立即更新设备媒体信息以高亮当前项，随后向设备发送 CreateQueue 指令。

        :param stationItem: 归一化后的电台数据字典。
        :return: None。
        '''
        if not self.guardWiiMRadioSupported():
            return None
        device = None.currentDevice
        if not device:
            logger.error('[WiiMRadio] playStation failed: no current device')
            return None
        if not None(stationItem, dict):
            logger.error('[WiiMRadio] playStation failed: invalid stationItem')
            return None
        name = None.get('name', '')
        stream_url = stationItem.get('streamUrl', '')
        if not stream_url:
            logger.warning(f'''[WiiMRadio] playStation: missing streamUrl, station={name}''')
        playlist = self._build_playlist(stationItem)
        xml = playlist.generateXML()
        play_item = playlist.list[0]
        device.deviceStreamServiceManager.updateMediaInfoForSource(device, self._source, play_item, playlist.header)
        device.guardMediaInfoRollback()
        
        def _on_play_result(response = None, *args):
            if response:
                logger.debug(f'''[WiiMRadio] play success: {name}''')
                LPRecentlyManager.instance().addRecentlyPlayedWithMusicList(playlist, {
                    'openMore': True,
                    'canNavigate': False })
            else:
                logger.debug(f'''[WiiMRadio] play failed: {name}''')

        self._get_upnp_model().palyWithSearchUrl(device, xml, _on_play_result)

    
    def playOrToggleStation(self = None, stationItem = None):
