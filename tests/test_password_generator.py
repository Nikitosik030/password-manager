"""Тесты для генератора паролей"""
import pytest
import re
from src.password_generator import PasswordGenerator


class TestPasswordGenerator:
    """Тестирование генерации паролей"""
    
    def test_generate_default(self):
        """Тест генерации пароля по умолчанию"""
        password = PasswordGenerator.generate()
        
        # Проверка длины
        assert len(password) == 16
        
        # Проверка наличия всех типов символов
        assert any(c.islower() for c in password), "Нет строчных букв"
        assert any(c.isupper() for c in password), "Нет заглавных букв"
        assert any(c.isdigit() for c in password), "Нет цифр"
        assert any(c in PasswordGenerator.SPECIAL for c in password), "Нет спецсимволов"
    
    def test_generate_length(self):
        """Тест генерации паролей разной длины"""
        lengths = [8, 12, 16, 20, 32, 64]
        
        for length in lengths:
            password = PasswordGenerator.generate(length=length)
            assert len(password) == length
    
    def test_generate_no_lowercase(self):
        """Тест генерации без строчных букв"""
        password = PasswordGenerator.generate(use_lowercase=False)
        assert not any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in PasswordGenerator.SPECIAL for c in password)
    
    def test_generate_no_uppercase(self):
        """Тест генерации без заглавных букв"""
        password = PasswordGenerator.generate(use_uppercase=False)
        assert any(c.islower() for c in password)
        assert not any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in PasswordGenerator.SPECIAL for c in password)
    
    def test_generate_no_digits(self):
        """Тест генерации без цифр"""
        password = PasswordGenerator.generate(use_digits=False)
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert not any(c.isdigit() for c in password)
        assert any(c in PasswordGenerator.SPECIAL for c in password)
    
    def test_generate_no_special(self):
        """Тест генерации без спецсимволов"""
        password = PasswordGenerator.generate(use_special=False)
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert not any(c in PasswordGenerator.SPECIAL for c in password)
    
    def test_generate_only_lowercase(self):
        """Тест генерации только строчных букв"""
        password = PasswordGenerator.generate(
            use_lowercase=True,
            use_uppercase=False,
            use_digits=False,
            use_special=False
        )
        assert all(c.islower() for c in password)
        assert len(password) == 16
    
    def test_generate_exclude_similar(self):
        """Тест исключения похожих символов"""
        password = PasswordGenerator.generate(exclude_similar=True)
        similar = "il1Lo0O"
        assert not any(c in similar for c in password)
    
    def test_generate_include_similar(self):
        """Тест с включением похожих символов"""
        password = PasswordGenerator.generate(exclude_similar=False)
        # Не гарантируем, что будут, но проверяем что не исключены
        # Просто проверяем что пароль сгенерировался
        assert len(password) == 16
    
    def test_generate_invalid_length(self):
        """Тест генерации с неверной длиной"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=0)
        
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=-5)
    
    def test_generate_no_characters(self):
        """Тест: ошибка если не выбраны символы"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(
                use_lowercase=False,
                use_uppercase=False,
                use_digits=False,
                use_special=False
            )
    
    def test_generate_uniqueness(self):
        """Тест уникальности генерируемых паролей"""
        passwords = [PasswordGenerator.generate() for _ in range(50)]
        # Проверяем что есть разные пароли (вероятность коллизии крайне мала)
        assert len(set(passwords)) > 40
    
    def test_generate_meets_requirements(self):
        """Тест что сгенерированный пароль соответствует требованиям"""
        for _ in range(20):
            password = PasswordGenerator.generate(
                length=12,
                use_lowercase=True,
                use_uppercase=True,
                use_digits=True,
                use_special=True
            )
            
            # Проверка через внутренний метод
            assert PasswordGenerator._meets_requirements(
                password,
                use_lowercase=True,
                use_uppercase=True,
                use_digits=True,
                use_special=True
            )
    
    def test_generate_special_characters(self):
        """Тест что используются все специальные символы"""
        password = PasswordGenerator.generate(
            length=100,
            use_lowercase=True,
            use_uppercase=True,
            use_digits=True,
            use_special=True
        )
        
        # Проверяем что есть хотя бы несколько разных спецсимволов
        special_chars = [c for c in password if c in PasswordGenerator.SPECIAL]
        assert len(set(special_chars)) >= 3  # Как минимум 3 разных