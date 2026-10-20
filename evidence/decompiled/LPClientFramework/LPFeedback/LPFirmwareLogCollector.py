# Source Generated with Decompyle++
# File: LPFirmwareLogCollector.pyc (Python 3.9)

'''PC Feedback 音箱固件日志收集器。

对齐安卓 FeedbackToolsManager.downloadFirmwareLogs + FirmwareLogRequest：
多台设备并发触发 getsyslog；SSDP 在线从设备独立收集，
离线从设备由主设备触发 getsyslog:ip:<slaveIp> 并从主设备下载
/data/sys.log 原始字节到固件日志目录。
固件日志文件名对齐安卓：主设备 master-<主设备名>-<yyyyMMdd_HHmmss>.log，
从设备 slave-<主设备名>-<从设备名>-<yyyyMMdd_HHmmss>.log，并去掉名称中的空格。
'''
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from LPClientFramework.LPUtility import logger, pureUUID

class LPFirmwareLogCollector:
    '''固件日志收集器：遍历已发现音箱并下载主/从设备 sys.log。

    单台设备失败不抛出异常，collectAll 返回成功数量，
    上层可据此容忍失败而不阻断反馈主流程。
    '''
    
    def __init__(self, firmwareLogDir, maxWorkers = (30,)):
        '''初始化收集器。

        参数:
            firmwareLogDir (str|Path): 固件日志保存目录（对应安卓 LogsFirmwareDir）。
            maxWorkers (int): 并发收集任务数上限。
        返回:
            无。
        '''
        self._firmwareLogDir = Path(firmwareLogDir)
        self._maxWorkers = max(1, maxWorkers)
        self.lastDeviceTotal = 0
        self.lastDeviceSuccess = 0

    
    def _formatLogFileName(masterName, slaveName, timestamp = (None, None)):
        '''按安卓命名规则生成固件日志文件名。

        主设备为 master-<主设备名>-<yyyyMMdd_HHmmss>.log，从设备为
        slave-<主设备名>-<从设备名>-<yyyyMMdd_HHmmss>.log，
        随后去掉名称中的所有空格（对齐安卓 fileName.replace(" ", "")）。

        参数:
            masterName (str): 主设备名称。
            slaveName (str|None): 从设备名称；None 表示主设备。
            timestamp (float|None): 下载时刻时间戳；缺省取当前时间。
        返回:
            str: 固件日志文件名。
        '''
        if not timestamp:
            pass
        timestampText = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        if slaveName is None:
            if not masterName:
                pass
            fileName = 'master-%s-%s.log' % ('', timestampText)
        elif not masterName:
            pass
        if not slaveName:
            pass
        fileName = masterName % ('', '', timestampText)
        return fileName.replace(' ', '')

    _formatLogFileName = staticmethod(_formatLogFileName)
    
    def collectFromDevice(self, device, slaveIp, masterName, slaveName = (None, None, None)):
        '''从单台音箱触发打包并下载固件日志。

        主设备命令为 getsyslog，等待 3s；SSDP 在线从设备独立触发自身
        getsyslog 并等待 3s；离线从设备命令为 getsyslog:ip:<slaveIp>
        （发往主设备），等待 6s。随后从主设备 IP 下载 /data/sys.log 字节流，
        按安卓规则命名写入固件日志目录。

        参数:
            device (LPDevice): 设备实例（含 ip/uuid，用于命令通道）。
            slaveIp (str|None): 离线从设备 IP；非空时命令为 getsyslog:ip:<slaveIp>。
            masterName (str|None): 主设备名称；缺省取 device.name。
            slaveName (str|None): 从设备名称；None 表示当前设备为主设备。
        返回:
            bool: 下载并落盘成功返回 True，失败返回 False。
        '''
        if masterName is None:
            if not getattr(device, 'name', ''):
                pass
            masterName = ''
        command = 'getsyslog' if not slaveIp else 'getsyslog:ip:%s' % slaveIp
    # WARNING: Decompyle incomplete

    
    def collectAll(self, devices, maxWorkers = (None,)):
        '''并发遍历所有音箱收集固件日志，对齐安卓的并发行为。

        在线设备（含 stereo pair 在线从设备）各自独立触发 getsyslog 并下载
        自己的 /data/sys.log；离线从设备由所属主设备触发
        getsyslog:ip:<slaveIp> 并从主设备下载。不同设备并发执行，
        同组离线从设备在主设备任务内串行；失败均不阻断其他设备。

        参数:
            devices (list): LPDevice 列表（来自 LPDeviceDiscoverManager.deviceList）。
            maxWorkers (int|None): 本次并发任务数，缺省用构造参数。
        返回:
            int: 成功收集的设备数（含从设备）。
        '''
        self.lastDeviceTotal = 0
        self.lastDeviceSuccess = 0
        deviceByUuid = { }
        if not devices:
            pass
        for device in []:
            key = pureUUID(getattr(device, 'uuid', ''))
            if key:
                deviceByUuid[key] = device
                continue
                onlineUuids = set(deviceByUuid)
                tasks = []
                if not devices:
                    pass
    # WARNING: Decompyle incomplete

    
    def _collectDeviceTask(self, device, offlineSlaves, masterName, slaveName = (None,)):
