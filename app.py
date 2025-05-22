from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
import pandas as pd
import os
import traceback

from config import config
from llm_search_school import get_school_info
from extensions import db, login_manager, csrf, admin, SecureModelView

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)
    
    # Дополнительные настройки для CSRF-защиты
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # Отключаем ограничение по времени для CSRF-токена
    
    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Импорт моделей для Flask-Login
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Загрузка пользователя для Flask-Login"""
        return User.query.get(int(user_id))
    
    # Регистрация моделей в админке
    from models.graduate import Graduate, GraduateSchool, Vote
    from models.school import School
    from models.teacher import Teacher, TeacherSchool
    from models.application import Application
    
    admin.add_view(SecureModelView(Graduate, db.session, name='Выпускники', category='Модели'))
    admin.add_view(SecureModelView(School, db.session, name='Школы', category='Модели'))
    admin.add_view(SecureModelView(Teacher, db.session, name='Учителя', category='Модели'))
    admin.add_view(SecureModelView(Application, db.session, name='Заявки', category='Модели'))
    admin.add_view(SecureModelView(User, db.session, name='Пользователи', category='Администрирование'))
    admin.add_view(SecureModelView(GraduateSchool, db.session, name='Школы выпускников', category='Связи'))
    admin.add_view(SecureModelView(TeacherSchool, db.session, name='Школы учителей', category='Связи'))
    admin.add_view(SecureModelView(Vote, db.session, name='Голоса', category='Связи'))
    
    # Регистрация чертежей (blueprints)
    from controllers.admin_controller import admin_bp
    from controllers.graduate_controller import graduate_bp
    from controllers.school_controller import school_bp
    from controllers.teacher_controller import teacher_bp
    from controllers.auth_controller import auth_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin_panel')
    app.register_blueprint(graduate_bp, url_prefix='/graduate_panel')
    app.register_blueprint(school_bp, url_prefix='/school_panel')
    app.register_blueprint(teacher_bp, url_prefix='/teacher_panel')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Маршрут для главной страницы
    @app.route('/', methods=['GET'])
    def index():
        # Главная страница административной панели с передачей статистики
        from models.graduate import Graduate
        from models.school import School
        from models.teacher import Teacher
        from models.application import Application

        graduates_count = Graduate.query.count()
        schools_count = School.query.count()
        teachers_count = Teacher.query.count()
        applications_count = Application.query.count()

        return render_template(
            'admin/index.html',
            graduates_count=graduates_count,
            schools_count=schools_count,
            teachers_count=teachers_count,
            applications_count=applications_count
        )
    
    # Маршрут для поиска информации о школе
    @app.route('/search', methods=['POST'])
    def search():
        try:
            if not request.is_json:
                return jsonify({'error': 'Неверный формат данных. Ожидается JSON.'}), 400
                
            data = request.get_json()
            
            if not isinstance(data, dict):
                return jsonify({'error': 'Неверный формат данных'}), 400
                
            city = data.get('city')
            school_name = data.get('school')
            
            if not city or not school_name:
                return jsonify({'error': 'Пожалуйста, выберите город и введите название школы'})
            
            # Извлекаем название города из строки формата "Город (Регион)"
            city = city.split(' (')[0]
            
            # Получаем информацию о школе
            basic_info, detailed_info = get_school_info(city, school_name)
            
            # Преобразуем объекты в словари
            result = {
                'basic': {
                    'name': basic_info.name,
                    'status': basic_info.status,
                    'successor': basic_info.successor
                },
                'detailed': {
                    'full_name': detailed_info.full_name,
                    'address': detailed_info.address,
                    'inn': detailed_info.inn,
                    'director': detailed_info.director,
                    'email': detailed_info.email
                }
            }
            
            return jsonify(result)
            
        except Exception as e:
            print("Произошла ошибка:", str(e))
            print("Traceback:", traceback.format_exc())
            return jsonify({'error': f'Произошла ошибка при поиске информации: {str(e)}'}), 500
    
    # Обработчик ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    # Создание всех таблиц в базе данных
    with app.app_context():
        db.create_all()
        
        # Создание администратора по умолчанию, если его нет
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('Создан администратор по умолчанию (admin:admin123)')
    
    return app

# Создание экземпляра приложения
app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)