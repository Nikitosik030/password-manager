"""Криптографические функции: AES-128, PBKDF2"""
import os
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Управление шифрованием и деривацией ключа"""
    
    SALT_SIZE = 16
    KEY_SIZE = 16  # AES-128
    ITERATIONS = 100_000
    
    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        """Деривация ключа из мастер-пароля"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=CryptoManager.KEY_SIZE,
            salt=salt,
            iterations=CryptoManager.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(master_password.encode('utf-8'))
    
    @staticmethod
    def generate_salt() -> bytes:
        """Генерация случайной соли"""
        return os.urandom(CryptoManager.SALT_SIZE)
    
    @staticmethod
    def encrypt(data: dict, key: bytes) -> dict:
        """Шифрование данных AES-128 GCM"""
        plaintext = json.dumps(data).encode('utf-8')
        iv = os.urandom(12)
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return {
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(encryptor.tag).decode('utf-8')
        }
    
    @staticmethod
    def decrypt(encrypted_data: dict, key: bytes) -> dict:
        """Расшифрование данных"""
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        tag = base64.b64decode(encrypted_data['tag'])
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return json.loads(plaintext.decode('utf-8'))