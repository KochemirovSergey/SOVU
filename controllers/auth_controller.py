from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from utils.auth import admin_required
from forms.auth_forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel.index'))
    
    # Для отладки
    print("Метод запроса:", request.method)
    if request.method == 'POST':
        print("Данные формы:", request.form)
        
    form = LoginForm()
    
    # Отключаем CSRF-защиту для отладки
    form.csrf_enabled = False
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin_panel.index')
            return redirect(next_page)
        flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    """Регистрация нового администратора (только для существующих администраторов)"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Администратор {form.username.data} успешно зарегистрирован', 'success')
        return redirect(url_for('admin_panel.index'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Профиль пользователя"""
    return render_template('auth/profile.html')