# Source Generated with Decompyle++
# File: LPMediaServer.pyc (Python 3.9)

import requests
import html
from threading import Thread
from bs4 import BeautifulSoup
from LPClientFramework import UPnPTool
from urllib.parse import urlparse
from LPClientFramework.LPUtility import logger

class LPContentDirectory(object):
    audioContainerArray = [
        'object.container',
        'object.item.audioitem',
        'object.container.genre.musicgenre',
        'object.container.album.musicalbum']
    videoContainerArray = [
        'object.container.person.movieactor',
        'object.item.videoitem',
        'object.container.album.videoalbum',
        'object.container.genre.moviegenre']
    imageContainerArray = [
        'object.item.imageitem.photo',
        'object.container.album.photoalbum',
        'object.item.imageitem']
    
    def __init__(self, ip, port, parentContentDirectory, server):
        self.ip = ip
        self.upnpPort = port
        self.objectID = None
        self.parentContentDirectory = parentContentDirectory
        self.server = server
        self.subItems = []
        self.directoryClass = 'object.container'
        self.title = None
        self.icon = None
        self.artist = None
        self.album = None
        self.albumArtURI = None
        self.date = None
        self.creator = None
        self.duration = None
        self.genre = None
        self.bitRate = None
        self.frequency = None
        self.channels = None
        self.size = None
        self.trackUri = None
        self.isFetching = False

    
    def isContainer(self):
        containerArray = self.audioContainerArray + self.videoContainerArray + self.imageContainerArray
        if self.directoryClass.lower() in containerArray or self.directoryClass.lower().startswith('object.container'):
            return True

    isContainer = property(isContainer)
    
    def isAudio(self):
        return self.directoryClass.startswith('object.item.audioItem')

    isAudio = property(isAudio)
    
    def trackImage(self):
        if self.icon:
            return self.icon
        return None.albumArtURI

    trackImage = property(trackImage)
    
    def search(self, keyword, requestFinishMethod):
        
        def _singleSearch(searchType = None):
