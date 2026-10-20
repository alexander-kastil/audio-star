# Source Generated with Decompyle++
# File: LPFeedbackDraftStore.pyc (Python 3.9)

'''Feedback 填写中草稿的跨会话持久化封装。'''
import hashlib
import os
import shutil
import time
from pathlib import Path

class LPFeedbackDraftStore:
    '''保存反馈弹窗未提交的填写草稿，并维护附件图片副本。

    草稿包含主题/邮箱/描述文本与已选附件（图片副本路径列表）。
    任意关闭方式不清除草稿，下次打开弹窗可恢复；只有提交成功或用户主动清除时才删除。
    附件图片在选图时复制到缓存目录 feedback_draft_attachments 下，
    避免用户移动/删除原图后草稿恢复时引用失效。
    '''
    _SUBJECT_KEY = 'feedback/draft/subject'
    _EMAIL_KEY = 'feedback/draft/email'
    _DESCRIPTION_KEY = 'feedback/draft/description'
    _ATTACHMENT_PATHS_KEY = 'feedback/draft/attachmentPaths'
    _UPDATED_AT_KEY = 'feedback/draft/updatedAt'
    _KEYS = (_SUBJECT_KEY, _EMAIL_KEY, _DESCRIPTION_KEY, _ATTACHMENT_PATHS_KEY, _UPDATED_AT_KEY)
    
    def __init__(self, settingsStore, attachmentCacheDir):
        '''初始化草稿存储。

        参数:
            settingsStore (object): 应用设置存储（QSettings 或兼容替身），提供
                value/setValue/remove/sync 方法。
            attachmentCacheDir (str|Path): 附件图片副本缓存目录。
        返回:
            无。
        '''
        self._settingsStore = settingsStore
        self._attachmentCacheDir = Path(attachmentCacheDir)

    
    def save(self, subject, email, description, attachmentPaths):
        '''保存一份草稿；三个文本全空且无附件时视为无效草稿并清除。

        参数:
            subject (str): 反馈主题。
            email (str): 用户邮箱。
            description (str): 问题描述。
            attachmentPaths (list[str]): 已选附件（图片副本）路径列表。
        返回:
            None。
        '''
        if not attachmentPaths:
            pass
        normalizedPaths = (lambda .0: [ str(path) for path in .0 if path ])([])
        hasText = any((lambda .0: for value in .0:
if not value:
passstr('').strip())((subject, email, description)))
        if not hasText and normalizedPaths:
            self.clear()
            return None
        if not subject:
            pass
        None._settingsStore.setValue(self._SUBJECT_KEY, str(''))
        if not email:
            pass
        self._settingsStore.setValue(self._EMAIL_KEY, str(''))
        if not description:
            pass
        self._settingsStore.setValue(self._DESCRIPTION_KEY, str(''))
        self._settingsStore.setValue(self._ATTACHMENT_PATHS_KEY, normalizedPaths)
        self._settingsStore.setValue(self._UPDATED_AT_KEY, int(time.time()))
        syncMethod = getattr(self._settingsStore, 'sync', None)
        if callable(syncMethod):
            syncMethod()

    
    def load(self):
        '''读取草稿；不存在或内容无效（全空且无附件）时返回 None。

        参数:
            无。
        返回:
            dict|None: 包含 subject/email/description/attachmentPaths/updatedAt
                的草稿字典；无有效草稿时返回 None。
        '''
        if not self._settingsStore.value(self._SUBJECT_KEY, ''):
            pass
        subject = str('')
        if not self._settingsStore.value(self._EMAIL_KEY, ''):
            pass
        email = str('')
        if not self._settingsStore.value(self._DESCRIPTION_KEY, ''):
            pass
        description = str('')
        if not self._settingsStore.value(self._ATTACHMENT_PATHS_KEY, []):
            pass
        attachmentPaths = list([])
        if not self._settingsStore.value(self._UPDATED_AT_KEY, 0):
            pass
        updatedAt = int(0)
        if not any((lambda .0: for value in .0:
value.strip())((subject, email, description))) and attachmentPaths:
            return None
        if not None:
            return None
        return {
            'subject': None,
            'email': email,
            'description': description,
            'attachmentPaths': attachmentPaths,
            'updatedAt': updatedAt }

    
    def clear(self):
        '''删除草稿元数据与全部附件图片副本（含副本目录）。'''
        if not self._settingsStore.value(self._ATTACHMENT_PATHS_KEY, []):
            pass
        attachmentPaths = list([])
    # WARNING: Decompyle incomplete

    
    def copyAttachment(self, srcPath):
        '''把图片复制到草稿缓存目录，返回副本路径。

        副本文件名由源文件真实路径哈希决定：同一张图多次选择返回同一副本路径，
        便于附件去重；复制失败时返回 None（由调用方决定回退策略）。

        参数:
            srcPath (str): 源图片文件路径。
        返回:
            str|None: 副本路径；复制失败时返回 None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def removeAttachment(self, cachedPath):
        '''删除单个附件图片副本文件（文件不存在时静默忽略）。

        参数:
            cachedPath (str): 附件副本路径。
        返回:
            None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def cleanupExpired(cls, settingsStore, attachmentCacheDir, maxAgeDays = (7,)):
        '''清理超过 maxAgeDays 天未更新的草稿及其附件图片副本。

        在应用启动时调用；过期草稿连同副本文件与元数据一并删除，
        未过期或不存在草稿时不作任何处理。

        参数:
            settingsStore (object): 应用设置存储（QSettings 或兼容替身）。
            attachmentCacheDir (str|Path): 附件图片副本缓存目录。
            maxAgeDays (int): 草稿最大保留天数。
        返回:
            None。
        '''
        if not settingsStore.value(cls._UPDATED_AT_KEY, 0):
            pass
        updatedAt = int(0)
        if not updatedAt:
            return None
        if None(time.time()) - updatedAt <= int(maxAgeDays) * 86400:
            return None
        if not settingsStore.value(cls._ATTACHMENT_PATHS_KEY, []):
            pass
        attachmentPaths = None([])
    # WARNING: Decompyle incomplete

    cleanupExpired = classmethod(cleanupExpired)

