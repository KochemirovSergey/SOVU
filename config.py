import os
from datetime import timedelta

class Config:
    # Базовая конфигурация
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки для Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Настройки для загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    
    # Настройки для QR-кодов
    QR_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/qr')
    
    # Настройки для API
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Настройки для приложения
    BASE_URL = os.environ.get('BASE_URL') or 'http://127.0.0.1:5000'
    
    @staticmethod
    def init_app(app):
        # Создаем необходимые директории, если они не существуют
        
        # Настройки безопасности
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = False
        app.config['REMEMBER_COOKIE_HTTPONLY'] = True
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.QR_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    # В продакшене используем более надежную базу данных
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}