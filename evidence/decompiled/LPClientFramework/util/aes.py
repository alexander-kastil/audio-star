# Source Generated with Decompyle++
# File: aes.pyc (Python 3.9)

import base64
from Crypto.Cipher import AES

class AESCipher(object):
    
    def __init__(self, key):
        pass

    
    def encrypt(key, raw):
        iv = bytes(16).decode()
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        length = 16
        count = len(raw.encode('utf-8'))
        if count % length != 0:
            add = length - count % length
        else:
            add = 0
        raw = raw + '\x00' * add
        encrypted = cipher.encrypt(raw.encode('utf-8'))
        encoded = base64.b64encode(encrypted)
        return str(encoded, 'utf-8')

    encrypt = staticmethod(encrypt)
    
    def encrypt2(key = None, raw = None):
        '''
        完全对应下面这段 Objective-C 逻辑：
        - key 用 UUID 的 UTF-8 bytes，右补 0 截取 16 字节
        - iv 全 0
        - 计算 diff = 16 - (len(data)%16)，如果 diff>0 且 diff<=16，就在末尾填 diff 个 0
        - AES-CBC, NoPadding
        - Base64 返回
        '''
        key_bytes = key.encode('utf-8')
        key_bytes = key_bytes + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'[:16]
        iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        data = raw.encode('utf-8')
        data_len = len(data)
        diff = AES.block_size - data_len % AES.block_size
        if diff > 0 and diff <= AES.block_size:
            padded = data + b'\x00' * diff
        else:
            padded = data
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode('utf-8')

    encrypt2 = None(encrypt2)
    
    def decrypt(key, raw):
        iv = bytes(16).decode()
        decryptedBytes = base64.b64decode(raw)
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        decrypted = cipher.decrypt(decryptedBytes)
        return decrypted.decode('utf-8', 'ignore').strip('\x00')

    decrypt = staticmethod(decrypt)
    
    def decrypt2(key = None, raw = None):
        '''
        对应上面 aes128_encrypt 的解密函数：
        - key 用 UUID 的 UTF-8 bytes，右补 0 截取 16 字节
        - iv 全 0
        - 无库级 Padding，手动填充时都是右侧 0x00
        - 解密后 strip 掉尾部的 0x00
        - 返回 UTF-8 字符串
        '''
        key_bytes = key.encode('utf-8')
        key_bytes = key_bytes + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'[:16]
        iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        encrypted = base64.b64decode(raw)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        return decrypted.rstrip(b'\x00').decode('utf-8')

    decrypt2 = None(decrypt2)

if __name__ == '__main__':
    ret = AESCipher.encrypt2('FF98F7F4DE2A98B5', 'QOc59BL8NEGEb7PNh3iyl5DLhQ6Twicd')
    print(ret)
