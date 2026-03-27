import os
import gzip
import random
from Crypto.Cipher import AES, ARC4
from Crypto.Util.Padding import pad


MODES = ["aes", "xor_aes", "rc4_aes"]


def compress(data: bytes, level: int = 9) -> bytes:
    """GZip compress payload."""
    return gzip.compress(data, compresslevel=level)


def gen_key_iv() -> tuple:
    """Generate random AES-256 key (32 bytes) and IV (16 bytes)."""
    return os.urandom(32), os.urandom(16)


def gen_xor_key(length: int = 32) -> bytes:
    """Generate random XOR key."""
    return os.urandom(length)


def gen_rc4_key(length: int = 32) -> bytes:
    """Generate random RC4 key."""
    return os.urandom(length)



def aes_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-256-CBC encrypt with PKCS7 padding."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))


def xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Rolling XOR encryption."""
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def rc4_encrypt(data: bytes, key: bytes) -> bytes:
    """RC4 stream cipher encryption."""
    cipher = ARC4.new(key)
    return cipher.encrypt(data)



def encrypt_layered(data: bytes, mode: str = "aes") -> dict:
    aes_key, aes_iv = gen_key_iv()

    if mode == "xor_aes":
        xor_key = gen_xor_key()
        step1 = xor_encrypt(data, xor_key)
        step2 = aes_encrypt(step1, aes_key, aes_iv)
        return {
            "mode": "xor_aes",
            "ciphertext": step2,
            "aes_key": aes_key,
            "aes_iv": aes_iv,
            "xor_key": xor_key,
        }

    elif mode == "rc4_aes":
        rc4_key = gen_rc4_key()
        step1 = rc4_encrypt(data, rc4_key)
        step2 = aes_encrypt(step1, aes_key, aes_iv)
        return {
            "mode": "rc4_aes",
            "ciphertext": step2,
            "aes_key": aes_key,
            "aes_iv": aes_iv,
            "rc4_key": rc4_key,
        }

    else:  # "aes" default
        ct = aes_encrypt(data, aes_key, aes_iv)
        return {
            "mode": "aes",
            "ciphertext": ct,
            "aes_key": aes_key,
            "aes_iv": aes_iv,
        }


def random_mode() -> str:
    return random.choice(MODES)
