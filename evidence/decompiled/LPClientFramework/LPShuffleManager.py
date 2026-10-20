# Source Generated with Decompyle++
# File: LPShuffleManager.pyc (Python 3.9)

'''
@Time ： 2025/7/21 11:37
@Auth ： Chris
@File ：LPShuffleManager.py
@Desc:
'''
from PyQt6.QtGui import QIcon
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPEventFilter.ButtonEventFilter.LPButtonEventFilter import LPButtonEventFilter
from LPClientFramework.LPMediaInfo import LPLoopMode

class LPShuffleManager:
    
    def setShuffle():
        
        def callback(response = None):
            LPGlobalUI.currentDevice.updateMediaInfo({
                'loopMode': int(nextMode) })

        currentMode = LPGlobalUI.currentDevice.mediaInfo.loopMode
        nextMode = LPLoopMode.shuffle
        if currentMode == LPLoopMode.singlerepeat:
            nextMode = LPLoopMode.singlerepeatshuffle
        elif currentMode == LPLoopMode.listrepeat:
            nextMode = LPLoopMode.repeatshuffle
        elif currentMode in (LPLoopMode.shuffle, LPLoopMode.repeatshuffle, LPLoopMode.singlerepeatshuffle):
            return None
        LPGlobalUI.currentDevice.updateMediaInfo({
            'loopMode': int(nextMode) })
        LPGlobalUI.currentDevice.asyncUpnpPost('SetQueueLoopMode', {
            'LoopMode': int(nextMode) }, callback, **('callbackMethod',))

    setShuffle = staticmethod(setShuffle)
    
    def setNoShuffle():
        
        def callback(response = None):
            LPGlobalUI.currentDevice.updateMediaInfo({
                'loopMode': int(nextMode) })

        currentMode = LPGlobalUI.currentDevice.mediaInfo.loopMode
        nextMode = LPLoopMode.default
        if currentMode == LPLoopMode.singlerepeatshuffle:
            nextMode = LPLoopMode.singlerepeat
        elif currentMode == LPLoopMode.repeatshuffle:
            nextMode = LPLoopMode.listrepeat
        elif currentMode in (LPLoopMode.default, LPLoopMode.singlerepeat, LPLoopMode.listrepeat):
            return None
        LPGlobalUI.currentDevice.updateMediaInfo({
            'loopMode': int(nextMode) })
        LPGlobalUI.currentDevice.asyncUpnpPost('SetQueueLoopMode', {
            'LoopMode': int(nextMode) }, callback, **('callbackMethod',))

    setNoShuffle = staticmethod(setNoShuffle)
    
    def updateLoopShuffleButton(device, loopButton, shuffleButton):
        loopImage = 'miniBar/repeat.png'
        shuffleImage = 'miniBar/shuffle.png'
        shuffleTint = LPGlobalUI.THEME_LIGHT_COLOR
        loopTint = LPGlobalUI.THEME_LIGHT_COLOR
        if device is None:
            tintImage = LPUtility.tintImage(LPGlobalUI.imagePath(loopImage), loopTint)
            LPButtonEventFilter(loopButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath(loopImage)), QIcon(tintImage), 'image')
            tintImage = LPUtility.tintImage(LPGlobalUI.imagePath(shuffleImage), shuffleTint)
            LPButtonEventFilter(shuffleButton, QIcon(tintImage), QIcon(LPGlobalUI.imagePath(shuffleImage)), QIcon(tintImage), 'image')
            return None
        loopMode = None.mediaInfo.loopMode
        if loopMode == LPLoopMode.singlerepeat or loopMode == LPLoopMode.singlerepeatshuffle:
            loopImage = 'miniBar/singlerepeat.png'
        if loopMode == LPLoopMode.listrepeat:
            shuffleTint = LPGlobalUI.THEME_LIGHT_COLOR
            loopTint = LPGlobalUI.THEME_HIGH_COLOR
        elif loopMode == LPLoopMode.singlerepeat:
            shuffleTint = LPGlobalUI.THEME_LIGHT_COLOR
            loopTint = LPGlobalUI.THEME_HIGH_COLOR
        elif loopMode == LPLoopMode.shuffle:
            shuffleTint = LPGlobalUI.THEME_HIGH_COLOR
            loopTint = LPGlobalUI.THEME_LIGHT_COLOR
        elif loopMode == LPLoopMode.repeatshuffle:
            loopTint = shuffleTint = LPGlobalUI.THEME_HIGH_COLOR
        elif loopMode == LPLoopMode.default:
            loopTint = shuffleTint = LPGlobalUI.THEME_LIGHT_COLOR
        elif loopMode == LPLoopMode.singlerepeatshuffle:
            loopTint = shuffleTint = LPGlobalUI.THEME_HIGH_COLOR
        else:
            loopTint = shuffleTint = LPGlobalUI.THEME_LIGHT_COLOR
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath(loopImage), loopTint)
        hoverImage = None
        if loopTint == LPGlobalUI.THEME_HIGH_COLOR:
            hoverImage = LPUtility.tintImage(LPGlobalUI.imagePath(loopImage), LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        else:
            hoverImage = LPGlobalUI.imagePath(loopImage)
        LPButtonEventFilter(loopButton, QIcon(tintImage), QIcon(hoverImage), QIcon(hoverImage), 'image')
        if shuffleTint == LPGlobalUI.THEME_HIGH_COLOR:
            hoverImage = LPUtility.tintImage(LPGlobalUI.imagePath(shuffleImage), LPGlobalUI.THEME_HIGH_HIGH_COLOR)
        else:
            hoverImage = LPGlobalUI.imagePath(shuffleImage)
        tintImage = LPUtility.tintImage(LPGlobalUI.imagePath(shuffleImage), shuffleTint)
        LPButtonEventFilter(shuffleButton, QIcon(tintImage), QIcon(hoverImage), QIcon(hoverImage), 'image')

    updateLoopShuffleButton = staticmethod(updateLoopShuffleButton)
    
    def nextShuffleMode():
        nextMode = LPLoopMode.default
        currentMode = LPGlobalUI.currentDevice.mediaInfo.loopMode
        if currentMode == LPLoopMode.singlerepeat:
            nextMode = LPLoopMode.singlerepeatshuffle
        elif currentMode == LPLoopMode.listrepeat:
            nextMode = LPLoopMode.repeatshuffle
        elif currentMode == LPLoopMode.shuffle:
            nextMode = LPLoopMode.default
        elif currentMode == LPLoopMode.repeatshuffle:
            nextMode = LPLoopMode.listrepeat
        elif currentMode == LPLoopMode.default:
            nextMode = LPLoopMode.shuffle
        elif currentMode == LPLoopMode.singlerepeatshuffle:
            nextMode = LPLoopMode.singlerepeat
        else:
            nextMode = LPLoopMode.shuffle
        return nextMode

    nextShuffleMode = staticmethod(nextShuffleMode)
    
    def nextLoopMode():
        nextMode = LPLoopMode.default
        currentMode = LPGlobalUI.currentDevice.mediaInfo.loopMode
        if currentMode == LPLoopMode.singlerepeat:
            nextMode = LPLoopMode.default
        elif currentMode == LPLoopMode.listrepeat:
            nextMode = LPLoopMode.singlerepeat
        elif currentMode == LPLoopMode.shuffle:
            nextMode = LPLoopMode.repeatshuffle
        elif currentMode == LPLoopMode.repeatshuffle:
            nextMode = LPLoopMode.singlerepeatshuffle
        elif currentMode == LPLoopMode.default:
            nextMode = LPLoopMode.listrepeat
        elif currentMode == LPLoopMode.singlerepeatshuffle:
            nextMode = LPLoopMode.shuffle
        else:
            nextMode = LPLoopMode.shuffle
        return nextMode

    nextLoopMode = staticmethod(nextLoopMode)

