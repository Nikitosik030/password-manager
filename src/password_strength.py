"""Оценка стойкости паролей по энтропии"""
import math
import re


class PasswordStrengthAnalyzer:
    """Анализ стойкости паролей"""
    
    @staticmethod
    def calculate_entropy(password: str) -> float:
        """Расчет энтропии по Шеннону"""
        if not password:
            return 0.0
        
        freq = {}
        for char in password:
            freq[char] = freq.get(char, 0) + 1
        
        length = len(password)
        entropy = 0.0
        
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy * length
    
    @staticmethod
    def get_character_set_size(password: str) -> int:
        """Определение размера набора символов"""
        size = 0
        if re.search(r'[a-z]', password):
            size += 26
        if re.search(r'[A-Z]', password):
            size += 26
        if re.search(r'[0-9]', password):
            size += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
            size += 32
        return size
    
    @staticmethod
    def classify_strength(password: str) -> dict:
        """Классификация стойкости пароля"""
        entropy = PasswordStrengthAnalyzer.calculate_entropy(password)
        
        # Классификация
        if entropy >= 80:
            strength = "Очень сильный"
        elif entropy >= 60:
            strength = "Сильный"
        elif entropy >= 40:
            strength = "Средний"
        elif entropy >= 20:
            strength = "Слабый"
        else:
            strength = "Очень слабый"
        
        # Предупреждения
        warnings = []
        if len(password) < 8:
            warnings.append("Пароль слишком короткий (< 8 символов)")
        if not re.search(r'[A-Z]', password):
            warnings.append("Нет заглавных букв")
        if not re.search(r'[a-z]', password):
            warnings.append("Нет строчных букв")
        if not re.search(r'[0-9]', password):
            warnings.append("Нет цифр")
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
            warnings.append("Нет специальных символов")
        
        return {
            'entropy': round(entropy, 2),
            'strength': strength,
            'warnings': warnings,
            'length': len(password)
        }