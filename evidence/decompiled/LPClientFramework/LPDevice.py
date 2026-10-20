# Source Generated with Decompyle++
# File: LPDevice.pyc (Python 3.9)

import threading
from xml.sax.saxutils import unescape
import requests
import json
from distutils.version import LooseVersion
from PyQt6.QtCore import QTimer
from cherrypy import response
from urllib3.exceptions import InsecureRequestWarning
from LPClientFramework import UPnPTool, LPTLSTool, LPUtility, LPStreamServiceManager, LPPublicDefine
from LPClientFramework.LPDeviceStreamServiceManager import LPDeviceStreamServiceManager
from LPClientFramework.LPMediaInfo import LPMediaInfo
from LPClientFramework.LPDeviceManager.LPDeviceGroupInfo import LPDeviceGroupInfo
from LPClientFramework.LPDeviceManager.LPGroup import LPGroupType
from LPClientFramework.LPPlayList.LPPlayList import LPPlayMusicList, LPPlayHeader, LPPlayItem, LPPlayListSource
from LPClientFramework.LPPublicDefine import LPAudioInputEnum
from LPClientFramework.LPQueueManager import LPQueueManager
from LPClientFramework.LPUtility import logger, logAcctBifurcate
from threading import Thread
from bs4 import BeautifulSoup
LPDeviceConfigDict = {
    'Muzo_Mini': {
        'name': 'WiiM Mini',
        'supportTouchControl': True,
        'supportStatusLight': True,
        'supportOverrideVolume': True,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': False,
        'supportMQA': True,
        'supportSubwoofer': False,
        'supportSyncAudio': True,
        'image': 'wiim_mini' },
    'WiiM_Pro_with_gc4a': {
        'name': 'WiiM Pro',
        'supportTouchControl': True,
        'supportStatusLight': True,
        'supportOverrideVolume': True,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': True,
        'supportMQA': True,
        'supportSubwoofer': False,
        'supportSyncAudio': True,
        'image': 'wiim_pro' },
    'WiiM_Pro_AVS': {
        'name': 'WiiM Pro',
        'supportTouchControl': True,
        'supportStatusLight': True,
        'supportOverrideVolume': True,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': True,
        'supportMQA': True,
        'supportSubwoofer': False,
        'supportSyncAudio': True,
        'image': 'wiim_pro' },
    'WiiM_Pro_Plus': {
        'name': 'WiiM Pro Plus',
        'supportTouchControl': True,
        'supportStatusLight': True,
        'supportOverrideVolume': True,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': True,
        'supportMQA': True,
        'supportDACDigitalFilter': True,
        'supportSubwoofer': False,
        'supportSyncAudio': True,
        'supportLineinInputResolution': True,
        'image': 'wiim_pro' },
    'WiiM_AMP': {
        'name': 'WiiM Amp',
        'supportTouchControl': False,
        'supportStatusLight': True,
        'supportOverrideVolume': False,
        'supportVolumeIndicator': True,
        'supportFixedVolumeOutput': False,
        'supportSPDIFOutput': False,
        'supportCoaxOutput': False,
        'supportMQA': False,
        'supportSubwoofer': True,
        'supportSyncAudio': False,
        'supportLineinInputResolution': True,
        'image': 'wiim_amp' },
    'WiiM_Amp_Pro': {
        'name': 'WiiM Amp Pro',
        'supportTouchControl': False,
        'supportStatusLight': True,
        'supportOverrideVolume': False,
        'supportVolumeIndicator': True,
        'supportFixedVolumeOutput': False,
        'supportSPDIFOutput': False,
        'supportCoaxOutput': False,
        'supportMQA': False,
        'supportSubwoofer': True,
        'supportSyncAudio': False,
        'supportLineinInputResolution': True,
        'image': 'wiim_amp' },
    'WiiM_Ultra': {
        'name': 'WiiM Ultra',
        'supportTouchControl': False,
        'supportStatusLight': False,
        'supportOverrideVolume': False,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': True,
        'supportMQA': True,
        'supportDACDigitalFilter': True,
        'supportSubwoofer': True,
        'supportSyncAudio': True,
        'supportLineinInputResolution': True,
        'image': 'wiim_ultra' },
    'WiiM_CI_MOD_S': {
        'name': 'WiiM CI MOD S',
        'supportTouchControl': True,
        'supportStatusLight': True,
        'supportOverrideVolume': True,
        'supportVolumeIndicator': False,
        'supportFixedVolumeOutput': True,
        'supportSPDIFOutput': True,
        'supportCoaxOutput': False,
        'supportMQA': True,
        'supportDACDigitalFilter': True,
        'supportSubwoofer': False,
        'supportSyncAudio': True,
        'supportLineinInputResolution': True,
        'image': 'wiim_pro' } }
LPDeviceImageNameDict = {
    'Muzo_Mini': 'wiim_mini',
    'WiiM_Pro_with_gc4a': 'wiim_pro',
    'WiiM_Pro_AVS': 'wiim_pro',
    'WiiM_Pro_Plus': 'wiim_pro',
    'WiiM_AMP': 'wiim_amp',
    'WiiM_Amp_Pro': 'wiim_amp',
    'WiiM_Amp_4layer': 'wiim_amp',
    'WiiM_AMP_No_MFI': 'wiim_amp',
    'WiiM_Amp_Ultra': 'wiim_amp_ultra',
    'WiiM_Ultra': 'wiim_ultra',
    'WiiM_Ultra_X': 'wiim_ultra',
    'WiiM_Ultra_CN': 'wiim_ultra',
    'WiiM_CI_MOD_S': 'wiim_c10',
    'WiiM_CI_MOD_A80': 'wiim_c10_mod_a80',
    'WiiM_Bar': 'wiim_bar',
    'WiiM_Remote': 'wiim_remote',
    'WiiM_Sound': 'wiim_sound',
    'WiiM_Sound_CN': 'wiim_sound',
    'WiiM_Sound_Lite': 'wiim_sound_lite',
    'WiiM_Sound_Lite_V2': 'wiim_sound_lite',
    'WiiM_SUB': 'wiim_sub',
    'WiiM_Sub': 'wiim_sub',
    'WiiM_Sub_Pro': 'wiim_sub_pro',
    'WiiM_Vibelink_Amp': 'wiim_vibelink_amp' }

def _diagnoseSlaveUuids(slaveList):
