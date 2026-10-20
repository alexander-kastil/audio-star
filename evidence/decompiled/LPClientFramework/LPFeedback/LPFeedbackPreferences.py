# Source Generated with Decompyle++
# File: LPFeedbackPreferences.pyc (Python 3.9)

'''Feedback 用户偏好的本地持久化封装。'''

class LPFeedbackPreferences:
    '''使用应用设置存储 Feedback 表单中需要跨会话保留的字段。'''
    _EMAIL_KEY = 'feedback/email'
    
    def __init__(self, settingsStore):
        '''初始化 Feedback 偏好存储。

        参数:
            settingsStore (QSettings): 应用级设置存储对象。
        返回:
            无。
        '''
        self._settingsStore = settingsStore

    
    def loadEmail(self):
        '''读取上一次成功提交 Feedback 时保存的邮箱。

        参数:
            无。
        返回:
            str: 已保存并去除首尾空白的邮箱；不存在时返回空字符串。
        '''
        email = self._settingsStore.value(self._EMAIL_KEY, '')
        if not email:
            pass
        return str('').strip()

    
    def saveEmail(self, email):
        '''保存一次成功提交 Feedback 所使用的邮箱。

        参数:
            email (str): 待保存的用户邮箱。
        返回:
            str: 实际保存并去除首尾空白的邮箱；空值不会覆盖已有邮箱。
        '''
        if not email:
            pass
        normalizedEmail = str('').strip()
        if not normalizedEmail:
            return self.loadEmail()
        None._settingsStore.setValue(self._EMAIL_KEY, normalizedEmail)
        syncMethod = getattr(self._settingsStore, 'sync', None)
        if callable(syncMethod):
            syncMethod()
        return normalizedEmail


