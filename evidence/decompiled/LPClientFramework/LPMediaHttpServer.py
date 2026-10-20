# Source Generated with Decompyle++
# File: LPMediaHttpServer.pyc (Python 3.9)

from mediafile import MediaFile
import os
import hashlib
from pathlib import Path
import cherrypy
from LPClientFramework import LPUtility
from LPClientFramework.LPUtility import logger

def _isAccessibleMusicFilePath(filePath):
    '''
    判断媒体服务是否允许访问指定音频文件。

    参数:
        filePath (str): 待校验的文件路径。
    返回:
        bool: 路径仍在跟踪目录下或已入库时返回 True，否则返回 False。
    '''
    return LPUtility.isAccessibleLocalMusicFilePath(filePath)


class MediaServerPage:
    
    def index(self):
        return 'WiiM Home Media Service'

    index = cherrypy.expose(index)
    
    def music(self, path):
        if path is None or len(path) == 0:
            raise cherrypy.HTTPError(404, 'File empty')
        filePath = None
    # WARNING: Decompyle incomplete

    music = cherrypy.expose(music)
    
    def cover(self, path):
        if path is None or len(path) == 0:
            raise cherrypy.HTTPError(404, 'File empty')
        filePath = None
    # WARNING: Decompyle incomplete

    cover = cherrypy.expose(cover)

