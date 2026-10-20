# Source Generated with Decompyle++
# File: LPTidalImageConfig.pyc (Python 3.9)

'''
TIDAL 图片尺寸与使用场景配置。
'''
from enum import Enum
from typing import Any

class LPTidalImageSize(Enum):
    '''TIDAL CDN 图片尺寸枚举，限定可请求的远端资源尺寸。'''
    SIZE_160 = '160x160'
    SIZE_320 = '320x320'
    SIZE_480 = '480x480'
    SIZE_640 = '640x640'
    SIZE_750 = '750x750'
    SIZE_1280 = '1280x1280'


class LPTidalImageUseCase(Enum):
    '''TIDAL 图片使用场景枚举，统一约束远端尺寸与 QML 解码尺寸。'''
    LIST_THUMBNAIL = 'list_thumbnail'
    CARD_COVER = 'card_cover'
    DETAIL_COVER = 'detail_cover'
    HERO_BACKGROUND = 'hero_background'
    ARTIST_AVATAR = 'artist_avatar'
    TABLE_ROW = 'table_row'
    DIALOG_THUMBNAIL = 'dialog_thumbnail'

_USE_CASE_SIZE_MAP = {
    LPTidalImageUseCase.DIALOG_THUMBNAIL: LPTidalImageSize.SIZE_320,
    LPTidalImageUseCase.TABLE_ROW: LPTidalImageSize.SIZE_320,
    LPTidalImageUseCase.ARTIST_AVATAR: LPTidalImageSize.SIZE_320,
    LPTidalImageUseCase.HERO_BACKGROUND: LPTidalImageSize.SIZE_640,
    LPTidalImageUseCase.DETAIL_COVER: LPTidalImageSize.SIZE_640,
    LPTidalImageUseCase.CARD_COVER: LPTidalImageSize.SIZE_320,
    LPTidalImageUseCase.LIST_THUMBNAIL: LPTidalImageSize.SIZE_320 }

def tidalNormalizeImageSize(size = None, fallback = None):
