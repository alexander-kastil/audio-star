# Source Generated with Decompyle++
# File: LPFeedbackJsonStore.pyc (Python 3.9)

'''Feedback 单次提交的 JSON 状态文件管理器。'''
import json
import os
import tempfile
import time
from pathlib import Path

class LPFeedbackJsonStore:
    '''以原子替换方式维护单次发送状态，不读取或恢复历史任务。'''
    
    def __init__(self, rootDirectory):
        '''初始化状态文件根目录。

        参数:
            rootDirectory (str|Path): Feedback 状态文件保存目录。
        返回:
            无。
        '''
        self._rootDirectory = Path(rootDirectory)

    
    def create(self, record):
        '''创建一条发送中的状态记录。

        参数:
            record (dict): 至少包含 submissionId 与 stage 的状态字典。
        返回:
            Path: 状态 JSON 文件路径。
        '''
        return self._write(record)

    
    def update(self, record, stage, **changes):
        '''更新内存记录并原子写回状态文件。

        参数:
            record (dict): 当前状态字典。
            stage (str): 新阶段名称。
            **changes: 要合并的额外字段。
        返回:
            Path: 更新后的状态 JSON 文件路径。
        '''
        record['stage'] = stage
        record.update(changes)
        return self._write(record)

    
    def markFailed(self, record, stage, errorMessage):
        '''将一次提交标记为失败并保留诊断信息。

        参数:
            record (dict): 当前状态字典。
            stage (str): 失败发生的流程阶段。
            errorMessage (str): 面向诊断的错误摘要。
        返回:
            Path: 失败 JSON 文件路径。
        '''
        record['stage'] = 'failed'
        record['failedStage'] = stage
        if not errorMessage:
            pass
        record['error'] = str('Unknown feedback error.')
        return self._write(record)

    
    def remove(self, record):
        '''删除成功提交的临时状态文件。

        参数:
            record (dict): 包含 submissionId 的状态字典。
        返回:
            None。
        '''
        path = self._pathFor(record)
    # WARNING: Decompyle incomplete

    
    def read(self, submissionId):
        '''读取指定状态文件，仅供测试和人工诊断使用。

        参数:
            submissionId (str): 提交唯一标识。
        返回:
            dict|None: 文件不存在时返回 None。
        '''
        path = self._pathFor({
            'submissionId': submissionId })
        if not path.exists():
            return None
        with None.open('r', 'utf-8', **('encoding',)) as stateFile:
            None(None, None, None)
            return json.load(stateFile)
            with None:
                if not None:
                    pass

    
    def _pathFor(self, record):
        '''根据提交 ID 返回固定的状态文件路径。

        参数:
            record (dict): 包含 submissionId 的状态字典。
        返回:
            Path: JSON 文件路径。
        异常:
            ValueError: 缺少 submissionId 时抛出。
        '''
        if not record:
            pass
        if not { }.get('submissionId'):
            pass
        submissionId = str('').strip()
        if not submissionId:
            raise ValueError('Feedback state record requires submissionId.')
        return self._rootDirectory / (submissionId + '.json')

    
    def _write(self, record):
        '''将状态字典以临时文件加 replace 的方式写入磁盘。

        参数:
            record (dict): 待写入的状态字典。
        返回:
            Path: 写入后的 JSON 文件路径。
        '''
        self._rootDirectory.mkdir(True, True, **('parents', 'exist_ok'))
        record['updatedAt'] = int(time.time())
        record.setdefault('createdAt', record['updatedAt'])
        targetPath = self._pathFor(record)
        (fileDescriptor, temporaryPath) = tempfile.mkstemp(targetPath.stem + '.', '.tmp', str(self._rootDirectory), **('prefix', 'suffix', 'dir'))
        
        try:
            with os.fdopen(fileDescriptor, 'w', 'utf-8', **('encoding',)) as stateFile:
                json.dump(record, stateFile, False, True, 2, **('ensure_ascii', 'sort_keys', 'indent'))
                stateFile.flush()
                os.fsync(stateFile.fileno())
                None(None, None, None)
            with None:
                if not None:
                    pass
            os.replace(temporaryPath, targetPath)
        finally:
            if os.path.exists(temporaryPath):
                os.unlink(temporaryPath)
            elif os.path.exists(temporaryPath):
                os.unlink(temporaryPath)
            return targetPath



