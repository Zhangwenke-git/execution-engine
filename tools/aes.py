"""pip install pycryptodome"""
import base64
from Crypto import Random
from Crypto.Cipher import AES
from hashlib import md5


class AESHelper:

    @classmethod
    def pad(cls, data):
        length = 16 - (len(data) % 16)
        return data.encode(encoding='utf-8') + (chr(length) * length).encode(encoding='utf-8')

    @classmethod
    def unpad(cls, data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    @classmethod
    def _bytes_to_key(cls, data, salt, output=48):
        data = data.encode(encoding='utf-8')
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    @classmethod
    def encrypt(cls, message, passphrase):
        salt = Random.new().read(8)
        key_iv = cls._bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(cls.pad(message)))

    @classmethod
    def decrypt(cls, encrypted, passphrase):
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = cls._bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return cls.unpad(aes.decrypt(encrypted[16:]))
