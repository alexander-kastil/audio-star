# Source Generated with Decompyle++
# File: LPHttpServerManager.pyc (Python 3.9)

import cherrypy
import portend
import random
from cherrypy import dispatch
from cherrypy._cpserver import Server
from LPClientFramework import LPUtility
from LPClientFramework.LPMediaHttpServer import MediaServerPage
from LPClientFramework.LPOAuthHttpServer import OAuthServerPage
from LPClientFramework.LPUPnPHttpServer import UPnPServerPage
from LPClientFramework.LPUtility import logger

class Root:
    
    def __init__(self):
        self.upnp = UPnPServerPage()
        self.media = MediaServerPage()
        self.auth = OAuthServerPage()



def bindServer(port):
    s = Server()
    s.socket_host = '0.0.0.0'
# WARNING: Decompyle incomplete


def disableAutoreloader():
    '''关闭 CherryPy 源码自动重载。

    参数:
        无。
    返回:
        无。
    '''
    cherrypy.config.update({
        'engine.autoreload.on': False })
# WARNING: Decompyle incomplete


def start():
    '''启动 UPnP、媒体和 OAuth HTTP 服务。

    参数:
        无。
    返回:
        无。
    '''
    disableAutoreloader()
    upnpServerAddr = f'''localhost:{LPUtility.upnpServerPort}'''
    mediaServerAddr = f'''localhost:{LPUtility.mediaServerPort}'''
    oauthServerAddr = f'''localhost:{LPUtility.oauthServerPort}'''
# WARNING: Decompyle incomplete


def stop(name = None):
    '''
    name: None upnp media
    '''
    if name == 'upnp' and LPUtility.upnpServer:
        LPUtility.upnpServer.stop()
    elif name == 'media' and LPUtility.upnpServer:
        LPUtility.mediaServer.stop()
# WARNING: Decompyle incomplete


def startOne(name = None):
    if name == 'upnp' and LPUtility.upnpServer:
        LPUtility.upnpServer.start()
    elif name == 'media' and LPUtility.upnpServer:
        LPUtility.mediaServer.start()
# WARNING: Decompyle incomplete

