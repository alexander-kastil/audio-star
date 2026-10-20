# Source Generated with Decompyle++
# File: LPNativeCrashHandler_mac.pyc (Python 3.9)

'''
@Time ： 2026/7/14
@Auth ： AI Assistant
@File ：LPNativeCrashHandler_mac.py
@Desc ：macOS 平台原生崩溃处理器实现。

工作原理:
  macOS 有内置的 CrashReporter 守护进程，任何进程崩溃时系统会自动:
    1. 生成 .crash 文件到 ~/Library/Logs/DiagnosticReports/
    2. 包含所有线程调用栈、寄存器、加载的 dylib 列表
  因此本模块不需要（也不可能）自己生成 .dmp，而是:
    1. 注册 POSIX 信号处理器，崩溃时写一个 .signo 标记文件辅助定位
    2. 配合 faulthandler 输出 Python traceback
    3. 配合 qInstallMessageHandler 捕获 Qt 致命消息

  用户提交崩溃信息时，只需将:
    - DiagnosticReports 下的 .crash 文件
    - crashes/ 目录下的 .signo / .traceback.txt / qt_fatal.log
    - 业务日志
  一起打包发送即可。

捕获范围:
  - SIGSEGV (11): 访问违规（空指针/野指针/缓冲区溢出）
  - SIGBUS  (10): 总线错误（未对齐访问、mmap 失败等）
  - SIGILL  (4) : 非法指令
  - SIGFPE  (8) : 浮点异常（除零等）
  - SIGABRT (6) : abort() / qFatal() / pure virtual call

无法捕获:
  - SIGKILL (9): 外部 kill -9，不可被捕获
  - SIGTERM (15): 正常终止信号，不是崩溃
  - 系统强制退出 / 断电 / 内核恐慌
'''
import os
import sys
import signal
import datetime
_last_traceback_written = False

def _get_crash_dir():
    '''
    获取崩溃文件存放目录（~/Library/Logs/WiiMHome/crashes/）。

    参数:
        无

    返回:
        str: 崩溃目录的绝对路径
    '''
    crash_dir = os.path.expanduser('~/Library/Logs/WiiMHome/crashes')
    os.makedirs(crash_dir, True, **('exist_ok',))
    return crash_dir


def _write_signal_marker(signum):
    '''
    写一个 .signo 标记文件，记录崩溃信号编号和进程信息。

    标记文件用于:
      1. 确认崩溃信号类型（与 .crash 中的 Exception Type 交叉验证）
      2. 记录精确时间戳（.crash 文件名中的时间可能不够精确）
      3. 建立与 .traceback.txt 的时间关联

    参数:
        signum (int): 信号编号（如 11=SIGSEGV）

    返回:
        str 或 None: 标记文件路径，失败返回 None
    '''
    pass
# WARNING: Decompyle incomplete


def _write_python_traceback_mac():
    '''
    将 Python 各线程调用栈写入文本文件。

    参数:
        无

    返回:
        str 或 None: traceback 文件路径，失败返回 None
    '''
    pass
# WARNING: Decompyle incomplete


def _crash_signal_handler(signum, frame):
    '''
    macOS 通用崩溃信号处理器。

    在信号处理上下文中只能安全调用 async-signal-safe 的操作。
    这里的文件 I/O 虽然不完全满足 POSIX 严格要求，但 faulthandler
    内部采取了相同的策略，且在 macOS 上实际表现稳定。

    处理器执行完后恢复默认信号处理器，让系统 CrashReporter 接管并生成 .crash。

    参数:
        signum (int): 信号编号
        frame: 当前栈帧

    返回:
        无
    '''
    global _last_traceback_written
    if _last_traceback_written:
        signal.signal(signum, signal.SIG_DFL)
        return None
    _last_traceback_written = None
# WARNING: Decompyle incomplete


def _qt_fatal_message_handler(msg_type, context, message):
    '''
    Qt 消息处理器：保留标准输出，并在 qFatal() 调用时将上下文写入崩溃目录。

    qFatal() 之后 Qt 会调用 abort()（即 SIGABRT），因此 SIGABRT 处理器会继续执行。

    参数:
        msg_type (QtMsgType): 消息级别枚举
        context (QMessageLogContext): 消息上下文（含文件、行号、函数名）
        message (str): 致命错误的消息文本
    '''
    pass
# WARNING: Decompyle incomplete


def install_qt_fatal_handler():
    '''
    安装 Qt 的 qInstallMessageHandler，捕获 qFatal() 消息。

    需要在 QApplication 创建之后调用。

    参数:
        无

    返回:
        无
    '''
    pass
# WARNING: Decompyle incomplete


def _install_darwin():
    '''
    macOS 平台崩溃处理器的安装入口。

    注册 SIGSEGV、SIGBUS、SIGILL、SIGFPE、SIGABRT 的信号处理器。
    仅在 macOS 平台调用。

    参数:
        无

    返回:
        无
    '''
    fatal_signals = []
# WARNING: Decompyle incomplete

