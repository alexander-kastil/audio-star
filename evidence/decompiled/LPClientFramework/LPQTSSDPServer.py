# Source Generated with Decompyle++
# File: LPQTSSDPServer.pyc (Python 3.9)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtNetwork import QUdpSocket, QHostAddress, QNetworkInterface, QNetworkDatagram
from PyQt6 import QtNetwork
from PyQt6.QtCore import QRunnable, QThreadPool
from random import Random
import threading
import platform
import time
from LPClientFramework import LPUtility
from LPClientFramework.CacheLog import logger
from LPClientFramework.LPUtility import fetchLocalIP
SSDP_PORT = 1900
SSDP_ADDR_V4 = '239.255.255.250'
SSDP_ADDR_V6 = '[FF05::C]'

def validInterfaces():
    '''过滤所有可能的interface
    '''
    ifaces = QNetworkInterface.allInterfaces()
    if ifaces is None:
        return None
    retInterfaces = None
    for iface in ifaces:
        flags = iface.flags()
        is_loopback = bool(flags & QNetworkInterface.InterfaceFlag.IsLoopBack)
        is_p2p = bool(flags & QNetworkInterface.InterfaceFlag.IsPointToPoint)
        is_running = bool(flags & QNetworkInterface.InterfaceFlag.IsRunning)
        canMulticast = bool(flags & QNetworkInterface.InterfaceFlag.CanMulticast)
        if not is_running or canMulticast:
            continue
        if iface.isValid() and is_loopback or is_p2p:
            continue
        retInterfaces.append(iface)
    return retInterfaces


class RequestHandler(QRunnable):
    
    def __init__(self = None, datagram = None, sender_addr = None, sender_port = None, ssdpServer = None):
        super().__init__()
        self.datagram = datagram
        self.sender_addr = sender_addr
        self.sender_port = sender_port
        self.ssdpServer = ssdpServer

    
    def run(self):
        (method, path, version, headers) = self.http_parse_raw(self.datagram)
        if method == 'M-SEARCH':
            self.received_MSEARCH(headers, (self.sender_addr, self.sender_port))
        elif method == 'NOTIFY':
            self.received_NOTIFY(headers, (self.sender_addr, self.sender_port))
        else:
            logger.warning("[UPnPServer] unhandled Method '%s'", self.datagram)

    
    def received_MSEARCH(self, headers, addr):
        (address, port) = addr
    # WARNING: Decompyle incomplete

    
    def respond(self, headers, addr):
        (address, port) = addr
        logger.debug('[UPnPServer] respond %s:%s', address.toString(), port)
        msg = 'HTTP/1.1 200 OK\r\n'
        msg += self.headers_join(headers)
        msg += '\r\n\r\n'
    # WARNING: Decompyle incomplete

    
    def notify_live_method(self):
        self.send_NOTIFY('', 'ssdp:alive')
        time.sleep(0.1)
        self.send_NOTIFY('upnp:rootdevice', 'ssdp:alive')
        time.sleep(0.1)
        self.send_NOTIFY('urn:schemas-upnp-org:service:ContentDirectory:1', 'ssdp:alive')
        time.sleep(0.1)
        self.send_NOTIFY('urn:schemas-upnp-org:device:MediaServer:1', 'ssdp:alive')

    
    def notify_bye_method(self):
        self.send_NOTIFY('', 'ssdp:byebye')
        time.sleep(0.1)
        self.send_NOTIFY('upnp:rootdevice', 'ssdp:byebye')
        time.sleep(0.1)
        self.send_NOTIFY('urn:schemas-upnp-org:service:ContentDirectory:1', 'ssdp:byebye')
        time.sleep(0.1)
        self.send_NOTIFY('urn:schemas-upnp-org:device:MediaServer:1', 'ssdp:byebye')

    
    def notify(self, headers, addr):
        (address, port) = addr
        msg = 'NOTIFY * HTTP/1.1\r\n'
        msg += self.headers_join(headers)
        msg += '\r\n\r\n'
    # WARNING: Decompyle incomplete

    
    def respond_MSEARCH(self, st, addr):
        (address, port) = addr
        ip = '127.0.0.1'
        if address.toString() != '127.0.0.1':
            ip = fetchLocalIP()
        location = 'http://%s:%d/upnp/DeviceDescription.xml' % (ip, LPUtility.upnpServerPort)
        (usn, st) = self.build_notification_type(self.ssdpServer.uuid, st)
        headers = {
            'CACHE-CONTROL': 'max-age = %d' % self.ssdpServer.responseExpire,
            'EXT': '',
            'LOCATION': location,
            'SERVER': self.ssdpServer.upnpServerStr,
            'ST': st,
            'USN': usn,
            'OPT': '"http://schemas.upnp.org/upnp/1/0/"; ns=01',
            '01-NLS': self.ssdpServer.bootID,
            'BOOTID.UPNP.ORG': self.ssdpServer.bootID }
        self.respond(headers, (address, port))

    
    def send_NOTIFY(self, nt, nts):
        ip = fetchLocalIP()
        location = 'http://%s:%d/upnp/DeviceDescription.xml' % (ip, LPUtility.upnpServerPort)
        (usn, nt) = self.build_notification_type(self.ssdpServer.uuid, nt)
        headers = {
            'HOST': '%s:%d' % (SSDP_ADDR_V4, SSDP_PORT),
            'CACHE-CONTROL': 'max-age = %d' % self.ssdpServer.responseExpire,
            'LOCATION': location,
            'SERVER': self.ssdpServer.upnpServerStr,
            'NT': nt,
            'NTS': nts,
            'USN': usn,
            'BOOTID.UPNP.ORG': self.ssdpServer.bootID,
            'CONFIGID.UPNP.ORG': 1 }
        self.notify(headers, (QHostAddress(SSDP_ADDR_V4), SSDP_PORT))

    
    def received_NOTIFY(self, headers, addr):
        (address, port) = addr

    
    def http_parse_raw(self, data):
        lines = data.split('\r\n')
        (version, respCode, respText) = (None, None, None)
        headers = { }
    # WARNING: Decompyle incomplete

    
    def build_notification_type(self, uuid, nt):
        if nt == '':
            return ('uuid:' + uuid, 'uuid:' + uuid)
        return (None + uuid + '::' + nt, nt)

    
    def headers_join(self, headers):
        msg = ''
        for hk, hv in headers.items():
            msg += str(hk) + ': ' + str(hv) + '\r\n'
        return msg

    __classcell__ = None


class LPQTSSDPServer:
    
    def __init__(self, responseExpire = (900,)):
        self.responseExpire = responseExpire
        self.running = False
        self.rand = Random()
        self.bootID = int(time.time())
        self.uuid = LPUtility.pcUUID()
        SERVER_STRING = '%s/%s UPnP/1.0 DLNADOC/1.50 WiiMHome/%s' % (platform.system(), platform.release(), QApplication.applicationVersion())
        self.upnpServerStr = SERVER_STRING
        self.socket = QUdpSocket()
        self.thread_pool = QThreadPool()

    
    def start(self):
        if self.running:
            logger.warning('[UPnPServer] already running')
            return None
        self.bootID = None(time.time())
        logger.debug('[UPnPServer] ssdp start listen')
        self.running = True
        self.socket.bind(QHostAddress.SpecialAddress.AnyIPv4, SSDP_PORT, QtNetwork.QAbstractSocket.BindFlag.ShareAddress | QtNetwork.QAbstractSocket.BindFlag.ReuseAddressHint)
        for interface in validInterfaces():
            self.socket.joinMulticastGroup(QHostAddress(SSDP_ADDR_V4), interface)
        self.socket.readyRead.connect(self.receive_message)
        self.liveSwitch = True
        self.notifyThread = threading.Thread(self.sendLiveNotify, **('target',))
        self.notifyThread.setDaemon(True)
        self.notifyThread.start()

    
    def sendLiveNotify(self):
        if not self.liveSwitch:
            pass
        else:
            handler = RequestHandler(None, None, 0, self)
            handler.notify_live_method()
            time.sleep(self.responseExpire + 600)

    
    def receive_message(self):
        if self.socket.hasPendingDatagrams():
            size = self.socket.pendingDatagramSize()
            (datagram, address, port) = self.socket.readDatagram(size)
            data = datagram.decode()
            handler = RequestHandler(data, address, port, self)
            self.thread_pool.start(handler)
            continue

    
    def stop(self):
        logger.debug('[UPnPServer] stop')
        if not self.running:
            logger.warning('[UPnPServer] already stop')
            return None
        self.liveSwitch = None
        self.bootID = 0
        self.running = False
        handler = RequestHandler(None, None, 0, self)
        handler.notify_bye_method()
        self.socket.close()


