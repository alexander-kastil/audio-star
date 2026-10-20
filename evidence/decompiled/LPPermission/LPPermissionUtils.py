# Source Generated with Decompyle++
# File: LPPermissionUtils.pyc (Python 3.9)

'''
@Time ： 2024/12/25 13:32
@Auth ： Chris
@File ：LPPermissionUtils.py
@Desc:
'''
import os
from LPClientFramework.LPUtility import logger

class LPPermissionUtils:
    
    def __init__(self):
        pass

    
    def check_access_permission(dir_path):
        if not os.access(dir_path, os.R_OK):
            logger.warning(f'''LPPermissionUtils check_access_permission reject dir：{dir_path}''')
            return False

    check_access_permission = staticmethod(check_access_permission)

