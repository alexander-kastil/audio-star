# Source Generated with Decompyle++
# File: LPNativeCrashHandler_win.pyc (Python 3.9)

'''
@Time ： 2026/7/14
@Auth ： AI Assistant
@File ：LPNativeCrashHandler_win.py
@Desc ：Windows 平台原生崩溃处理器实现。

工作原理:
  1. 通过 kernel32.SetUnhandledExceptionFilter 注册顶层未处理异常过滤器，
     只在 SEH 异常最终无人处理、进程即将退出时获得通知。
  2. 回调中调用 dbghelp.MiniDumpWriteDump 生成 .dmp 小型转储。
  3. 同时调用 faulthandler.dump_traceback 输出 Python 线程栈帧。
  4. 注册 SIGABRT 信号处理器，用于捕获 abort() / qFatal() 场景。

捕获范围:
  - Access Violation (c0000005): 空指针/野指针/缓冲区溢出
  - Stack Overflow  (c00000fd): 无限递归（C 层）
  - Integer Division by Zero (c0000094)
  - Illegal Instruction (c000001d)
  - abort() / qFatal() / pure virtual call → SIGABRT

无法捕获:
  - 已被应用或第三方库处理的第一机会异常
  - TerminateProcess() 直接杀进程
  - 外部 kill / 任务管理器结束进程
  - 系统蓝屏 / 断电 / OOM
'''
import ctypes
from ctypes import wintypes
import os
import sys
import signal
import datetime
MiniDumpNormal = 0
EXCEPTION_CONTINUE_SEARCH = 0
_CALLBACK_FACTORY = getattr(ctypes, 'WINFUNCTYPE', ctypes.CFUNCTYPE)
_TOP_LEVEL_EXCEPTION_FILTER_TYPE = _CALLBACK_FACTORY(wintypes.LONG, ctypes.c_void_p)

class _MINIDUMP_EXCEPTION_INFORMATION(ctypes.Structure):
    '''描述 MiniDumpWriteDump 所需异常上下文。'''
    _fields_ = [
        ('ThreadId', wintypes.DWORD),
        ('ExceptionPointers', ctypes.c_void_p),
        ('ClientPointers', wintypes.BOOL)]

_kernel32 = None
_dbghelp = None
_previous_unhandled_filter_ref = None
_unhandled_filter_installed = False
_dump_in_progress = False

def _configure_winapi(kernel32, dbghelp):
    '''为崩溃处理所用 WinAPI 声明准确的 ctypes 签名。

    参数:
        kernel32: 已加载的 kernel32 WinDLL。
        dbghelp: 已加载的 dbghelp WinDLL。

    返回:
        无
    '''
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.GetCurrentProcessId.argtypes = []
    kernel32.GetCurrentProcessId.restype = wintypes.DWORD
    kernel32.GetCurrentThreadId.argtypes = []
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    kernel32.SetUnhandledExceptionFilter.argtypes = [
        _TOP_LEVEL_EXCEPTION_FILTER_TYPE]
    kernel32.SetUnhandledExceptionFilter.restype = ctypes.c_void_p
    kernel32.OutputDebugStringW.argtypes = [
        wintypes.LPCWSTR]
    kernel32.OutputDebugStringW.restype = None
    dbghelp.MiniDumpWriteDump.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.HANDLE,
        wintypes.DWORD,
        ctypes.POINTER(_MINIDUMP_EXCEPTION_INFORMATION),
        ctypes.c_void_p,
        ctypes.c_void_p]
    dbghelp.MiniDumpWriteDump.restype = wintypes.BOOL


def _get_winapi():
    '''按需加载并配置 Windows 崩溃处理 API。

    参数:
        无

    返回:
        tuple: kernel32 和 dbghelp WinDLL。
    '''
    global _kernel32, _dbghelp
    if _kernel32 is None or _dbghelp is None:
        _kernel32 = ctypes.WinDLL('kernel32', True, **('use_last_error',))
        _dbghelp = ctypes.WinDLL('dbghelp', True, **('use_last_error',))
        _configure_winapi(_kernel32, _dbghelp)
    return (_kernel32, _dbghelp)


def _get_native_file_handle(dump_file):
    '''把 Python 文件对象的 CRT 描述符转换为 Windows HANDLE。

    参数:
        dump_file: 以二进制写模式打开的 Python 文件对象。

    返回:
        int: Windows 原生文件句柄。
    '''
    import msvcrt
    return msvcrt.get_osfhandle(dump_file.fileno())


def _get_last_error():
    '''获取最近一次 WinAPI 调用保存的错误码。

    参数:
        无

    返回:
        int: Windows 错误码或 HRESULT。
    '''
    return ctypes.get_last_error()


def _format_windows_error(error_code):
    '''把有符号错误值格式化为可诊断的 HRESULT/Win32 信息。

    �