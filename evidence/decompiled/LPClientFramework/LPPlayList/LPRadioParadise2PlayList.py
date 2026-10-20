# Source Generated with Decompyle++
# File: LPRadioParadise2PlayList.pyc (Python 3.9)

'''
@Time ： 2025/1/2 16:26
@Auth ： Chris
@File ：LPRadioParadise2PlayList.py
@Desc:
'''
import datetime
from html import escape
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayListSource, LPPlayItem, LPAccount

class LPRadioParadise2Account(LPAccount):
    
    def __init__(self = None):
        super().__init__()
        self.source = LPPlayListSource.RadioParadise2.value
        self.anonUserId = None
        self.cUserId = None

    __classcell__ = None


class LPRadioParadise2PlayList(LPPlayMusicList):
    
    def __init__(self = None):
        super().__init__()

    
    def generateXML(self):
        '''
        <?xml version="1.0"?>
        <PlayList>
            <ListName>RP Global Mix</ListName>
            <ListInfo>
                <SearchUrl>https://api.radioparadise.com/api/gapless?chan=3&amp;bitrate=4&amp;C_user_id=1264406187&amp;player_id=uuid:FF98F7F4-A937-DD0D-7447-DA2BFF98F7F4</SearchUrl>
                <ContentType>station</ContentType>
                <PicUrl>https://img.radioparadise.com/channels/0/3/cover_512x512/0.jpg</PicUrl>
                <ContentType>station</ContentType>
                <SourceName>RadioParadise2</SourceName>
            </ListInfo>
        </PlayList>
        '''
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(self.header.headTitle if self.header.headTitle else '')
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape(self.header.searchUrl if self.header.searchUrl else '')
        xmlStr += '<ContentType>station</ContentType>'
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(self.header.imageUrl if self.header.imageUrl else '')
        xmlStr += '<StartPlayIndex>1</StartPlayIndex>'
        xmlStr += '</ListInfo>'
        xmlStr += '</PlayList>'
        return xmlStr

    
    def generateBackupQueueXML(self, listName):
        '''
        <?xml version="1.0"?>
        <PlayList>
            <ListName>RP Rock Mix_#~2025-04-01 11:27:20</ListName>
            <ListInfo>
                <SourceName>RadioParadise2</SourceName>
                <SearchUrl>https://api.radioparadise.com/api/gapless?chan=2&amp;bitrate=4&amp;C_user_id=1257664614&amp;player_id=FF98F7F4BBB1646CE0AC7A30</SearchUrl>
                <PicUrl>https://img.radioparadise.com/covers/l/B000002UBB.jpg</PicUrl>
                <Login_username></Login_username>
            </ListInfo>
        </PlayList>
        '''
        xmlStr = '<?xml version="1.0"?><PlayList>'
        xmlStr += '<ListName>%s</ListName>' % escape(listName)
        xmlStr += '<ListInfo>'
        xmlStr += '<SourceName>%s</SourceName>' % self.header.mediaSource
        xmlStr += '<SearchUrl>%s</SearchUrl>' % escape(self.header.searchUrl if self.header.searchUrl else '')
        xmlStr += '<ContentType>station</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
        xmlStr += '<Login_username></Login_username>'
        xmlStr += '</ListInfo>'
        xmlStr += '</PlayList>'
        return xmlStr

    
    def generateSetKeyMappingXML(self, name):
        xmlStr = '<Name>%s</Name>' % escape(name)
        xmlStr += '<Source>%s</Source>' % self.header.mediaSource
        xmlStr += '<ContentType>station</ContentType>'
        picUrl = self.getPicUrl()
        xmlStr += '<PicUrl>%s</PicUrl>' % escape(picUrl if picUrl else '')
        xmlStr += '<RoutineId>Empty</RoutineId>'
        xmlStr += '<Loop>0</Loop>'
        xmlStr += '<Shuffle>0</Shuffle>'
        return xmlStr

    __classcell__ = None


class LPRadioParadise2PlayHeader(LPPlayHeader):
    
    def __init__(self = None):
        super().__init__()
        self.mediaSource = LPPlayListSource.RadioParadise2.value

    __classcell__ = None


class LPRadioParadise2PlayItem(LPPlayItem):
    
    def __init__(self = None):
        super().__init__()
        self.date = None
        self.localPath = None
        self.trackNumber = 0
        self.trackSource = LPPlayListSource.RadioParadise2.value
        self.customUUID = None
        self.bitrate = 0
        self.samplerate = 0
        self.channels = 0

    __classcell__ = None

