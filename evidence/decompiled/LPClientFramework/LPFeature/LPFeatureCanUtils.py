# Source Generated with Decompyle++
# File: LPFeatureCanUtils.pyc (Python 3.9)

'''
@Time ： 2025/2/13 11:51
@Auth ： Chris
@File ：LPFeaturesManager.py
@Desc:
'''
from distutils.version import LooseVersion
from LPClientFramework.LPDevice import LPDevice
from LPClientFramework.LPMediaInfo import LPLoopMode
from LPGlobalUI import featureManager

def canQueueMoveDelete(device = None):
    
    def customConditionCheck(source, loopMode, queueVersion):
        if queueVersion and LooseVersion(queueVersion) >= LooseVersion('1.0'):
            return True
        if None != 'Qobuz' and loopMode in (LPLoopMode.shuffle, LPLoopMode.repeatshuffle, LPLoopMode.singlerepeatshuffle):
            return False

    source = device.mediaInfo.trackSource if device.mediaInfo.trackSource else ''
    loopMode = device.mediaInfo.loopMode
    queueVersion = device.queueManager.version
    return featureManager.isEnabled('QUEUE_MOVE_DELETE', device.streamServiceVersion, customConditionCheck, source, loopMode, queueVersion)

