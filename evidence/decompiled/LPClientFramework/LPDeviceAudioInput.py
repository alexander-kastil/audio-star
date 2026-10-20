# Source Generated with Decompyle++
# File: LPDeviceAudioInput.pyc (Python 3.9)

from PyQt6.QtCore import QCoreApplication
from LPClientFramework import LPPublicDefine
from LPClientFramework.LPPublicDefine import LPAudioInputEnum

def audioInputTemplateForDevice(device):
    if device.isWiiMAMP:
        return {
            LPAudioInputEnum.plm_hdmi: {
                'title': QCoreApplication.translate('AudioInput', 'TV'),
                'mode': 'HDMI',
                'mediaType': LPPublicDefine.MEDIATYPE_HDMI },
            LPAudioInputEnum.plm_linein: {
                'title': QCoreApplication.translate('AudioInput', 'Line In'),
                'mode': 'line-in',
                'mediaType': LPPublicDefine.MEDIATYPE_LINEIN },
            LPAudioInputEnum.plm_optical: {
                'title': QCoreApplication.translate('AudioInput', 'Optical In'),
                'mode': 'optical',
                'mediaType': LPPublicDefine.MEDIATYPE_OPTICAL },
            LPAudioInputEnum.plm_bluetooth: {
                'title': QCoreApplication.translate('AudioInput', 'Bluetooth'),
                'mode': 'bluetooth',
                'mediaType': LPPublicDefine.MEDIATYPE_BLUETOOTH },
            LPAudioInputEnum.plm_wifi: {
                'title': QCoreApplication.translate('AudioInput', 'Wi-Fi'),
                'mode': 'wifi',
                'mediaType': LPPublicDefine.MEDIATYPE_UNKNOWN } }
    if None.isWiiMUltra:
        return {
            LPAudioInputEnum.plm_phono: {
                'title': QCoreApplication.translate('AudioInput', 'PHONO'),
                'mode': 'phono',
                'mediaType': LPPublicDefine.MEDIATYPE_PHONO },
            LPAudioInputEnum.plm_hdmi: {
                'title': QCoreApplication.translate('AudioInput', 'TV'),
                'mode': 'HDMI',
                'mediaType': LPPublicDefine.MEDIATYPE_HDMI },
            LPAudioInputEnum.plm_linein: {
                'title': QCoreApplication.translate('AudioInput', 'Line In'),
                'mode': 'line-in',
                'mediaType': LPPublicDefine.MEDIATYPE_LINEIN },
            LPAudioInputEnum.plm_optical: {
                'title': QCoreApplication.translate('AudioInput', 'Optical In'),
                'mode': 'optical',
                'mediaType': LPPublicDefine.MEDIATYPE_OPTICAL },
            LPAudioInputEnum.plm_bluetooth: {
                'title': QCoreApplication.translate('AudioInput', 'Bluetooth'),
                'mode': 'bluetooth',
                'mediaType': LPPublicDefine.MEDIATYPE_BLUETOOTH },
            LPAudioInputEnum.plm_wifi: {
                'title': QCoreApplication.translate('AudioInput', 'Wi-Fi'),
                'mode': 'wifi',
                'mediaType': LPPublicDefine.MEDIATYPE_UNKNOWN } }
    if None.isWiiMPro:
        return {
            LPAudioInputEnum.plm_linein: {
                'title': QCoreApplication.translate('AudioInput', 'Line In'),
                'mode': 'line-in',
                'mediaType': LPPublicDefine.MEDIATYPE_LINEIN },
            LPAudioInputEnum.plm_optical: {
                'title': QCoreApplication.translate('AudioInput', 'Optical In'),
                'mode': 'optical',
                'mediaType': LPPublicDefine.MEDIATYPE_OPTICAL },
            LPAudioInputEnum.plm_bluetooth: {
                'title': QCoreApplication.translate('AudioInput', 'Bluetooth'),
                'mode': 'bluetooth',
                'mediaType': LPPublicDefine.MEDIATYPE_BLUETOOTH },
            10001: {
                'title': QCoreApplication.translate('AudioInput', 'Wi-Fi'),
                'mode': 'wifi',
                'mediaType': LPPublicDefine.MEDIATYPE_UNKNOWN } }
    return {
        LPAudioInputEnum.plm_arc: {
            'title': QCoreApplication.translate('AudioInput', 'ARC'),
            'mode': 'arc',
            'mediaType': LPPublicDefine.MEDIATYPE_ARC },
        LPAudioInputEnum.plm_phono: {
            'title': QCoreApplication.translate('AudioInput', 'PHONO'),
            'mode': 'phono',
            'mediaType': LPPublicDefine.MEDIATYPE_PHONO },
        LPAudioInputEnum.plm_pc_usb: {
            'title': QCoreApplication.translate('AudioInput', 'USBDAC'),
            'mode': 'PCUSB',
            'mediaType': LPPublicDefine.MEDIATYPE_EXTERNAL_USB },
        LPAudioInputEnum.plm_extern_bt: {
            'title': QCoreApplication.translate('AudioInput', 'Bluetooth'),
            'mode': 'extern_bluetooth',
            'mediaType': LPPublicDefine.MEDIATYPE_BLUETOOTH },
        LPAudioInputEnum.plm_wifi: {
            'title': QCoreApplication.translate('AudioInput', 'Wi-Fi'),
            'mode': 'wifi',
            'mediaType': LPPublicDefine.MEDIATYPE_UNKNOWN },
        LPAudioInputEnum.plm_coaxial: {
            'title': QCoreApplication.translate('AudioInput', 'CO-AXIAL'),
            'mode': 'co-axial',
            'mediaType': LPPublicDefine.MEDIATYPE_CO_AXIAL },
        LPAudioInputEnum.plm_hdmi: {
            'title': QCoreApplication.translate('AudioInput', 'TV'),
            'mode': 'HDMI',
            'mediaType': LPPublicDefine.MEDIATYPE_HDMI },
        LPAudioInputEnum.plm_optical: {
            'title': QCoreApplication.translate('AudioInput', 'Optical'),
            'mode': 'optical',
            'mediaType': LPPublicDefine.MEDIATYPE_OPTICAL },
        LPAudioInputEnum.plm_rca: {
            'title': QCoreApplication.translate('AudioInput', 'Stereo out'),
            'mode': 'RCA',
            'mediaType': LPPublicDefine.MEDIATYPE_RCA },
        LPAudioInputEnum.plm_radio: {
            'title': QCoreApplication.translate('AudioInput', 'Radio'),
            'mode': 'FM',
            'mediaType': LPPublicDefine.MEDIATYPE_RADIO },
        LPAudioInputEnum.plm_linein2: {
            'title': QCoreApplication.translate('AudioInput', 'Aux'),
            'mode': 'line-in',
            'mediaType': LPPublicDefine.MEDIATYPE_LINEIN2 },
        LPAudioInputEnum.plm_linein: {
            'title': QCoreApplication.translate('AudioInput', 'Aux In'),
            'mode': 'line-in',
            'mediaType': LPPublicDefine.MEDIATYPE_LINEIN },
        LPAudioInputEnum.plm_xlr: {
            'title': QCoreApplication.translate('AudioInput', 'XLR'),
            'mode': 'XLR',
            'mediaType': LPPublicDefine.MEDIATYPE_XLR },
        LPAudioInputEnum.plm_tf: {
            'title': QCoreApplication.translate('AudioInput', 'TF Card'),
            'mode': 'TFCard',
            'mediaType': LPPublicDefine.MEDIATYPE_LOCALLIST_TF },
        LPAudioInputEnum.plm_usb: {
            'title': QCoreApplication.translate('AudioInput', 'USB Devices'),
            'mode': 'udisk',
            'mediaType': LPPublicDefine.MEDIATYPE_EXTERNAL_USB },
        None.plm_bluetooth: {
            'title': QCoreApplication.translate('AudioInput', 'Bluetooth'),
            'mode': 'bluetooth',
            'mediaType': LPPublicDefine.MEDIATYPE_BLUETOOTH } }


def makeAudioInputArray(device):
