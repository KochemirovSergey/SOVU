import re
from datetime import datetime

def validate_email(email):
    """
    Валидация email
    
    Args:
        email (str): Email для проверки
        
    Returns:
        bool: Результат проверки
    """
    if not email:
        return False
        
    # Простая проверка формата email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_inn(inn):
    """
    Валидация ИНН
    
    Args:
        inn (str): ИНН для проверки
        
    Returns:
        bool: Результат проверки
    """
    if not inn:
        return False
        
    # Проверка длины ИНН (10 цифр для организаций, 12 для физических лиц)
    if len(inn) not in (10, 12):
        return False
        
    # Проверка, что ИНН состоит только из цифр
    if not inn.isdigit():
        return False
        
    return True

def validate_year(year):
    """
    Валидация года
    
    Args:
        year (int): Год для проверки
        
    Returns:
        bool: Результат проверки
    """
    try:
        year = int(year)
        current_year = datetime.now().year
        
        # Проверка, что год находится в разумных пределах
        return 1900 <= year <= current_year
    except (ValueError, TypeError):
        return False

def validate_grade(grade):
    """
    Валидация класса
    
    Args:
        grade (int): Класс для проверки
        
    Returns:
        bool: Результат проверки
    """
    try:
        grade = int(grade)
        
        # Проверка, что класс находится в пределах от 1 до 11
        return 1 <= grade <= 11
    except (ValueError, TypeError):
        return False

def validate_period(start_year, end_year, start_grade, end_grade):
    """
    Валидация периода обучения
    
    Args:
        start_year (int): Год начала
        end_year (int): Год окончания
        start_grade (int): Класс начала
        end_grade (int): Класс окончания
        
    Returns:
        bool: Результат проверки
    """
    try:
        start_year = int(start_year)
        end_year = int(end_year)
        start_grade = int(start_grade)
        end_grade = int(end_grade)
        
        # Проверка, что год окончания не раньше года начала
        if end_year < start_year:
            return False
            
        # Проверка, что класс окончания не раньше класса начала
        if end_grade < start_grade:
            return False
            
        # Проверка согласованности периода
        years_diff = end_year - start_year
        grades_diff = end_grade - start_grade
        
        # Разница в годах должна быть примерно равна разнице в классах
        return years_diff == grades_diff
    except (ValueError, TypeError):
        return False

def validate_full_name(full_name):
    """
    Валидация ФИО
    
    Args:
        full_name (str): ФИО для проверки
        
    Returns:
        bool: Результат проверки
    """
    if not full_name:
        return False
        
    # Проверка минимальной длины
    if len(full_name) < 5:
        return False
        
    # Проверка, что ФИО содержит хотя бы два слова
    words = full_name.split()
    if len(words) < 2:
        return False
        
    return True