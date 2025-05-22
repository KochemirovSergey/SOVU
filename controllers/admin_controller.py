from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.graduate import Graduate
from models.school import School
from models.teacher import Teacher, TeacherSchool
from models.application import Application
from services.link_service import LinkService
from services.document_service import DocumentService
from utils.auth import admin_required
from forms.admin_forms import GraduateForm, ApplicationFilterForm, ApplicationStatusForm, ApplicationForm
from forms.teacher_forms import TeacherSelfRegisterForm

admin_bp = Blueprint('admin_panel', __name__)

# Сервисы
link_service = LinkService()
document_service = DocumentService()

@admin_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    """Главная страница административной панели"""
    graduates_count = Graduate.query.count()
    schools_count = School.query.count()
    teachers_count = Teacher.query.count()
    applications_count = Application.query.count()
    
    return render_template('admin/index.html', 
                          graduates_count=graduates_count,
                          schools_count=schools_count,
                          teachers_count=teachers_count,
                          applications_count=applications_count)

@admin_bp.route('/graduates', methods=['GET', 'POST'])
@login_required
@admin_required
def graduates():
    """Управление выпускниками"""
    form = GraduateForm()
    if form.validate_on_submit():
        graduate = Graduate(full_name=form.full_name.data)
        # Генерация токена для ссылки
        graduate.link_token = link_service.generate_token()
        db.session.add(graduate)
        db.session.commit()
        flash('Выпускник успешно добавлен', 'success')
        return redirect(url_for('admin_panel.graduates'))
    
    graduates = Graduate.query.all()
    return render_template('admin/graduates.html', graduates=graduates, form=form)

@admin_bp.route('/graduates/<int:id>/link', methods=['GET'])
@login_required
@admin_required
def graduate_link(id):
    """Получение ссылки для выпускника"""
    graduate = Graduate.query.get_or_404(id)
    link = link_service.generate_graduate_link(graduate.id)
    return render_template('admin/graduate_link.html', graduate=graduate, link=link)

@admin_bp.route('/graduates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def graduate_edit(id):
    """Редактирование выпускника"""
    graduate = Graduate.query.get_or_404(id)
    form = GraduateForm(obj=graduate)
    
    if form.validate_on_submit():
        form.populate_obj(graduate)
        db.session.commit()
        flash('Данные выпускника обновлены', 'success')
        return redirect(url_for('admin.graduates'))
    
    return render_template('admin/graduate_edit.html', form=form, graduate=graduate)

@admin_bp.route('/graduates/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def graduate_delete(id):
    """Удаление выпускника"""
    graduate = Graduate.query.get_or_404(id)
    db.session.delete(graduate)
    db.session.commit()
    flash('Выпускник удален', 'success')
    return redirect(url_for('admin_panel.graduates'))

@admin_bp.route('/graduates/<int:id>', methods=['GET'])
@login_required
@admin_required
def graduate_detail(id):
    """Детальная информация о выпускнике"""
    graduate = Graduate.query.get_or_404(id)
    return render_template('admin/graduate_detail.html', graduate=graduate)

@admin_bp.route('/applications', methods=['GET'])
@login_required
@admin_required
def applications():
    """Просмотр всех заявок"""
    form = ApplicationFilterForm()
    status_filter = request.args.get('status', 'all')
    
    if status_filter and status_filter != 'all':
        applications = Application.query.filter_by(status=status_filter).all()
    else:
        applications = Application.query.all()
    
    return render_template('admin/applications.html',
                          applications=applications,
                          form=form,
                          current_status=status_filter)

@admin_bp.route('/applications/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def application_detail(id):
    """Просмотр и редактирование заявки"""
    application = Application.query.get_or_404(id)
    form = ApplicationStatusForm(obj=application)
    
    if form.validate_on_submit():
        application.status = form.status.data
        db.session.commit()
        flash('Статус заявки обновлен', 'success')
        return redirect(url_for('admin.application_detail', id=application.id))
    
    return render_template('admin/application_detail.html',
                          application=application,
                          form=form)

@admin_bp.route('/applications/<int:id>/document', methods=['GET', 'POST'])
@login_required
@admin_required
def application_document(id):
    """Генерация и редактирование письма запроса"""
    application = Application.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'generate' in request.form:
            # Генерация документа
            document_path = document_service.generate_school_request(application.id)
            application.document_path = document_path
            db.session.commit()
            flash('Документ успешно сгенерирован', 'success')
    
    return render_template('admin/application_document.html', application=application)

@admin_bp.route('/schools', methods=['GET'])
@login_required
@admin_required
def schools():
    """Просмотр всех школ"""
    schools = School.query.all()
    return render_template('admin/schools.html', schools=schools)

@admin_bp.route('/teachers', methods=['GET'])
@login_required
@admin_required
def teachers():
    """Просмотр всех учителей"""
    teachers = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers)
@admin_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
@admin_required
def teacher_delete(teacher_id):
    """Удаление учителя с учётом зависимостей"""
    from sqlalchemy.exc import IntegrityError
    teacher = Teacher.query.get_or_404(teacher_id)
    try:
        # Удаляем связанные записи TeacherSchool
        for ts in teacher.schools:
            db.session.delete(ts)
        # Удаляем связанные голоса
        for vote in teacher.votes:
            db.session.delete(vote)
        db.session.delete(teacher)
        db.session.commit()
        flash('Учитель и связанные данные удалены', 'success')
    except IntegrityError as e:
        db.session.rollback()
        flash('Ошибка удаления: есть связанные объекты, которые нельзя удалить. Обратитесь к администратору.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Не удалось удалить учителя: {str(e)}', 'danger')
    return redirect(url_for('admin_panel.teachers'))

@admin_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def teacher_edit(teacher_id):
    """Редактирование учителя"""
    teacher = Teacher.query.get_or_404(teacher_id)
    # Получаем TeacherSchool (первую, если их несколько)
    teacher_school = TeacherSchool.query.filter_by(teacher_id=teacher.id).first()
    if not teacher_school:
        flash('Не найдена информация о школе для этого учителя', 'danger')
        return redirect(url_for('admin_panel.teachers'))

    # Для GET: передаём данные из обеих моделей в форму
    if request.method == 'GET':
        form = TeacherSelfRegisterForm(
            full_name=teacher.full_name,
            subjects=teacher_school.subjects,
            start_year=teacher_school.start_year,
            end_year=teacher_school.end_year
        )
    else:
        form = TeacherSelfRegisterForm()

    if form.validate_on_submit():
        teacher.full_name = form.full_name.data
        teacher_school.subjects = form.subjects.data
        teacher_school.start_year = form.start_year.data
        teacher_school.end_year = form.end_year.data
        db.session.commit()
        flash('Данные учителя обновлены', 'success')
        return redirect(url_for('admin_panel.teachers'))

    return render_template('teacher/form.html', form=form, teacher=teacher)