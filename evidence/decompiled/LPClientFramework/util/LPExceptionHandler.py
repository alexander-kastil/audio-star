# Source Generated with Decompyle++
# File: LPExceptionHandler.pyc (Python 3.9)

'''
@Time ： 2025/2/8 16:04
@Auth ： Chris
@File ：LPExceptionHandler.py
@Desc: 全局未处理异常处理器。

既把异常写入应用日志，又（若注入了 LPCrashDumper）落盘成独立 crash 文件，
供 feedback 日志包打包上传。crash 落盘器由 configureCrashDumper 在应用启动时注入。
'''
import traceback
from LPClientFramework.LPUtility import logger
_crashDumper = None

def configureCrashDumper(dumper):
    '''
    注入 LPCrashDumper 实例（应用启动时调用一次）。

    参数:
        dumper (LPCrashDumper|None): crash 落盘器实例；传 None 可关闭落盘。
    返回:
        None。
    '''
    global _crashDumper
    _crashDumper = dumper


class LPExceptionHandler:
    '''全局异常处理器（作为 sys.excepthook 使用）。'''
    
    def __init__(self):
        pass

    
    def globalHandler(exc_type, exc_value, exc_traceback):
        '''
        全局未处理异常钩子：写日志 + 落盘 crash 文件。

        参数:
            exc_type: 异常类型。
            exc_value: 异常值。
            exc_traceback: 异常 traceback。
        返回:
            None。
        '''
        errorMessage = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error('=======[Global Exception Capture] Error Occurred ======')
        logger.error(errorMessage)
    # WARNING: Decompyle incomplete

    globalHandler = staticmethod(globalHandler)

