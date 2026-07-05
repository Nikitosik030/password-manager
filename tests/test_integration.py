"""Интеграционные тесты для Password Manager"""
import pytest
import tempfile
import os
import json
from src.password_manager import PasswordManager, PasswordEntry
from src.crypto import CryptoManager


class TestIntegration:
    """Интеграционное тестирование полного цикла работы"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = os.path.join(self.temp_dir, "test.vault")
        self.master_password = "MasterPassword123!"
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_cycle(self):
        """Полный цикл: создание, добавление, поиск, удаление"""
        
        # 1. Инициализация менеджера
        manager = PasswordManager(self.master_password, self.vault_path)
        assert len(manager.list_entries()) == 0
        
        # 2. Добавление записей
        entry1 = manager.add_entry(
            login="user1",
            password="pass123",
            url="https://site1.com",
            note="Test user 1"
        )
        entry2 = manager.add_entry(
            login="user2",
            password="pass456",
            url="https://site2.com"
        )
        
        assert len(manager.list_entries()) == 2
        
        # 3. Проверка ID
        assert entry1.id is not None
        assert entry2.id is not None
        
        # 4. Поиск
        results = manager.search_entries("user1")
        assert len(results) == 1
        assert results[0].login == "user1"
        assert results[0].url == "https://site1.com"
        
        # 5. Получение по ID
        found = manager.get_entry(entry1.id)
        assert found is not None
        assert found.login == "user1"
        
        # 6. Обновление
        updated = manager.update_entry(entry1.id, password="newpass123")
        assert updated.password == "newpass123"
        
        # 7. Удаление
        assert manager.delete_entry(entry2.id)
        assert len(manager.list_entries()) == 1
        
        # 8. Проверка что второй записи нет
        assert manager.get_entry(entry2.id) is None
    
    def test_persistence(self):
        """Тест сохранения данных между сессиями"""
        
        # Первая сессия - создание данных
        manager1 = PasswordManager(self.master_password, self.vault_path)
        entry = manager1.add_entry(
            login="persistent_user",
            password="persistent_pass",
            url="https://test.com"
        )
        entry_id = entry.id
        
        # Вторая сессия - загрузка данных
        manager2 = PasswordManager(self.master_password, self.vault_path)
        entries = manager2.list_entries()
        
        assert len(entries) == 1
        assert entries[0].login == "persistent_user"
        assert entries[0].password == "persistent_pass"
        assert entries[0].id == entry_id
    
    def test_search(self):
        """Тест поиска по разным полям"""
        manager = PasswordManager(self.master_password, self.vault_path)
        
        # Добавление тестовых данных
        manager.add_entry("alice@mail.com", "pass1", "https://mail.com")
        manager.add_entry("bob@work.com", "pass2", "https://work.com")
        manager.add_entry("charlie@home.com", "pass3", "https://home.com", "Home account")
        
        # Поиск по логину
        results = manager.search_entries("alice")
        assert len(results) == 1
        assert results[0].login == "alice@mail.com"
        
        # Поиск по URL
        results = manager.search_entries("work")
        assert len(results) == 1
        assert results[0].url == "https://work.com"
        
        # Поиск по заметке
        results = manager.search_entries("Home")
        assert len(results) == 1
        assert results[0].note == "Home account"
        
        # Поиск по частичному совпадению
        results = manager.search_entries(".com")
        assert len(results) == 3
        
        # Поиск несуществующего
        results = manager.search_entries("nonexistent")
        assert len(results) == 0
    
    def test_export_import(self):
        """Тест экспорта и импорта хранилища"""
        manager = PasswordManager(self.master_password, self.vault_path)
        
        # Добавление данных
        manager.add_entry("export_user", "export_pass", "https://export.com")
        manager.add_entry("export_user2", "export_pass2", "https://export2.com")
        
        # Экспорт
        export_path = os.path.join(self.temp_dir, "export.vault")
        manager.export_vault(export_path)
        
        # Проверка что файл создан
        assert os.path.exists(export_path)
        
        # Создание нового менеджера с новым хранилищем
        new_vault_path = os.path.join(self.temp_dir, "new.vault")
        new_manager = PasswordManager(self.master_password, new_vault_path)
        
        # Импорт
        assert new_manager.import_vault(export_path)
        assert len(new_manager.list_entries()) == 2
        
        # Проверка данных
        entries = new_manager.list_entries()
        assert any(e.login == "export_user" for e in entries)
        assert any(e.login == "export_user2" for e in entries)
    
    def test_wrong_password(self):
        """Тест с неправильным мастер-паролем"""
        # Создание с правильным паролем
        manager1 = PasswordManager("correct_password", self.vault_path)
        manager1.add_entry("test", "pass", "url")
        
        # Попытка загрузить с неправильным паролем
        with pytest.raises(Exception):
            manager2 = PasswordManager("wrong_password", self.vault_path)
            manager2.list_entries()
    
    def test_empty_vault(self):
        """Тест пустого хранилища"""
        manager = PasswordManager(self.master_password, self.vault_path)
        assert len(manager.list_entries()) == 0
        
        # Поиск в пустом хранилище
        results = manager.search_entries("anything")
        assert len(results) == 0
        
        # Удаление несуществующей записи
        assert manager.delete_entry("nonexistent_id") == False
    
    def test_add_entry_without_url(self):
        """Тест добавления записи без URL"""
        manager = PasswordManager(self.master_password, self.vault_path)
        entry = manager.add_entry(
            login="test_user",
            password="test_pass",
            note="No URL provided"
        )
        
        assert entry.url == ""
        assert entry.note == "No URL provided"
    
    def test_password_entry_serialization(self):
        """Тест сериализации записи"""
        entry = PasswordEntry("test", "pass", "url", "note")
        entry_dict = entry.to_dict()
        
        assert entry_dict['login'] == "test"
        assert entry_dict['password'] == "pass"
        assert entry_dict['url'] == "url"
        assert entry_dict['note'] == "note"
        
        # Восстановление из словаря
        restored = PasswordEntry.from_dict(entry_dict)
        assert restored.login == entry.login
        assert restored.password == entry.password
        assert restored.url == entry.url
        assert restored.note == entry.note
    
    def test_multiple_operations(self):
        """Тест множественных операций подряд"""
        manager = PasswordManager(self.master_password, self.vault_path)
        
        # Добавление 10 записей
        for i in range(10):
            manager.add_entry(
                login=f"user_{i}",
                password=f"pass_{i}",
                url=f"https://site_{i}.com"
            )
        
        assert len(manager.list_entries()) == 10
        
        # Поиск
        results = manager.search_entries("user_5")
        assert len(results) == 1
        
        # Удаление четных
        entries = manager.list_entries()
        for entry in entries:
            if int(entry.login.split('_')[1]) % 2 == 0:
                manager.delete_entry(entry.id)
        
        # Должно остаться 5 записей (нечетные)
        assert len(manager.list_entries()) == 5
        
        # Проверка что остались только нечетные
        for entry in manager.list_entries():
            num = int(entry.login.split('_')[1])
            assert num % 2 == 1