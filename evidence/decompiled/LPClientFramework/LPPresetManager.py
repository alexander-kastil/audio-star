# Source Generated with Decompyle++
# File: LPPresetManager.pyc (Python 3.9)

'''
@Time ： 2025/4/15 18:50
@Auth ： Chris
@File ：LPPresetManager.py
@Desc:
'''
import copy
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class PresetManager:
    
    def __init__(self):
        self.device = LPGlobalUI.currentDevice

    
    def getKeyMapping(self, device, callback):
        device.asyncUpnpPost('GetKeyMapping', { }, callback)

    
    def backupQueue(self, device, streamService, playList, listName, playSection = (None,)):
