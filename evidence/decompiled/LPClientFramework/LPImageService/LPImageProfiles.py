# Source Generated with Decompyle++
# File: LPImageProfiles.pyc (Python 3.9)

'''
全局 QML 图片 profile 定义。
'''
from dataclasses import dataclass
from typing import Dict
from PyQt6.QtCore import Qt
LPImageProfile = dataclass(True, **('frozen',))(<NODE:12>)
WIIMRADIO_FAVICON_PROFILE = 'wiimradio_favicon'
TIDAL_COVER_320_PROFILE = 'tidal_cover_320'
IMAGE_PROFILES: Dict[(str, LPImageProfile)] = {
    TIDAL_COVER_320_PROFILE: LPImageProfile(TIDAL_COVER_320_PROFILE, 320, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 604800, True, True, **('name', 'size', 'aspectMode', 'ttlSeconds', 'saveOriginal', 'useSharedUrlCacheLayout')),
    WIIMRADIO_FAVICON_PROFILE: LPImageProfile(WIIMRADIO_FAVICON_PROFILE, 155, Qt.AspectRatioMode.KeepAspectRatio, 86400, True, **('name', 'size', 'aspectMode', 'ttlSeconds', 'useSharedUrlCacheLayout')) }

def imageProfile(profileName = None):
    '''
    按名称返回图片 profile。

    :param profileName: profile 名称。
    :return: 图片 profile 配置。
    '''
    if not profileName:
        pass
    normalized = str('').strip()
    profile = IMAGE_PROFILES.get(normalized)
    if profile is None:
        raise ValueError(f'''unknown_image_profile:{normalized}''')
    return profile

