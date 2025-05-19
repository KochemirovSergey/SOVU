import os
import csv
import json
from datetime import datetime
from flask import current_app

def format_date(date):
    """
    Форматирование даты
    
    Args:
        date (datetime): Дата для форматирования
        
    Returns:
        str: Отформатированная дата
    """
    if not date:
        return ""
        
    return date.strftime("%d.%m.%Y")

def format_datetime(date):
    """
    Форматирование даты и времени
    
    Args:
        date (datetime): Дата для форматирования
        
    Returns:
        str: Отформатированная дата и время
    """
    if not date:
        return ""
        
    return date.strftime("%d.%m.%Y %H:%M")

def get_current_year():
    """
    Получение текущего года
    
    Returns:
        int: Текущий год
    """
    return datetime.now().year

def get_years_range(start_year, end_year=None):
    """
    Получение списка годов в диапазоне
    
    Args:
        start_year (int): Начальный год
        end_year (int, optional): Конечный год
        
    Returns:
        list: Список годов
    """
    if not end_year:
        end_year = get_current_year()
        
    return list(range(start_year, end_year + 1))

def get_grades_range():
    """
    Получение списка классов
    
    Returns:
        list: Список классов
    """
    return list(range(1, 12))

def load_cities_from_csv(file_path=None):
    """
    Загрузка списка городов из CSV файла
    
    Args:
        file_path (str, optional): Путь к CSV файлу
        
    Returns:
        list: Список городов с регионами
    """
    if not file_path:
        file_path = os.path.join(current_app.root_path, 'cities.csv')
        
    if not os.path.exists(file_path):
        return []
        
    cities = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cities.append({
                    'city': row.get('Город', ''),
                    'region': row.get('Регион', '')
                })
    except Exception as e:
        print(f"Ошибка при загрузке городов: {str(e)}")
        
    return cities

def save_to_json(data, file_path):
    """
    Сохранение данных в JSON файл
    
    Args:
        data: Данные для сохранения
        file_path (str): Путь к файлу
        
    Returns:
        bool: Результат операции
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении JSON: {str(e)}")
        return False

def load_from_json(file_path):
    """
    Загрузка данных из JSON файла
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        dict: Загруженные данные
    """
    if not os.path.exists(file_path):
        return {}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка при загрузке JSON: {str(e)}")
        return {}

def ensure_dir(directory):
    """
    Проверка существования директории и создание при необходимости
    
    Args:
        directory (str): Путь к директории
        
    Returns:
        bool: Результат операции
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return os.path.exists(directory)

def get_file_extension(filename):
    """
    Получение расширения файла
    
    Args:
        filename (str): Имя файла
        
    Returns:
        str: Расширение файла
    """
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename, allowed_extensions=None):
    """
    Проверка допустимости файла по расширению
    
    Args:
        filename (str): Имя файла
        allowed_extensions (set, optional): Допустимые расширения
        
    Returns:
        bool: Результат проверки
    """
    if not allowed_extensions:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
        
    return '.' in filename and get_file_extension(filename)[1:] in allowed_extensions