# Source Generated with Decompyle++
# File: LPDeviceAudioOutput.pyc (Python 3.9)

from PyQt6.QtCore import QCoreApplication
from LPClientFramework.LPPublicDefine import LPAudioOutEnum

def makeAudioOutputArray(device):
    if device.isWiiMAMP:
        return [
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Speaker Out'),
                'type': LPAudioOutEnum.AudioOutput_AuxOutDefault,
                'value': '2' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Bluetooth Out'),
                'type': LPAudioOutEnum.AudioOutput_Bluetooth,
                'value': '5' }]
    if None.isWiiMUltra:
        return [
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Line Out'),
                'type': LPAudioOutEnum.AudioOutput_AuxOutDefault,
                'value': '2' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Optical Out'),
                'type': LPAudioOutEnum.AudioOutput_SPDIF,
                'value': '1' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'COAX Out'),
                'type': LPAudioOutEnum.AudioOutput_COAX,
                'value': '3' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Headphone Out'),
                'type': LPAudioOutEnum.AudioOutput_PhoneJack,
                'value': '4' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Bluetooth Out'),
                'type': LPAudioOutEnum.AudioOutput_Bluetooth,
                'value': '5' }]
    if None.isWiiMPro:
        return [
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Line Out'),
                'type': LPAudioOutEnum.AudioOutput_AuxOutDefault,
                'value': '2' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Optical Out'),
                'type': LPAudioOutEnum.AudioOutput_SPDIF,
                'value': '1' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'COAX Out'),
                'type': LPAudioOutEnum.AudioOutput_COAX,
                'value': '3' },
            {
                'title': QCoreApplication.translate('DeviceSetting', 'Bluetooth Out'),
                'type': LPAudioOutEnum.AudioOutput_Bluetooth,
                'value': '5' }]
    return [
        {
            'title': None.translate('DeviceSetting', 'Aux Out'),
            'type': LPAudioOutEnum.AudioOutput_AuxOutDefault,
            'value': 'AUX' },
        {
            'title': QCoreApplication.translate('DeviceSetting', 'Optical Out'),
            'type': LPAudioOutEnum.AudioOutput_SPDIF,
            'value': 'SPDIF' },
        {
            'title': QCoreApplication.translate('DeviceSetting', 'Bluetooth Out'),
            'type': LPAudioOutEnum.AudioOutput_Bluetooth,
            'value': 'BLUETOOTH' }]

outputInfoTemplate = {
    'AUDIO_OUTPUT_SPDIF_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'Optical Out'),
        'type': LPAudioOutEnum.AudioOutput_SPDIF },
    'AUDIO_OUTPUT_AUX_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'Aux Out'),
        'type': LPAudioOutEnum.AudioOutput_AuxOutDefault },
    'AUDIO_OUTPUT_COAX_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'COAX Out'),
        'type': LPAudioOutEnum.AudioOutput_COAX },
    'AUDIO_OUTPUT_PHONE_JACK_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'Headphone Out'),
        'type': LPAudioOutEnum.AudioOutput_PhoneJack },
    'AUDIO_OUTPUT_HDMI_MODE': {
        'title': 'HDMI',
        'type': LPAudioOutEnum.AudioOutput_HDMI },
    'AUDIO_OUTPUT_BT_SOURCE_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'Bluetooth'),
        'type': LPAudioOutEnum.AudioOutput_Bluetooth },
    'AUDIO_OUTPUT_UAC_CARD_MODE': {
        'title': QCoreApplication.translate('DeviceSetting', 'USB Out'),
        'type': LPAudioOutEnum.AudioOutput_UacCard } }
