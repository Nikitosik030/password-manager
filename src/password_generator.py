"""Генератор безопасных паролей"""
import secrets
import string
import re


class PasswordGenerator:
    """Генерация случайных паролей"""
    
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{};:'\",.<>/?\\|`~"
    
    @staticmethod
    def generate(
        length: int = 16,
        use_lowercase: bool = True,
        use_uppercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_similar: bool = True
    ) -> str:
        """Генерация безопасного пароля"""
        if length < 1:
            raise ValueError("Длина пароля должна быть больше 0")
        
        # Сбор доступных символов
        chars = ""
        if use_lowercase:
            chars += PasswordGenerator.LOWERCASE
        if use_uppercase:
            chars += PasswordGenerator.UPPERCASE
        if use_digits:
            chars += PasswordGenerator.DIGITS
        if use_special:
            chars += PasswordGenerator.SPECIAL
        
        if not chars:
            raise ValueError("Не выбрано ни одного набора символов")
        
        # Исключение похожих символов
        if exclude_similar:
            similar = "il1Lo0O"
            chars = ''.join(c for c in chars if c not in similar)
        
        # Генерация пароля
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Проверка, что пароль содержит все выбранные типы символов
        attempts = 0
        while attempts < 100:
            if PasswordGenerator._meets_requirements(
                password, use_lowercase, use_uppercase, use_digits, use_special
            ):
                return password
            
            # Перегенерация одного символа
            pos = secrets.randbelow(length)
            password = password[:pos] + secrets.choice(chars) + password[pos+1:]
            attempts += 1
        
        return password
    
    @staticmethod
    def _meets_requirements(
        password: str,
        use_lowercase: bool,
        use_uppercase: bool,
        use_digits: bool,
        use_special: bool
    ) -> bool:
        """Проверка соответствия пароля требованиям"""
        if use_lowercase and not re.search(r'[a-z]', password):
            return False
        if use_uppercase and not re.search(r'[A-Z]', password):
            return False
        if use_digits and not re.search(r'[0-9]', password):
            return False
        if use_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
            return False
        return True