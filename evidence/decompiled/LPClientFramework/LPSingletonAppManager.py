# Source Generated with Decompyle++
# File: LPSingletonAppManager.pyc (Python 3.9)

from PyQt6.QtNetwork import QLocalServer, QLocalSocket, QAbstractSocket
from PyQt6.QtCore import QObject, pyqtSignal
from LPClientFramework.LPUtility import logger

class LPSingletonAppManager(QObject):
    messageReceived = pyqtSignal(str)
    
    def __init__(self = None, key = None, timeout = None):
        super().__init__()
        self.key = key
        self.timeout = 500
        self._is_running = False
        self._local_server = None
        self.socket = None
        self.msg = None
        self._init_local_connection()

    
    def is_running(self = None):
        return self._is_running

    
    def _init_local_connection(self):
        '''尝试连接已有实例，如果失败则创建本地 server'''
        socket = QLocalSocket()
        socket.connectToServer(self.key)
        if socket.waitForConnected(self.timeout):
            logger.debug(f'''[_init_local_connection] {self.key} already running.''')
            self._is_running = True
            socket.close()
            return None
        None._new_local_server()

    
    def _new_local_server(self):
        '''创建 LocalServer，并监听新连接'''
        self._local_server = QLocalServer(self)
        self._local_server.setSocketOptions(QLocalServer.SocketOption.WorldAccessOption)
        self._local_server.newConnection.connect(self._new_local_connection)
        if not self._local_server.listen(self.key):
            if self._local_server.serverError() == QAbstractSocket.SocketError.AddressInUseError:
                QLocalServer.removeServer(self.key)
                if not self._local_server.listen(self.key):
                    logger.debug(f'''Error: Could not listen even after removing stale server: {self.key}''')
                    self._is_running = True
                else:
                    logger.debug(f'''self._local_server.serverError() = {self._local_server.serverError()}''')
                    logger.debug(f'''Error: Could not listen on {self.key}: {self._local_server.errorString()}''')
                    self._is_running = True

    
    def _new_local_connection(self):
        '''收到新连接，激活窗口'''
        logger.debug('[_onNewConnection] triggered')
        self.socket = self._local_server.nextPendingConnection()
        logger.debug('[_onNewConnection] socket connected')
        None((lambda : self._handleMessage()))

    
    def _handleMessage(self):
        self.msg = self.socket.readAll().data().decode()
        logger.debug(f'''[_handleMessage] msg = {self.msg}''')
        self.socket.disconnectFromServer()
        if self.msg:
            self.messageReceived.emit(self.msg)

    
    def sendMsgToPrimary(self = None, message = None):
        '''
        子实例调用，向主实例发送消息。
        '''
        logger.debug(f'''[sendMsgToPrimary] msg = {message}''')
        socket = QLocalSocket()
        socket.connectToServer(self.key)
        if socket.waitForConnected(1000):
            if not message:
                message = 'wiim://showApp'
            socket.write(message.encode())
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            logger.debug('[sendMsgToPrimary] success')

    __classcell__ = None

