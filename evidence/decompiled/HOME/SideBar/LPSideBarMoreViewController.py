# Source Generated with Decompyle++
# File: LPSideBarMoreViewController.pyc (Python 3.9)

'''侧边栏 More 分组控制器。'''
from string import Template
from PyQt6.QtCore import QCoreApplication, QObject
from HOME.SideBar.LPSideBarListView import LPSideBarListDelegate, LPSideBarListModel
from LPClientFramework.LPConfig.LPFontConfig import Min_Text

class LPSideBarMoreViewController(QObject):
    '''管理侧边栏 More 分组，并分发非页面导航类菜单动作。'''
    
    def __init__(self = None, mainUI = None, sendFeedbackMethod = None):
        '''初始化 More 菜单列表。

        参数:
            mainUI (Ui_MainWindow): 主窗口的 Designer UI 实例。
            sendFeedbackMethod (callable): 用户点击 Send Feedback 时的处理方法。
        返回:
            无。
        '''
        super().__init__()
        self.dataArray = [
            {
                'id': 'send_feedback',
                'icon': 'deviceDiscovery/feedback_icon.svg',
                'title': QCoreApplication.translate('SideBarMore', 'Send Feedback') }]
        self.sendFeedbackMethod = sendFeedbackMethod
        self.moreListView = mainUI.moreListView
        model = LPSideBarListModel(self.dataArray, self.moreListView)
        delegate = LPSideBarListDelegate(self.moreListView)
        self.moreListView.setModel(model)
        self.moreListView.setItemDelegate(delegate)
        self.moreListView.clicked.connect(self.itemSelect)
        self.moreTitleLabel = mainUI.moreTitleLabel
        self.moreTitleLabel.setText(QCoreApplication.translate('SideBar', 'More'))
        self.moreSectionFrame = mainUI.moreSectionFrame
        stylesheetTemplate = Template('\n                QFrame {\n                    background: transparent;\n                    border: none;\n                }\n                QLabel#moreTitleLabel {\n                    color: rgba(255, 255, 255, 0.65);\n                    font-size: ${moreTitleLabelFontSize}pt;\n                }\n            ')
        self.moreSectionFrame.setStyleSheet(stylesheetTemplate.substitute(f'''{Min_Text}''', **('moreTitleLabelFontSize',)))

    
    def itemSelect(self, index):
        '''处理 More 菜单项点击事件。

        参数:
            index (QModelIndex): 被点击列表项的模型索引。
        返回:
            无。
        '''
        if not index.isValid():
            return None
        itemData = None.dataArray[index.row()]
        if itemData['id'] == 'send_feedback' and self.sendFeedbackMethod:
            self.sendFeedbackMethod()
        self.moreListView.clearSelection()

    __classcell__ = None

