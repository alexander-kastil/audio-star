# Source Generated with Decompyle++
# File: LPFeaturesManager.pyc (Python 3.9)

'''
@Time ： 2025/2/13 15:42
@Auth ： Chris
@File ：LPFeatureCanUtils.py
@Desc:
'''
import yaml
from distutils.version import LooseVersion
from LPClientFramework.LPUtility import appLocalDataPath, logger

class LPFeaturesManager:
    '''
    控制功能开关，如queue move
    '''
    
    def __init__(self):
        configFile = appLocalDataPath() / 'feature.yml'
        self.config = self.loadConfig(configFile)

    
    def loadConfig(self, config_file):
        with open(config_file, 'r', 'utf-8', **('encoding',)) as f:
            config = yaml.safe_load(f)
            None(None, None, None)
        with None:
            if not None:
                pass
        return config

    
    def isEnabled(self, featureName, currentVersion, customConditionMethod = (None,), *args):
        ''' 检查当前版本是否启用指定功能
            currentVersion: stream service version
        '''
        if featureName not in self.config:
            logger.error(f'''feature--{featureName} not exist! ''')
            return False
        feature = None.config[featureName]
        enabled = feature.get('enabled', False)
        if not enabled:
            return enabled
        minVer = None.get('min_version', None)
        maxVer = feature.get('max_version', None)
        if (minVer or LooseVersion(currentVersion) < LooseVersion(minVer) or maxVer) and LooseVersion(currentVersion) >= maxVer:
            logger.debug(f'''feature--{featureName} not allow in current version: {currentVersion} (minVer: {minVer}, maxVer: {maxVer})''')
            return False
        conditionRequired = None.get('condition', False)
    # WARNING: Decompyle incomplete


if __name__ == '__main__':
    feature_manager = LPFeaturesManager()
    feature_name = 'QUEUE_MOVE'
    current_version = '1.4'
    
    def customConditionCheck(cond):
        return True

    ret = feature_manager.isEnabled(feature_name, current_version, customConditionCheck, 12)
    print(ret)
