from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash, request

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Настройка Flask-Admin
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
        
    def inaccessible_callback(self, name, **kwargs):
        flash('Пожалуйста, войдите для доступа к этой странице.', 'danger')
        return redirect(url_for('auth.login', next=request.url))

class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Пожалуйста, войдите для доступа к этой странице.', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        return super(SecureAdminIndexView, self).index()

admin = Admin(
    name='Система сбора информации', 
    template_mode='bootstrap4',
    index_view=SecureAdminIndexView()
)