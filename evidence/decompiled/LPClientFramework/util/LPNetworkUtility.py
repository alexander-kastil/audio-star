# Source Generated with Decompyle++
# File: LPNetworkUtility.pyc (Python 3.9)

'''网络工具模块：集中承载网络信息读取、SSID/BSSID 获取与连通性探测。

本模块由 `LPClientFramework/LPUtility.py` 拆分而来，职责包括：

- 物理局域网信息（网关 / 接口名 / 子网掩码 / 本机 IP）读取；
- 网络接口类型判定（wifi / eth）；
- 当前 Wi-Fi 的 SSID、BSSID 读取（Windows 走 WLAN API，macOS 多方案 fallback）；
- 设备发现诊断用的 ICMP / TCP 连通性探测；
- 对外网连通性判断。

约束：

- 只依赖标准库与 psutil，不导入 `LPUtility` / `LPGlobalUI`，避免循环导入；
- 对外统一由 `LPUtility` 提供转发调用方法，调用方不必直接依赖本模块；
- 日志使用与 `LPUtility` 相同的 "linkplay" logger，命名的 handler 与级别由 `LPUtility` 统一配置。
'''
import ctypes
import ipaddress
import locale
import logging
import os
import plistlib
import platform
import re
import socket
import subprocess
import time
from ctypes import wintypes
import psutil
logger = logging.getLogger('linkplay')
_SUBPROCESS_CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
_SUBPROCESS_TIMEOUT = 5
_MAX_UID_DEREF_HOPS = 32
AF_INET = socket.AF_INET
ERROR_BUFFER_OVERFLOW = 111
ERROR_NO_DATA = 232
GAA_FLAG_SKIP_ANYCAST = 2
GAA_FLAG_SKIP_MULTICAST = 4
GAA_FLAG_SKIP_DNS_SERVER = 8
GAA_FLAG_INCLUDE_GATEWAYS = 128
_MAX_ADAPTERS_BUFFER_RETRY = 5
IF_TYPE_ETHERNET_CSMACD = 6
IF_TYPE_IEEE80211 = 71
IF_OPER_STATUS_UP = 1
IP_ADAPTER_NO_MULTICAST = 16
WLAN_CLIENT_VERSION = 2
WLAN_INTERFACE_STATE_CONNECTED = 1
WLAN_INTF_OPCODE_CURRENT_CONNECTION = 7
WINDOWS_ERROR_INVALID_PARAMETER = 87

class SOCKADDR_IN(ctypes.Structure):
    _fields_ = [
        ('sin_family', wintypes.USHORT),
        ('sin_port', wintypes.USHORT),
        ('sin_addr', ctypes.c_ubyte * 4),
        ('sin_zero', ctypes.c_ubyte * 8)]


class SOCKET_ADDRESS(ctypes.Structure):
    _fields_ = [
        ('lpSockaddr', ctypes.c_void_p),
        ('iSockaddrLength', ctypes.c_int)]


class IP_ADAPTER_UNICAST_ADDRESS(ctypes.Structure):
    pass

IP_ADAPTER_UNICAST_ADDRESS._fields_ = [
    ('Length', wintypes.ULONG),
    ('Flags', wintypes.DWORD),
    ('Next', ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ('Address', SOCKET_ADDRESS),
    ('PrefixOrigin', ctypes.c_int),
    ('SuffixOrigin', ctypes.c_int),
    ('DadState', ctypes.c_int),
    ('ValidLifetime', wintypes.ULONG),
    ('PreferredLifetime', wintypes.ULONG),
    ('LeaseLifetime', wintypes.ULONG),
    ('OnLinkPrefixLength', ctypes.c_ubyte)]

class IP_ADAPTER_GATEWAY_ADDRESS(ctypes.Structure):
    pass

IP_ADAPTER_GATEWAY_ADDRESS._fields_ = [
    ('Length', wintypes.ULONG),
    ('Reserved', wintypes.DWORD),
    ('Next', ctypes.POINTER(IP_ADAPTER_GATEWAY_ADDRESS)),
    ('Address', SOCKET_ADDRESS)]

class IP_ADAPTER_ADDRESSES(ctypes.Structure):
    pass

IP_ADAPTER_ADDRESSES._fields_ = [
    ('Length', wintypes.ULONG),
    ('IfIndex', wintypes.DWORD),
    ('Next', ctypes.POINTER(IP_ADAPTER_ADDRESSES)),
    ('AdapterName', ctypes.c_char_p),
    ('FirstUnicastAddress', ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ('FirstAnycastAddress', ctypes.c_void_p),
    ('FirstMulticastAddress', ctypes.c_void_p),
    ('FirstDnsServerAddress', ctypes.c_void_p),
    ('DnsSuffix', wintypes.LPWSTR),
    ('Description', wintypes.LPWSTR),
    ('FriendlyName', wintypes.LPWSTR),
    ('PhysicalAddress', ctypes.c_ubyte * 8),
    ('PhysicalAddressLength', wintypes.DWORD),
    ('Flags', wintypes.DWORD),
    ('Mtu', wintypes.DWORD),
    ('IfType', wintypes.DWORD),
    ('OperStatus', ctypes.c_int),
    ('Ipv6IfIndex', wintypes.DWORD),
    ('ZoneIndices', wintypes.DWORD * 16),
    ('FirstPrefix', ctypes.c_void_p),
    ('TransmitLinkSpeed', ctypes.c_uint64),
    ('ReceiveLinkSpeed', ctypes.c_uint64),
    ('FirstWinsServerAddress', ctypes.c_void_p),
    ('FirstGatewayAddress', ctypes.POINTER(IP_ADAPTER_GATEWAY_ADDRESS))]

class WLAN_INTERFACE_GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', ctypes.c_ubyte * 8)]


class WLAN_INTERFACE_INFO(ctypes.Structure):
    _fields_ = [
        ('InterfaceGuid', WLAN_INTERFACE_GUID),
        ('strInterfaceDescription', wintypes.WCHAR * 256),
        ('isState', wintypes.DWORD)]


class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
    _fields_ = [
        ('dwNumberOfItems', wintypes.DWORD),
        ('dwIndex', wintypes.DWORD),
        ('InterfaceInfo', WLAN_INTERFACE_INFO * 1)]


class DOT11_SSID(ctypes.Structure):
    _fields_ = [
        ('uSSIDLength', wintypes.ULONG),
        ('ucSSID', ctypes.c_ubyte * 32)]


class WLAN_ASSOCIATION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('dot11Ssid', DOT11_SSID),
        ('dot11BssType', wintypes.DWORD),
        ('dot11Bssid', ctypes.c_ubyte * 6),
        ('dot11PhyType', wintypes.DWORD),
        ('uDot11PhyIndex', wintypes.ULONG),
        ('wlanSignalQuality', wintypes.ULONG),
        ('ulRxRate', wintypes.ULONG),
        ('ulTxRate', wintypes.ULONG)]


class WLAN_SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('bSecurityEnabled', wintypes.BOOL),
        ('bOneXEnabled', wintypes.BOOL),
        ('dot11AuthAlgorithm', wintypes.DWORD),
        ('dot11CipherAlgorithm', wintypes.DWORD)]


class WLAN_CONNECTION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('isState', wintypes.DWORD),
        ('wlanConnectionMode', wintypes.DWORD),
        ('strProfileName', wintypes.WCHAR * 256),
        ('wlanAssociationAttributes', WLAN_ASSOCIATION_ATTRIBUTES),
        ('wlanSecurityAttributes', WLAN_SECURITY_ATTRIBUTES)]


class LPWindowsNetworkInfoReader:
    '''通过 GetAdaptersAddresses 读取物理局域网配置（VPN 场景下不落到虚拟网卡）。'''
    
    def _ipv4FromSocketAddress(address):
        '''把 Windows 原生 socket 地址转换为 IPv4 字符串。

        参数:
            address (SOCKET_ADDRESS): Windows 原生 socket 地址。
        返回:
            str | None: 有效的 IPv4 地址；地址无效时返回 None。
        '''
        if address.lpSockaddr or address.iSockaddrLength < ctypes.sizeof(SOCKADDR_IN):
            return None
        sockaddr = None.cast(address.lpSockaddr, ctypes.POINTER(SOCKADDR_IN)).contents
        if sockaddr.sin_family != AF_INET:
            return None
        return None.inet_ntoa(bytes(sockaddr.sin_addr))

    _ipv4FromSocketAddress = staticmethod(_ipv4FromSocketAddress)
    
    def _firstIPv4Unicast(cls, adapter):
        '''读取适配器的首个可用 IPv4 单播地址。

        参数:
            adapter (IP_ADAPTER_ADDRESSES): Windows 网络适配器。
        返回:
            tuple[str, int] | None: 本机 IP 与前缀长度；不存在时返回 None。
        '''
        current = adapter.FirstUnicastAddress
        if current:
            item = current.contents
            localIP = cls._ipv4FromSocketAddress(item.Address)
            if localIP and localIP != '0.0.0.0':
                return (localIP, int(item.OnLinkPrefixLength))
            current = None.Next
            continue

    _firstIPv4Unicast = classmethod(_firstIPv4Unicast)
    
    def _firstIPv4Gateway(cls, adapter):
        '''读取适配器的首个有效 IPv4 网关。

        参数:
            adapter (IP_ADAPTER_ADDRESSES): Windows 网络适配器。
        返回:
            str | None: IPv4 网关；不存在时返回 None。
        '''
        current = adapter.FirstGatewayAddress
        if current:
            item = current.contents
            gateway = cls._ipv4FromSocketAddress(item.Address)
            if gateway and gateway != '0.0.0.0':
                return gateway
            current = None.Next
            continue

    _firstIPv4Gateway = classmethod(_firstIPv4Gateway)
    
    def _prefixToNetmask(prefixLength):
        '''把 IPv4 前缀长度转换为点分十进制子网掩码。

        参数:
            prefixLength (int): 0 到 32 的 IPv4 前缀长度。
        返回:
            str: 点分十进制子网掩码。
        '''
        maskValue = 0xFFFFFFFF << 32 - prefixLength & 0xFFFFFFFF if prefixLength else 0
        return socket.inet_ntoa(maskValue.to_bytes(4, 'big'))

    _prefixToNetmask = staticmethod(_prefixToNetmask)
    
    def fetch(cls):
        '''通过 Windows IP Helper API 获取物理局域网信息。

        参数:
            无。
        返回:
            dict | None: 同一物理网卡的网络信息；没有合适网卡时返回 None。
        '''
        getAdaptersAddresses = ctypes.windll.iphlpapi.GetAdaptersAddresses
        getAdaptersAddresses.argtypes = [
            wintypes.ULONG,
            wintypes.ULONG,
            ctypes.c_void_p,
            ctypes.POINTER(IP_ADAPTER_ADDRESSES),
            ctypes.POINTER(wintypes.ULONG)]
        getAdaptersAddresses.restype = wintypes.ULONG
        flags = GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER | GAA_FLAG_INCLUDE_GATEWAYS
        bufferSize = wintypes.ULONG(15360)
        buffer = None
        adapters = None
        result = 0
        for _ in range(_MAX_ADAPTERS_BUFFER_RETRY):
            buffer = ctypes.create_string_buffer(bufferSize.value)
            adapters = ctypes.cast(buffer, ctypes.POINTER(IP_ADAPTER_ADDRESSES))
            result = getAdaptersAddresses(AF_INET, flags, None, adapters, ctypes.byref(bufferSize))
            if result != ERROR_BUFFER_OVERFLOW:
                pass
            
            logger.warning('[win] GetAdaptersAddresses buffer overflow retry exhausted')
            raise ctypes.WinError(result)
            if result == ERROR_NO_DATA:
                _windowsSelectedAdapter['interface'] = ''
                _windowsSelectedAdapter['ifType'] = 0
                return None
            if None != 0:
                raise ctypes.WinError(result)
            candidates = []
            current = adapters
            if current:
                adapter = current.contents
                address = cls._firstIPv4Unicast(adapter)
                gateway = cls._firstIPv4Gateway(adapter)
                if adapter.OperStatus == IF_OPER_STATUS_UP and adapter.IfType in (IF_TYPE_ETHERNET_CSMACD, IF_TYPE_IEEE80211) and adapter.Flags & IP_ADAPTER_NO_MULTICAST and address and gateway:
                    (localIP, prefixLength) = address
                    if not adapter.FriendlyName and adapter.Description:
                        pass
                    candidates.append({
                        'gateway': gateway,
                        'interface': '',
                        'netmask': cls._prefixToNetmask(prefixLength),
                        'localIP': localIP,
                        'ifIndex': int(adapter.IfIndex),
                        'ifType': int(adapter.IfType) })
                current = adapter.Next
                continue
        if not candidates:
            _windowsSelectedAdapter['interface'] = ''
            _windowsSelectedAdapter['ifType'] = 0
            return None
        None.sort((lambda item: (item['ifType'] != IF_TYPE_IEEE80211, item['ifIndex'])), **('key',))
        selected = candidates[0]
        _windowsSelectedAdapter['interface'] = selected['interface']
        _windowsSelectedAdapter['ifType'] = selected['ifType']
        networkInfo = dict(selected)
        networkInfo.pop('ifIndex')
        networkInfo.pop('ifType')
        return networkInfo

    fetch = classmethod(fetch)

_windowsSelectedAdapter = {
    'interface': '',
    'ifType': 0 }
_wlanapiCache = {
    'loaded': False,
    'dll': None }

def _loadWlanApi():
    '''惰性加载 wlanapi.dll 并声明所用函数签名。

    仅在 Windows 上可用；不引入第三方依赖（wlanapi.dll 为系统自带组件），
    也不参与 PyInstaller 静态分析，因此无需修改打包配置。

    加载结果先写入局部变量、最后一次性发布到缓存：早期实现先置 loaded=True 再赋值 dll，
    并发调用（主线程与设备发现监控线程都会读 SSID）会在该窗口期拿到 loaded 为真但
    dll 为 None 的结果，从而误判 WLAN API 不可用并回退慢速 netsh。

    参数:
        无。
    返回:
        ctypes.WinDLL | None: 可用的 wlanapi 句柄；非 Windows 或系统缺少该 DLL 时返回 None。
    '''
    if _wlanapiCache['loaded']:
        return _wlanapiCache['dll']
    if None.system() != 'Windows':
        _wlanapiCache['dll'] = None
        _wlanapiCache['loaded'] = True
        return None
    wlanapi = None
# WARNING: Decompyle incomplete


class LPWindowsWlanReader:
    '''通过 WLAN API 读取当前无线连接信息（不依赖系统语言与子进程）。'''
    
    def _decodeSsid(rawBytes):
        '''把 802.11 SSID 原始字节解码为字符串。

        SSID 字节按 UTF-8 解释（Windows 与主流路由器写入口径一致）；
        非法 UTF-8 时依次回退到系统首选编码和替换式解码，保证不抛异常。

        参数:
            rawBytes (bytes): SSID 原始字节。
        返回:
            str | None: 解码后的 SSID；字节为空时返回 None。
        '''
        if not rawBytes:
            return None
        :
            if not rawBytes:
                return None
            
            return rawBytes.decode('utf-8')
        return rawBytes.decode('utf-8')
    # WARNING: Decompyle incomplete

    _decodeSsid = staticmethod(_decodeSsid)
    
    def _formatBssid(rawBytes):
        '''把 6 字节 BSSID 格式化为 aa:bb:cc:dd:ee:ff 形式。

        参数:
            rawBytes (bytes): 6 字节 BSSID。
        返回:
            str | None: 格式化后的 BSSID；长度不足或全零时返回 None。
        '''
        if not len(rawBytes) != 6 or any(rawBytes):
            return None
        return None.join((lambda .0: for value in .0:
'%02x' % value)(rawBytes))

    _formatBssid = staticmethod(_formatBssid)
    
    def fetch(cls, log = (False,)):
        '''读取当前已连接无线接口的 SSID 与 BSSID。

        参数:
            log (bool): 是否输出调试日志。
        返回:
            dict | None: {"ssid": str | None, "bssid": str | None}；
                WLAN API 不可用或无线服务未启动时返回 None。
        '''
        wlanapi = _loadWlanApi()
        if wlanapi is None:
            return None
        handle = None.HANDLE()
        negotiatedVersion = wintypes.DWORD()
        result = wlanapi.WlanOpenHandle(WLAN_CLIENT_VERSION, None, ctypes.byref(negotiatedVersion), ctypes.byref(handle))
        if result == WINDOWS_ERROR_INVALID_PARAMETER:
            result = wlanapi.WlanOpenHandle(1, None, ctypes.byref(negotiatedVersion), ctypes.byref(handle))
        if result != 0:
            logger.warning('[win] WlanOpenHandle failed: %s' % result)
            return None
        interfaceList = ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)()
        result = wlanapi.WlanEnumInterfaces(handle, None, ctypes.byref(interfaceList))
        if not result != 0 or interfaceList:
            logger.warning('[win] WlanEnumInterfaces failed: %s' % result)
        wlanapi.WlanCloseHandle(handle, None)
        return None
        
        try:
            count = int(interfaceList.contents.dwNumberOfItems)
            baseAddress = ctypes.addressof(interfaceList.contents.InterfaceInfo)
            itemSize = ctypes.sizeof(WLAN_INTERFACE_INFO)
            for index in range(count):
                interface = WLAN_INTERFACE_INFO.from_address(baseAddress + index * itemSize)
                if interface.isState != WLAN_INTERFACE_STATE_CONNECTED:
                    continue
                connection = cls._queryConnection(wlanapi, handle, interface)
                if connection is None:
                    continue
                if log:
                    logger.debug('[network] WLAN API %s: %s' % (interface.strInterfaceDescription, connection))
        finally:
            wlanapi.WlanCloseHandle(handle, None)
            return None
            wlanapi.WlanFreeMemory(interfaceList)
        wlanapi.WlanCloseHandle(handle, None)
        wlanapi.WlanCloseHandle(handle, None)
        return None


    fetch = classmethod(fetch)
    
    def _q