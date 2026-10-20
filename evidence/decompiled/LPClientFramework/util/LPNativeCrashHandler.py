# Source Generated with Decompyle++
# File: LPNativeCrashHandler.pyc (Python 3.9)

'''
@Time ： 2026/7/14
@Auth ： AI Assistant
@File ：LPNativeCrashHandler.py
@Desc ：跨平台原生崩溃捕获模块，提供统一入口 install_native_crash_handler()。
        Windows   : UEF + MiniDumpWriteDump 生成 .dmp
        macOS     : POSIX 信号处理器 + 依赖系统 CrashReporter 生成 .crash
        共用      : faulthandler 输出 Python traceback、qInstallMessageHandler 输出 Qt 致命日志
'''
import os
import sys
import datetime

def install_native_crash_handler():
    '''
    安装原生崩溃处理器（跨平台统一入口）。

    在 main.py 最前端调用此函数，内部按操作系统分派到对应实现。

    参数:
        无

    返回:
        无
    '''
    if sys.platform == 'win32':
        _install_win32 = _install_win32
        import LPClientFramework.util.LPNativeCrashHandler_win
        _install_win32()
    elif sys.platform == 'darwin':
        _install_darwin = _install_darwin
        import LPClientFramework.util.LPNativeCrashHandler_mac
        _install_darwin()


def get_crash_dir():
    '''
    获取崩溃文件存放目录，不存在时自动创建。

    参数:
        无

    返回:
        str: 崩溃文件目录的绝对路径。
        Windows : %APPDATA%/WiiMHome/crashes/
        macOS   : ~/Library/Logs/WiiMHome/crashes/
        Linux   : ~/.local/share/WiiMHome/crashes/
    '''
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Logs')
    else:
        base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    crash_dir = os.path.join(base, 'WiiMHome', 'crashes')
    os.makedirs(crash_dir, True, **('exist_ok',))
    return crash_dir


def generate_crash_timestamp():
    '''
    生成带时间戳的字符串，用于崩溃文件名命名。

    参数:
        无

    返回:
        str: 格式为 20260714_115230_123456（含微秒）的时间戳字符串
    '''
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')


def _write_python_traceback_simple(dump_path = (None,)):
    '''
    将 Python 各线程调用栈写入文本文件，便于快速定位问题。

    参数:
        dump_path (str, optional): 关联的 .dmp 文件路径，用于命名。
                                   为 None 时使用独立时间戳命名。

    返回:
        str 或 None: 生成的 traceback 文件路径，失败时返回 None
    '''
    pass
# WARNING: Decompyle incomplete

