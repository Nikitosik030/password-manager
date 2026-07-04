"""Тесты для криптографических функций"""
import pytest
import json
from src.crypto import CryptoManager


class TestCrypto:
    """Тестирование шифрования и деривации ключа"""
    
    def test_derive_key(self):
        """Тест деривации ключа из пароля"""
        password = "test_password_123"
        salt = CryptoManager.generate_salt()
        
        key1 = CryptoManager.derive_key(password, salt)
        key2 = CryptoManager.derive_key(password, salt)
        key3 = CryptoManager.derive_key("wrong_password", salt)
        
        # Проверка длины ключа (AES-128 = 16 байт)
        assert len(key1) == CryptoManager.KEY_SIZE
        assert len(key2) == CryptoManager.KEY_SIZE
        
        # Одинаковые пароли дают одинаковый ключ
        assert key1 == key2
        
        # Разные пароли дают разные ключи
        assert key1 != key3
        
        # Разные соли дают разные ключи
        salt2 = CryptoManager.generate_salt()
        key4 = CryptoManager.derive_key(password, salt2)
        assert key1 != key4
    
    def test_generate_salt(self):
        """Тест генерации соли"""
        salt1 = CryptoManager.generate_salt()
        salt2 = CryptoManager.generate_salt()
        
        # Проверка длины соли
        assert len(salt1) == CryptoManager.SALT_SIZE
        assert len(salt2) == CryptoManager.SALT_SIZE
        
        # Соли должны быть разными (случайными)
        assert salt1 != salt2
    
    def test_encrypt_decrypt(self):
        """Тест шифрования и расшифрования"""
        key = CryptoManager.derive_key("master_password", CryptoManager.generate_salt())
        
        # Тестовые данные
        test_data = {
            "login": "test_user",
            "password": "secret_123",
            "url": "https://example.com",
            "note": "Test note"
        }
        
        # Шифрование
        encrypted = CryptoManager.encrypt(test_data, key)
        
        # Проверка наличия всех полей
        assert 'iv' in encrypted
        assert 'ciphertext' in encrypted
        assert 'tag' in encrypted
        
        # Проверка что зашифрованные данные - это base64 строки
        import base64
        try:
            base64.b64decode(encrypted['iv'])
            base64.b64decode(encrypted['ciphertext'])
            base64.b64decode(encrypted['tag'])
        except Exception:
            pytest.fail("Зашифрованные данные не в формате base64")
        
        # Расшифрование
        decrypted = CryptoManager.decrypt(encrypted, key)
        
        # Проверка что данные совпадают
        assert decrypted == test_data
    
    def test_encrypt_decrypt_wrong_key(self):
        """Тест: расшифрование с неправильным ключом должно вызвать ошибку"""
        key1 = CryptoManager.derive_key("master1", CryptoManager.generate_salt())
        key2 = CryptoManager.derive_key("master2", CryptoManager.generate_salt())
        
        test_data = {"test": "data"}
        
        # Шифрование с key1
        encrypted = CryptoManager.encrypt(test_data, key1)
        
        # Попытка расшифровать с key2 - должна быть ошибка
        with pytest.raises(Exception):
            CryptoManager.decrypt(encrypted, key2)
    
    def test_encrypt_decrypt_different_data(self):
        """Тест шифрования разных данных"""
        key = CryptoManager.derive_key("master", CryptoManager.generate_salt())
        
        data1 = {"user": "alice", "pass": "123"}
        data2 = {"user": "bob", "pass": "456"}
        
        encrypted1 = CryptoManager.encrypt(data1, key)
        encrypted2 = CryptoManager.encrypt(data2, key)
        
        # Зашифрованные данные должны быть разными
        assert encrypted1['ciphertext'] != encrypted2['ciphertext']
        
        # Расшифровка должна дать исходные данные
        assert CryptoManager.decrypt(encrypted1, key) == data1
        assert CryptoManager.decrypt(encrypted2, key) == data2
    
    def test_encrypt_empty_data(self):
        """Тест шифрования пустых данных"""
        key = CryptoManager.derive_key("master", CryptoManager.generate_salt())
        
        empty_data = {}
        encrypted = CryptoManager.encrypt(empty_data, key)
        decrypted = CryptoManager.decrypt(encrypted, key)
        
        assert decrypted == empty_data
    
    def test_encrypt_large_data(self):
        """Тест шифрования больших данных"""
        key = CryptoManager.derive_key("master", CryptoManager.generate_salt())
        
        # Создание большого словаря
        large_data = {
            "entries": [
                {"login": f"user_{i}", "password": f"pass_{i}" * 10}
                for i in range(100)
            ]
        }
        
        encrypted = CryptoManager.encrypt(large_data, key)
        decrypted = CryptoManager.decrypt(encrypted, key)
        
        assert decrypted == large_data
        assert len(decrypted['entries']) == 100