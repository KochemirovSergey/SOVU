from functools import wraps
from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user

def admin_required(f):
    """
    Декоратор для проверки, является ли пользователь администратором
    
    Args:
        f: Функция, которую нужно обернуть
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def token_required(f):
    """
    Декоратор для проверки наличия токена в запросе
    
    Args:
        f: Функция, которую нужно обернуть
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            flash('Отсутствует токен доступа', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def validate_token(token, model, token_field='link_token'):
    """
    Проверка валидности токена
    
    Args:
        token (str): Токен для проверки
        model: Модель данных
        token_field (str): Поле с токеном в модели
        
    Returns:
        object: Объект модели, если токен валидный, иначе None
    """
    if not token:
        return None
        
    # Формируем запрос
    query = {token_field: token}
    obj = model.query.filter_by(**query).first()
    
    return obj

def generate_password_hash(password):
    """
    Генерация хеша пароля
    
    Args:
        password (str): Пароль
        
    Returns:
        str: Хеш пароля
    """
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def check_password_hash(password_hash, password):
    """
    Проверка пароля
    
    Args:
        password_hash (str): Хеш пароля
        password (str): Пароль для проверки
        
    Returns:
        bool: Результат проверки
    """
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)