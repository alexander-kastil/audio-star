# Source Generated with Decompyle++
# File: LPTLSTool.pyc (Python 3.9)

import socket
import ssl
import base64
import codecs
import tempfile
import os
from contextlib import contextmanager
str1 = '<redacted>'
str2 = '<redacted>'
str3 = '<redacted>'

def twoNames():
    
    def _twoNames(str1, str2, str3):
        
        def _str2Name(tempStr):
            tstr1 = base64.b64decode(tempStr).decode('utf-8')
            tstr1 = codecs.decode(tstr1, 'rot13')
            f1 = tempfile.NamedTemporaryFile(False, **('delete',))
            f1.write(tstr1.encode('utf-8'))
            f1.close()
            return f1.name

        return (_str2Name(str1), _str2Name(str2), _str2Name(str3))

    (n1, n2, n3) = _twoNames(str1, str2, str3)
    yield (n1, n2, n3)
    os.unlink(n1)
    os.unlink(n2)
    os.unlink(n3)

twoNames = contextmanager(twoNames)

def tlsCmd(ip, command, port = (8893,)):
    
    def _twoNames(str1, str2, str3):
        
        def _str2Name(tempStr):
            tstr1 = base64.b64decode(tempStr).decode('utf-8')
            tstr1 = codecs.decode(tstr1, 'rot13')
            f1 = tempfile.NamedTemporaryFile(False, **('delete',))
            f1.write(tstr1.encode('utf-8'))
            f1.close()
            return f1.name

        return (_str2Name(str1), _str2Name(str2), _str2Name(str3))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    (n1, n2, n3) = _twoNames(str1, str2, str3)
    context.load_verify_locations(n3)
    context.load_cert_chain(n1, n2, **('certfile', 'keyfile'))
    secure_sock = context.wrap_socket(sock, False, ip, **('server_side', 'server_hostname'))
    os.unlink(n1)
    os.unlink(n2)
    os.unlink(n3)
    secure_sock.write(command.encode('utf-8'))
    data = b''
    received = secure_sock.read(1024)
    if len(received) == 0:
        pass
    else:
        data += received
    secure_sock.close()
    sock.close()
    return data

if __name__ == '__main__':
    print(tlsCmd('192.168.1.35', 'getStatusEx'))
