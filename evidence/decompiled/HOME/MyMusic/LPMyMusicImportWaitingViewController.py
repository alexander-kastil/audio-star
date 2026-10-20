# Source Generated with Decompyle++
# File: LPMyMusicImportWaitingViewController.pyc (Python 3.9)

from PyQt6.QtWidgets import QWidget, QDialog, QGraphicsBlurEffect
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt6.QtGui import QPainter, QColor, QIcon
import LPGlobalUI
from HOME.LPWaitingSpinner import LPWaitingSpinner
from LPClientFramework.LPBeetsWrapper import LPBeetsWrapperImportStatus, LIBRARY_TASK_KIND_MANUAL_IMPORT, LIBRARY_TASK_KIND_STARTUP_IMPORT

class LPMyMusicImportWaitingViewController(QWidget):
    '''显示本地音乐后台任务进度与完成状态的等待弹窗。'''
    updateUISignal = pyqtSignal(object, object, object, object)
    cancelImportSignal = pyqtSignal()
    
    def __init__(self = None):
        '''
        初始化等待弹窗控制器。

        参数:
            无。
        返回:
            无。
        '''
        super(LPMyMusicImportWaitingViewController, self).__init__()
        self.loadingSpinner = None
        self.lastProgress = 0
        self.currentKind = None
        self.currentStatus = None
        self.updateUISignal.connect(self._updateUI)

    
    def setupUi(self = None, ui = None):
        '''
        初始化等待弹窗界面样式与交互。

        参数:
            ui: Qt Designer 生成的界面对象。
        返回:
            无。
        '''
        superSetup = getattr(super(), 'setupUi', None)
        if callable(superSetup):
            super().setupUi(ui)
        self.setStyleSheet('\n        QFrame#contentFrame{\n        background-color: rgba(0, 0, 0, 30)\n        }\n        ')
        self.dialogFrame.setStyleSheet('\n        QFrame#dialogFrame{\n        background-color: rgba(0, 0, 0, 255);\n        border-radius : 15;\n        border : 0px\n        }\n        ')
        self.doneButton.setStyleSheet('\nQPushButton {\ncolor: white;\nborder-radius : 13;\nborder : 0px;\nbackground-color: %s\n}\n}        ' % LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name())
        self.doneButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.doneButton.clicked.connect(self._handleDoneButtonClicked)
        self.markFinishImageView.setIcon(QIcon(LPGlobalUI.imagePath('checkmark.png')))
        self.progressBar.setStyleSheet('\n        QProgressBar {\n        width: 2px;\n        border: 1px;\n        border-width: 2px;\n        border-radius: 2px;\n        background-color: white;\n }\n        QProgressBar::chunk {\n        border-radius: 2px;\n        background-color: %s\n }\n        ' % LPGlobalUI.THEME_BUTTON_HOVER_BACK_COLOR.name())

    
    def mousePressEvent(self = None, event = None):
        '''
        点击遮罩区域时关闭等待弹窗。

        参数:
            event: 鼠标事件对象。
        返回:
            无。
        '''
        super().mousePressEvent(event)
        if not self.dialogFrame.underMouse():
            self.hide()

    
    def show(self = None):
        '''
        显示等待弹窗并重置初始视觉状态。

        参数:
            无。
        返回:
            无。
        '''
        super().show()
        self.doneFrame.hide()
        self.markFinishImageView.hide()
        self.progressFrame.hide()
        self.progressBar.setRange(0, 100)
        if self.loadingSpinner is None:
            self.loadingSpinner = LPWaitingSpinner(self.markWidget, 30, 40, 6, 50, 3, 1, 1.5, QColor(255, 255, 255), **('roundness', 'fade', 'radius', 'lines', 'line_length', 'line_width', 'speed', 'color'))
        if not self.loadingSpinner.is_spinning:
            self.loadingSpinner.show()
            self.loadingSpinner.start()

    
    def _ensureLoadingSpinnerRunning(self):
        '''
        确保等待动画处于运行状态。

        参数:
            无。
        返回:
            无。
        '''
        if self.loadingSpinner is None:
            return None
        if not None.loadingSpinner.is_spinning:
            self.loadingSpinner.show()
            self.loadingSpinner.start()

    
    def _handleDoneButtonClicked(self):
        '''
        根据当前状态处理等待弹窗底部按钮点击。

        参数:
            无。
        返回:
            无。
        '''
        if self.currentStatus in (LPBeetsWrapperImportStatus.preparing, LPBeetsWrapperImportStatus.importing) and self.currentKind == LIBRARY_TASK_KIND_MANUAL_IMPORT:
            self.cancelImportSignal.emit()
            return None
        None.hide()

    
    def _noteTextForKind(self, kind, status, total, processed):
        '''
        根据任务类型与阶段生成等待弹窗文案。

        参数:
            kind (str): 任务类型。
            status (LPBeetsWrapperImportStatus): 当前阶段状态。
            total (int): 总文件数。
            processed (int): 已处理文件数。
        返回:
            str: 展示文案。
        '''
        if kind == LIBRARY_TASK_KIND_MANUAL_IMPORT and status == LPBeetsWrapperImportStatus.preparing:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Adding music to library: Preparing...')
        if None == LIBRARY_TASK_KIND_MANUAL_IMPORT and status == LPBeetsWrapperImportStatus.importing:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Adding music to library: Of %d tracks, %d added') % (total, processed)
        if None == LIBRARY_TASK_KIND_MANUAL_IMPORT and status == LPBeetsWrapperImportStatus.cancelling:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Canceling import: Of %d tracks, %d added') % (total, processed)
        if None == LIBRARY_TASK_KIND_MANUAL_IMPORT and status == LPBeetsWrapperImportStatus.canceled:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Import canceled: Of %d tracks, %d remain in library') % (total, processed)
        if None == LIBRARY_TASK_KIND_STARTUP_IMPORT and status == LPBeetsWrapperImportStatus.preparing:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Updating music library: Preparing...')
        if None == LIBRARY_TASK_KIND_STARTUP_IMPORT and status == LPBeetsWrapperImportStatus.importing:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Updating music library: Of %d tracks, %d added') % (total, processed)
        if None == LIBRARY_TASK_KIND_STARTUP_IMPORT:
            return QCoreApplication.translate('MyMusicImportWaiting', 'Music library update: Complete')
        return None.translate('MyMusicImportWaiting', 'Adding music to library: Complete')

    
    def _updateUI(self, kind, status, total, processed):
        '''
        刷新等待弹窗内容。

        参数:
            kind (str): 任务类型。
            status (LPBeetsWrapperImportStatus): 当前阶段状态。
            total (int): 总文件数。
            processed (int): 已处理文件数。
        返回:
            无。
        '''
        self.currentKind = kind
        self.currentStatus = status
        self.noteLabel.setText(self._noteTextForKind(kind, status, total, processed))
        if status == LPBeetsWrapperImportStatus.preparing:
            self._ensureLoadingSpinnerRunning()
            self.doneFrame.show()
            self.doneButton.setText(QCoreApplication.translate('MyMusicImportWaiting', 'Cancel' if kind == LIBRARY_TASK_KIND_MANUAL_IMPORT else 'Close'))
            self.doneButton.setEnabled(True)
            self.progressFrame.hide()
            self.markFinishImageView.hide()
            self.lastProgress = 0
            self.progressBar.setValue(0)
        elif status == LPBeetsWrapperImportStatus.importing:
            self._ensureLoadingSpinnerRunning()
            self.doneFrame.show()
            self.doneButton.setText(QCoreApplication.translate('MyMusicImportWaiting', 'Cancel' if kind == LIBRARY_TASK_KIND_MANUAL_IMPORT else 'Close'))
            self.doneButton.setEnabled(True)
            self.progressFrame.show()
            self.markFinishImageView.hide()
            if total > 0 and processed != self.lastProgress:
                progress = int((processed / total) * 100)
                self.progressBar.setValue(max(0, min(100, progress)))
                self.lastProgress = processed
            elif status == LPBeetsWrapperImportStatus.cancelling:
                self._ensureLoadingSpinnerRunning()
                self.doneFrame.show()
                self.doneButton.setText(QCoreApplication.translate('MyMusicImportWaiting', 'Cancel'))
                self.doneButton.setEnabled(False)
                self.progressFrame.show()
                self.markFinishImageView.hide()
                if total > 0:
                    progress = int((processed / total) * 100)
                    self.progressBar.setValue(max(0, min(100, progress)))
                    self.lastProgress = processed
                else:
                    self.doneFrame.show()
                    self.doneButton.setText(QCoreApplication.translate('MyMusicImportWaiting', 'Done'))
                    self.doneButton.setEnabled(True)
                    self.progressFrame.hide()
                    self.markFinishImageView.setVisible(status == LPBeetsWrapperImportStatus.finish)
                    if self.loadingSpinner and self.loadingSpinner.is_spinning:
                        self.loadingSpinner.stop()
                        self.loadingSpinner.hide()

    
    def updateDialogUI(self, kind, status, total, processed):
        '''
        从外部线程安全地提交等待弹窗状态更新。

        参数:
            kind (str): 任务类型。
            status (LPBeetsWrapperImportStatus): 当前阶段状态。
            total (int): 总文件数。
            processed (int): 已处理文件数。
        返回:
            无。
        '''
        self.updateUISignal.emit(kind, status, total, processed)

    __classcell__ = None

