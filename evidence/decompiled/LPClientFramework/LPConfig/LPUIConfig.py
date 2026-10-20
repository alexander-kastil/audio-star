# Source Generated with Decompyle++
# File: LPUIConfig.pyc (Python 3.9)

import platform
import yaml
from LPClientFramework import LPUtility

class UIConfig:
    
    def __init__(self):
        system = platform.system()
        if system == 'Darwin':
            yml = LPUtility.appLocalDataPath() / 'mac-uiconfig.yml'
        elif system == 'Windows':
            yml = LPUtility.appLocalDataPath() / 'win-uiconfig.yml'
        else:
            yml = LPUtility.appLocalDataPath() / 'win-uiconfig.yml'
    # WARNING: Decompyle incomplete

    
    def __getattr__(self, key):
        '''支持 config.xx 访问'''
        return getattr(self.data, key)



class ConfigNode:
    
    def __init__(self, data = (None,)):
        if data is None:
            data = { }
        object.__setattr__(self, '_data', data)

    
    def __getattr__(self, key):
        '''支持 config.a.xx 访问'''
        if key in self._data:
            value = self._data[key]
            if isinstance(value, dict):
                return ConfigNode(value)
            return None
        raise None(f'''\'{self.__class__.__name__}\' object has no attribute \'{key}\'''')


