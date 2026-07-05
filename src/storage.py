"""Работа с файловым хранилищем"""
import json
import os
import sys
from typing import Optional


class StorageManager:
    """Управление файловым хранилищем"""
    
    def __init__(self, vault_path: str = None):
        # Если путь не указан - определяем автоматически
        if vault_path is None:
            vault_path = self.get_default_vault_path()
        self.vault_path = vault_path
    
    @staticmethod
    def get_default_vault_path() -> str:
        """Определяет правильный путь к хранилищу"""
        # Если запущено как EXE (PyInstaller)
        if getattr(sys, 'frozen', False):
            # EXE находится в папке dist/
            exe_dir = os.path.dirname(sys.executable)
            
            # Вариант 1: data на уровень выше (рядом с dist)
            parent_dir = os.path.dirname(exe_dir)
            data_dir = os.path.join(parent_dir, 'data')
            
            # Если есть data на уровне выше - используем её
            if os.path.exists(data_dir):
                return os.path.join(data_dir, 'vault.vault')
            
            # Вариант 2: data в той же папке где EXE
            data_dir = os.path.join(exe_dir, 'data')
            if os.path.exists(data_dir):
                return os.path.join(data_dir, 'vault.vault')
            
            # Вариант 3: создать data на уровне выше (рядом с dist)
            os.makedirs(os.path.join(parent_dir, 'data'), exist_ok=True)
            return os.path.join(parent_dir, 'data', 'vault.vault')
        else:
            # Запуск через Python (разработка)
            return 'data/vault.vault'
    
    def save_vault(self, data: dict, key: bytes, crypto_manager) -> None:
        """Сохранение хранилища в зашифрованном виде"""
        # Создаем папку если её нет
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        encrypted = crypto_manager.encrypt(data, key)
        
        with open(self.vault_path, 'w') as f:
            json.dump(encrypted, f, indent=2)
        
        # Отладка - показываем где сохранили
        print(f"💾 Хранилище сохранено: {self.vault_path}")
    
    def load_vault(self, key: bytes, crypto_manager) -> Optional[dict]:
        """Загрузка и расшифровка хранилища"""
        if not os.path.exists(self.vault_path):
            print(f"⚠️ Файл не найден: {self.vault_path}")
            return None
        
        try:
            with open(self.vault_path, 'r') as f:
                encrypted = json.load(f)
            
            if not all(k in encrypted for k in ['iv', 'ciphertext', 'tag']):
                raise ValueError("Неверный формат файла хранилища")
            
            print(f"✅ Хранилище загружено: {self.vault_path}")
            return crypto_manager.decrypt(encrypted, key)
        except Exception as e:
            print(f"Ошибка при загрузке хранилища: {e}")
            return None
    
    def export_vault(self, data: dict, key: bytes, crypto_manager, export_path: str) -> None:
        """Экспорт хранилища"""
        encrypted = crypto_manager.encrypt(data, key)
        with open(export_path, 'w') as f:
            json.dump(encrypted, f, indent=2)
        print(f"✅ Хранилище экспортировано в {export_path}")