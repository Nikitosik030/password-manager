"""Тесты для оценки стойкости паролей"""
import pytest
from src.password_strength import PasswordStrengthAnalyzer


class TestPasswordStrength:
    """Тестирование анализа стойкости паролей"""
    
    def test_calculate_entropy_simple(self):
        """Тест расчета энтропии простого пароля"""
        analyzer = PasswordStrengthAnalyzer()
        
        # Пароль из одинаковых символов - низкая энтропия
        weak = "aaaaaa"
        entropy = analyzer.calculate_entropy(weak)
        assert entropy < 5
        
        # Пароль с разными символами - выше энтропия
        strong = "P@ssw0rd"
        entropy = analyzer.calculate_entropy(strong)
        assert entropy > 20
    
    def test_calculate_entropy_empty(self):
        """Тест энтропии пустого пароля"""
        analyzer = PasswordStrengthAnalyzer()
        assert analyzer.calculate_entropy("") == 0.0
    
    def test_calculate_entropy_repeated(self):
        """Тест энтропии с повторяющимися символами"""
        analyzer = PasswordStrengthAnalyzer()
        
        # "123456" - низкая энтропия
        entropy1 = analyzer.calculate_entropy("123456")
        
        # "1234567890" - чуть выше (больше символов)
        entropy2 = analyzer.calculate_entropy("1234567890")
        
        assert entropy2 > entropy1
    
    def test_get_character_set_size(self):
        """Тест определения размера набора символов"""
        analyzer = PasswordStrengthAnalyzer()
        
        # Только строчные
        assert analyzer.get_character_set_size("abc") == 26
        
        # Только заглавные
        assert analyzer.get_character_set_size("ABC") == 26
        
        # Строчные + заглавные
        assert analyzer.get_character_set_size("abcABC") == 52
        
        # Строчные + цифры
        assert analyzer.get_character_set_size("abc123") == 36
        
        # Все типы
        assert analyzer.get_character_set_size("Abc123!@#") == 94  # 26+26+10+32
    
    def test_classify_strength_weak(self):
        """Тест классификации слабого пароля"""
        analyzer = PasswordStrengthAnalyzer()
        result = analyzer.classify_strength("123456")
        
        assert result['strength'] in ["Очень слабый", "Слабый"]
        assert len(result['warnings']) > 0
        assert result['length'] == 6
    
    def test_classify_strength_strong(self):
        """Тест классификации сильного пароля"""
        analyzer = PasswordStrengthAnalyzer()
        result = analyzer.classify_strength("MyStr0ngP@ssw0rd!2024")
        
        assert result['strength'] in ["Сильный", "Очень сильный"]
        assert result['length'] > 15
    
    def test_classify_strength_warnings(self):
        """Тест предупреждений для слабого пароля"""
        analyzer = PasswordStrengthAnalyzer()
        result = analyzer.classify_strength("abc")
        
        # Должны быть предупреждения о:
        # - короткой длине (< 8)
        # - отсутствии заглавных
        # - отсутствии цифр
        # - отсутствии спецсимволов
        assert len(result['warnings']) >= 3
        assert any("короткий" in w.lower() for w in result['warnings'])
        assert any("заглавных" in w.lower() for w in result['warnings'])
    
    def test_classify_strength_edge_cases(self):
        """Тест граничных случаев"""
        analyzer = PasswordStrengthAnalyzer()
        
        # Пустой пароль
        result = analyzer.classify_strength("")
        assert result['strength'] == "Очень слабый"
        assert result['entropy'] == 0.0
        
        # Очень длинный пароль
        long_password = "A" * 100 + "b" * 100 + "1" * 100 + "!" * 100
        result = analyzer.classify_strength(long_password)
        assert result['strength'] in ["Сильный", "Очень сильный"]
    
    def test_classify_strength_medium(self):
        """Тест классификации среднего пароля"""
        analyzer = PasswordStrengthAnalyzer()
        result = analyzer.classify_strength("Password123")
        
        # Должен быть как минимум средний
        assert result['strength'] in ["Средний", "Сильный"]
        assert result['length'] >= 8
        
    def test_entropy_consistency(self):
        """Тест согласованности расчета энтропии"""
        analyzer = PasswordStrengthAnalyzer()
        
        # Одинаковые пароли дают одинаковую энтропию
        e1 = analyzer.calculate_entropy("Test123!@#")
        e2 = analyzer.calculate_entropy("Test123!@#")
        assert e1 == e2
        
        # Разные пароли должны давать разную энтропию
        e3 = analyzer.calculate_entropy("AnotherPass456")
        # Не гарантируем что разная, но проверяем что хоть что-то считается
        assert e3 > 0