# Source Generated with Decompyle++
# File: LPMinibarQueueButton.pyc (Python 3.9)

'''
@Time ： 2025/10/16 9:33
@Auth ： Chris
@File ：LPMinibarQueueButton.py
@Desc:
'''
from PyQt6.QtWidgets import QApplication, QPushButton, QToolButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
import sys
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPMediaInfo import LPLoopMode

class LPMinibarQueueButton(QPushButton):
    
    def __init__(self = None, parent = None):
        super().__init__(parent)
        self.badge = QToolButton(self.parent())
        self.badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.badge.setFixedSize(18, 18)
        self.badge.setIconSize(self.badge.size())
        self.badge.setAutoRaise(True)
        self.badge.show()

    
    def updateBadgePosition(self):
        btn_pos = self.mapToParent(self.rect().topLeft())
        self.badge.move(btn_pos.x() + self.width() - 4, btn_pos.y() - 12)

    
    def resizeEvent(self = None, event = None):
        super().resizeEvent(event)
        self.updateBadgePosition()

    
    def setLoopMode(self, device):
        '''设置角标数字（0隐藏）'''
        loopImage = 'miniBar/repeat_icon.png'
        shuffleImage = 'miniBar/shuffle_icon.png'
        if device is None:
            self.badge.hide()
            return None
        loopMode = None.mediaInfo.loopMode
        if loopMode == LPLoopMode.default:
            self.badge.hide()
            return None
        if None == LPLoopMode.singlerepeat or loopMode == LPLoopMode.singlerepeatshuffle:
            loopImage = 'miniBar/singlerepeat_icon.png'
        if loopMode == LPLoopMode.listrepeat:
            badgeImage = loopImage
        elif loopMode == LPLoopMode.singlerepeat:
            badgeImage = loopImage
        elif loopMode == LPLoopMode.shuffle:
            badgeImage = shuffleImage
        elif loopMode == LPLoopMode.repeatshuffle:
            badgeImage = shuffleImage
        elif loopMode == LPLoopMode.singlerepeatshuffle:
            badgeImage = shuffleImage
        else:
            badgeImage = loopImage
        hoverImageIcon = QIcon(LPGlobalUI.imagePath(badgeImage))
        defaultImageIcon = QIcon(LPUtility.tintImage(LPGlobalUI.imagePath(badgeImage), LPGlobalUI.THEME_DISABLE_COLOR))
        self.badge.defaultImage = defaultImageIcon
        self.badge.hoverImage = hoverImageIcon
        if self.underMouse() and hoverImageIcon:
            self.badge.setIcon(hoverImageIcon)
        else:
            self.badge.setIcon(defaultImageIcon)
        self.badge.show()

    __classcell__ = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setFixedSize(300, 150)
    btn = LPMinibarQueueButton(window)
    btn.move(100, 60)
    window.show()
    sys.exit(app.exec())
