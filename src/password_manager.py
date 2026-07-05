"""Основной класс Password Manager"""
from typing import List, Optional
import uuid
from datetime import datetime
import os
import sys
import base64
from src.crypto import CryptoManager
from src.storage import StorageManager
from src.password_strength import PasswordStrengthAnalyzer
from src.password_generator import PasswordGenerator


class PasswordEntry:
    """Запись с паролем"""
    
    def __init__(self, login: str, password: str, url: str = "", note: str = ""):
        self.id = str(uuid.uuid4())
        self.login = login
        self.password = password
        self.url = url
        self.note = note
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password,
            'url': self.url,
            'note': self.note,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordEntry':
        entry = cls(
            login=data['login'],
            password=data['password'],
            url=data.get('url', ''),
            note=data.get('note', '')
        )
        entry.id = data.get('id', entry.id)
        entry.created_at = data.get('created_at', entry.created_at)
        entry.updated_at = data.get('updated_at', entry.updated_at)
        return entry


class PasswordManager:
    """Менеджер паролей"""
    
    def __init__(self, master_password: str, vault_path: str = None):
        self.crypto = CryptoManager()
        self.storage = StorageManager(vault_path)
        self.strength_analyzer = PasswordStrengthAnalyzer()
        self.generator = PasswordGenerator()
        
        self.master_password = master_password
        self.entries: List[PasswordEntry] = []
        self.salt = None
        self.key = None
        
        # Загружаем существующее хранилище или создаем новое
        if not self._load_vault():
            # Создаем новое хранилище
            self.salt = self.crypto.generate_salt()
            self.key = self.crypto.derive_key(master_password, self.salt)
            self.entries = []
            self._save_vault()
            print(f"🆕 Создано новое хранилище: {self.storage.vault_path}")
    
    def _load_vault(self) -> bool:
        """Загрузка хранилища из файла"""
        # Проверяем наличие файла
        if not os.path.exists(self.storage.vault_path):
            print(f"⚠️ Файл не найден: {self.storage.vault_path}")
            return False
        
        try:
            # Читаем зашифрованные данные
            with open(self.storage.vault_path, 'r') as f:
                import json
                encrypted = json.load(f)
            
            # Проверяем структуру
            if not all(k in encrypted for k in ['iv', 'ciphertext', 'tag']):
                print("❌ Неверный формат файла")
                return False
            
            # Извлекаем соль (она хранится в зашифрованных данных)
            # Сначала пробуем расшифровать с солью из данных
            # Если нет соли - используем старый формат
            
            # Для совместимости - пробуем дешифровать
            # ВАЖНО: соль сохраняется в файле отдельно
            salt_file = self.storage.vault_path + '.salt'
            if os.path.exists(salt_file):
                with open(salt_file, 'r') as f:
                    self.salt = base64.b64decode(f.read().strip())
            else:
                # Нет файла с солью - генерируем новую (старые данные не прочитаются)
                self.salt = self.crypto.generate_salt()
            
            self.key = self.crypto.derive_key(self.master_password, self.salt)
            
            # Расшифровываем
            decrypted = self.crypto.decrypt(encrypted, self.key)
            
            if 'entries' in decrypted:
                self.entries = [PasswordEntry.from_dict(e) for e in decrypted['entries']]
                print(f"✅ Загружено {len(self.entries)} записей из {self.storage.vault_path}")
                return True
            else:
                print("❌ Нет записей в файле")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_vault(self) -> None:
        """Сохранение хранилища в файл"""
        try:
            # Подготавливаем данные
            data = {
                'entries': [e.to_dict() for e in self.entries]
            }
            
            # Шифруем
            encrypted = self.crypto.encrypt(data, self.key)
            
            # Сохраняем
            with open(self.storage.vault_path, 'w') as f:
                import json
                json.dump(encrypted, f, indent=2)
            
            # Сохраняем соль отдельно
            salt_file = self.storage.vault_path + '.salt'
            with open(salt_file, 'w') as f:
                f.write(base64.b64encode(self.salt).decode('utf-8'))
            
            print(f"💾 Хранилище сохранено: {self.storage.vault_path} ({len(self.entries)} записей)")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            import traceback
            traceback.print_exc()
    
    def add_entry(self, login: str, password: str, url: str = "", note: str = "") -> PasswordEntry:
        """Добавление записи"""
        entry = PasswordEntry(login, password, url, note)
        self.entries.append(entry)
        self._save_vault()
        return entry
    
    def get_entry(self, entry_id: str) -> Optional[PasswordEntry]:
        """Получение записи по ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def search_entries(self, query: str) -> List[PasswordEntry]:
        """Поиск записей"""
        query = query.lower()
        results = []
        for entry in self.entries:
            if (query in entry.login.lower() or
                query in entry.url.lower() or
                query in entry.note.lower()):
                results.append(entry)
        return results
    
    def list_entries(self) -> List[PasswordEntry]:
        """Список всех записей"""
        return self.entries
    
    def delete_entry(self, entry_id: str) -> bool:
        """Удаление записи"""
        for i, entry in enumerate(self.entries):
            if entry.id == entry_id:
                self.entries.pop(i)
                self._save_vault()
                return True
        return False
    
    def export_vault(self, export_path: str) -> None:
        """Экспорт хранилища"""
        data = {
            'entries': [e.to_dict() for e in self.entries]
        }
        encrypted = self.crypto.encrypt(data, self.key)
        with open(export_path, 'w') as f:
            import json
            json.dump(encrypted, f, indent=2)
        
        # Также сохраняем соль
        with open(export_path + '.salt', 'w') as f:
            f.write(base64.b64encode(self.salt).decode('utf-8'))
        
        print(f"✅ Хранилище экспортировано в {export_path}")
    
    def check_password(self, password: str) -> dict:
        """Проверка стойкости пароля"""
        return self.strength_analyzer.classify_strength(password)
    
    def generate_password(self, **kwargs) -> str:
        """Генерация пароля"""
        return self.generator.generate(**kwargs)