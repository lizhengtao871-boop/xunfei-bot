import base64
import hashlib
import struct
import socket
import time
import random
import string
from Crypto.Cipher import AES
from src.config import config


class WXBizMsgCrypt:
    def __init__(self):
        self.token = config.WX_TOKEN
        self.encoding_aes_key = config.WX_ENCODING_AES_KEY
        self.aes_key = base64.b64decode(self.encoding_aes_key + "=")
        self.corp_id = config.WX_CORP_ID.encode("utf-8")

    def _sha1(self, *args) -> str:
        return hashlib.sha1("".join(sorted(args)).encode()).hexdigest()

    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str | None:
        """Verify callback URL. Returns decrypted echostr or None if signature fails."""
        if self._sha1(self.token, timestamp, nonce, echostr) != msg_signature:
            return None
        return self.decrypt(echostr)

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt an encrypted message from WeChat Work."""
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        plaintext = cipher.decrypt(base64.b64decode(ciphertext))
        # PKCS#7 unpad
        pad = plaintext[-1]
        plaintext = plaintext[:-pad]
        # Structure: random(16) + msg_len(4) + msg + corp_id
        msg_len = socket.ntohl(struct.unpack("I", plaintext[16:20])[0])
        msg = plaintext[20:20 + msg_len]
        return msg.decode("utf-8")

    def encrypt(self, text: str) -> str:
        """Encrypt a reply message for WeChat Work."""
        text_bytes = text.encode("utf-8")
        random_bytes = bytes(random.randint(0, 255) for _ in range(16))
        msg_len = struct.pack("!I", len(text_bytes))
        raw = random_bytes + msg_len + text_bytes + self.corp_id
        # PKCS#7 pad
        pad = 32 - len(raw) % 32
        raw += bytes([pad] * pad)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        return base64.b64encode(cipher.encrypt(raw)).decode()

    def sign_encrypt(self, text: str, timestamp: str, nonce: str) -> str:
        """Encrypt reply and generate signature for callback response."""
        encrypted = self.encrypt(text)
        signature = self._sha1(self.token, timestamp, nonce, encrypted)
        return encrypted, signature
