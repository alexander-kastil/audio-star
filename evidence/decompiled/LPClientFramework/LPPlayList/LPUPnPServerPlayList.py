# Source Generated with Decompyle++
# File: LPUPnPServerPlayList.pyc (Python 3.9)

from LPPlayList import *

class LPUPnPServerPlayList(LPPlayMusicList):
    
    def __init__(self):
        LPPlayMusicList.__init__(self)



class LPUPnPServerPlayHeader(LPPlayHeader):
    
    def __init__(self):
        LPPlayHeader.__init__(self)
        self.mediaSource = LPPlayListSource.UPnPServer.value


