# Source Generated with Decompyle++
# File: LPRadioParadise2NetworkDataModel.pyc (Python 3.9)

'''
@Time ： 2025/2/14 17:51
@Auth ： Chris
@File ：LPRadioParadise2UpnpDataModel.py
@Desc:
'''
from PyQt6.QtCore import pyqtSignal
from LPClientFramework.LPDataModel.NetWorkDataModel.LPNetworkDataModel import LPNetworkDataModel
from LPClientFramework.LPUtility import logger

class LPRadioParadise2NetworkDataModel(LPNetworkDataModel):
    loadSkeletonSignal = pyqtSignal()
    
    def __init__(self = None):
        super().__init__()
        self.channelUrlFormatter = 'https://api.radioparadise.com/api/list_chan?C_user_id={}'

    
    def fetchChannelData(self, cUserId, callback):
        url = self.channelUrlFormatter.format(cUserId)
        logger.debug('[RadioParadise2] fetchChannelData url == ' + url)
        if not self.session.cache.has_url(url):
            logger.debug('url == not has_url')
            self.loadSkeletonSignal.emit()
        self.getData(self.worker, url, callback)

    __classcell__ = None

