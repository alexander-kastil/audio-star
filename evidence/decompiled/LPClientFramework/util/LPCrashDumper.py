# Source Generated with Decompyle++
# File: LPCrashDumper.pyc (Python 3.9)

'''
Crash 日志落盘工具。

对应 Android lib-log 的 CrashHandler：捕获到未处理异常时，把异常堆栈 + 系统/应用环境信息
写到独立的 crash 文件，并按保留天数滚动清理，供后续随日志包一起加密上传。

设计要点：
- 仅依赖标准库（platform/json/os/datetime/traceback/logging），不导入 LPUtility，
  便于在无 PyQt6 环境下单元测试。
- crash 目录、应用版本等由构造参数注入；正式使用时由调用方传入 cacheDir/"crash" 等。
'''
import json
import logging
import os
import platform
import traceback
from datetime import datetime, timedelta
logger = logging.getLogger('linkplay')
CRASH_LOG_SAVE_DAYS = 7

class LPCrashDumper:
    '''Crash 落盘器：把异常与运行环境写成 JSON 文件并滚动清理。'''
    
    def __init__(self, crashDir, appVersion, bundleId, extraEnvProvider = (None, None, None)):
        '''
        初始化落盘器。

        参数:
            crashDir (str): crash 文件存放目录（不存在会自动创建）。
            appVersion (str|None): 应用版本（注入，避免依赖 LPUtility）。
            bundleId (str|None): 应用包标识。
            extraEnvProvider (callable|None): 返回额外环境字段的回调，dump 时延迟调用。
        '''
        self._crashDir = str(crashDir)
        self._appVersion = appVersion
        self._bundleId = bundleId
        self._extraEnvProvider = extraEnvProvider
        os.makedirs(self._crashDir, True, **('exist_ok',))

    
    def dump(self, excType, excValue, excTraceback):
        '''
        写入一份 crash 报告并滚动清理旧文件。

        参数:
            excType: 异常类型。
            excValue: 异常值。
            excTraceback: 异常 traceback。
        返回:
            str|None: 写入的文件路径；失败时返回 None。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def _buildReport(self, excType, excValue, excTraceback, now):
        '''
        构造 crash 报告字典（纯逻辑，便于单测）。

        参数:
            excType: 异常类型。
            excValue: 异常值。
            excTraceback: 异常 traceback。
            now (datetime): 当前时间。
        返回:
            dict: crash 报告。
        '''
        report = {
            'crashTime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'exceptionType': getattr(excType, '__name__', str(excType)),
            'exceptionValue': str(excValue),
            'traceback': ''.join(traceback.format_exception(excType, excValue, excTraceback)),
            'environment': self._collectEnvironment() }
    # WARNING: Decompyle incomplete

    
    def _collectEnvironment(self):
        '''
        采集系统/应用环境信息（对应 Android 反射 dump Build.*）。

        返回:
            dict: 环境信息。
        '''
        return {
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'pythonVersion': platform.python_version(),
            'system': platform.system(),
            'release': platform.release(),
            'appVersion': self._appVersion,
            'bundleId': self._bundleId }

    
    def _pruneOldFiles(self, now):
        '''
        删除超过保留天数的 crash 文件。

        参数:
            now (datetime): 当前时间，用于计算截止点。
        '''
        cutoff = now - timedelta(CRASH_LOG_SAVE_DAYS, **('days',))
        cutoffSec = cutoff.timestamp()
    # WARNING: Decompyle incomplete


