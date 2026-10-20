# Source Generated with Decompyle++
# File: __main_script__.pyc (Python 3.9)

__doc__ = '\n@Time ： 2024/11/25 16:10\n@Auth ： Chris\n@File ：main.py\n@Desc:\n'
import os
import platform
import sys
from LPClientFramework.util.LPNativeCrashHandler import install_native_crash_handler
install_native_crash_handler()
import faulthandler
from LPClientFramework.util.LPNativeCrashHandler import get_crash_dir as _get_crash_dir
_crash_faulthandler_dir = _get_crash_dir()
_crash_faulthandler_path = os.path.join(_crash_faulthandler_dir, 'crash_faulthandler.log')
_crash_faulthandler_file = open(_crash_faulthandler_path, 'a', 'utf-8', **('encoding',))
faulthandler.enable(_crash_faulthandler_file, True, **('file', 'all_threads'))
# WARNING: Decompyle incomplete
