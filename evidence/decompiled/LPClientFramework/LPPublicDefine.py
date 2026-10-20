# Source Generated with Decompyle++
# File: LPPublicDefine.pyc (Python 3.9)

import enum
from enum import IntEnum

class LPMSCommonOption(enum.Enum):
    Option_View_Artist = 'View Artist'
    Option_View_Album = 'View Album'
    Option_Add_To_Playlist = 'Add to Playlist'
    Option_Remove_From_Playlist = 'Remove from Playlist'


class LPDeviceCapability(IntEnum):
    CAP2_FUNC_SUPPORT_MAX_VOLUME = 3
    CAP2_FUNC_DISABLE_A2DP_SINK = 4
    CAP2_FUNC_DISABLE_A2DP_SOURCE = 5
    CAP2_FUNC_MULTIROOM_TOGGLE = 6
    CAP2_FUNC_MULTIROOM_APCLI_PREFER = 7
    CAP2_FUNC_MULTIROOM_APCLI_AUTO = 8
    CAP2_FUNC_FAST_JOIN_ROUTER = 9
    CAP2_FUNC_AP_AUTO_PASSWORD = 10
    CAP2_FUNC_AP_AUTO_HIDE = 11
    CAP2_FUNC_EXT_USB = 12
    CAP2_FUNC_TF_MODE = 13
    CAP2_FUNC_ASR = 14
    CAP2_FUNC_DISABLE_INTERCOM = 15


class LPAudioOutEnum(IntEnum):
    AudioOutput_None = (0,)
    AudioOutput_AuxOutDefault = 1
    AudioOutput_SPDIF = 2
    AudioOutput_Bluetooth = 3
    AudioOutput_COAX = 4
    AudioOutput_PhoneJack = 5
    AudioOutput_Airplay = 6
    AudioOutput_DLNA = 7
    AudioOutput_HDMI = 8
    AudioOutput_UacCard = 9


class LPAudioInputEnum(IntEnum):
    plm_linein = 1
    plm_bluetooth = 2
    plm_usb = 3
    plm_optical = 4
    plm_rca = 5
    plm_linein2 = 8
    plm_radio = 7
    plm_hdmi = 10
    plm_tf = 13
    plm_xlr = 9
    plm_coaxial = 6
    plm_cd = 11
    plm_wifi = 10001
    plm_extern_bt = 14
    plm_pc_usb = 15
    plm_phono = 16
    plm_spdif_output = 21
    plm_arc = 22
    plm_optical2 = 18
    plm_coaxial2 = 19
    plm_dab = 17

MEDIATYPE_NONE = 'NONE'
MEDIATYPE_STATION = 'STATION-NETWORK'
MEDIATYPE_RADIO = 'RADIO-NETWORK'
MEDIATYPE_NETLIST = 'SONGLIST-NETWORK'
MEDIATYPE_LOCALLIST = 'SONGLIST-LOCAL'
MEDIATYPE_LOCALLIST_TF = 'SONGLIST-LOCAL_TF'
MEDIATYPE_EXTERNAL_TF = 'EXTERNAL_TFCARD'
MEDIATYPE_THIRDPARTY = 'THIRD-DLNA'
MEDIATYPE_AIRPLAY = 'AIRPLAY'
MEDIATYPE_ROON = 'Roon'
MEDIATYPE_UNKNOWN = 'UNKNOWN'
MEDIATYPE_SPOTIFY = 'SPOTIFY'
MEDIATYPE_QPLAY = 'QPLAY'
MEDIATYPE_ALI = 'ALI-RPC'
MEDIATYPE_LINEIN = 'LINE-IN'
MEDIATYPE_BLUETOOTH = 'BLUETOOTH'
MEDIATYPE_EXTERNAL_USB = 'EXTERNAL_USB'
MEDIATYPE_OPTICAL = 'OPTICAL'
MEDIATYPE_RCA = 'RCA'
SOURCES_NO_LOGIN = frozenset({
    'Samba',
    'vTuner',
    'RadioParadise',
    'Linkplay Radio',
    'newTuneIn',
    'RemoteLocal',
    'UPnPServer',
    'SleepRadio',
    'Soundtrack',
    'Roon',
    'SPOTIFY',
    'SleepSound',
    'RadioParadise2',
    'CustomRadio',
    'WiiMRadio',
    'PC_RemoteLocal',
    'HotMix'})
MEDIATYPE_ALEXA = 'ALEXA'
MEDIATYPE_ALEXA_PANDORA = 'ALEXA_PANDORA'
MEDIATYPE_PANDORA = 'Pandora'
MEDIATYPE_ALEXA_AUDIBLE = 'ALEXA_AUDIBLE'
MEDIATYPE_AUDIBLE = 'Audible'
MEDIATYPE_LINEIN2 = 'LINE-IN2'
MEDIATYPE_AUX2 = 'SECORD_LINEIN'
MEDIATYPE_RADIO2 = 'FM'
MEDIATYPE_HDMI = 'HDMI'
MEDIATYPE_CO_AXIAL = 'CO_AXIAL'
MEDIATYPE_CD = 'CD'
MEDIATYPE_XLR = 'XLR'
MEDIATYPE_CHROME_CAST = 'CAST'
MEDIATYPE_TIDAL_CONNECT = 'TIDAL_CONNECT'
MEDIATYPE_PHONO = 'PHONO'
MEDIATYPE_ARC = 'ARC'
MEDIATYPE_CO_AXIAL2 = 'SECOND_CO_AXIAL'
MEDIATYPE_OPTICAL2 = 'SECOND_OPTICAL'
MEDIATYPE_DAB = 'DAB'
MEDIATYPE_USB_DAC = 'USB_DAC'
MEDIATYPE_AUXIN = 'AUXIN'

class LPAudioPhonoEnum(IntEnum):
    Phono_Stage_Input_MM = 0
    Phono_Stage_Input_MC = 1

