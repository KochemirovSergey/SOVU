from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from models import db
from models.teacher import Teacher, TeacherSchool
from models.school import School
from models.application import Application
from services.link_service import LinkService
from ai.document_analyzer import DocumentAnalyzer

teacher_bp = Blueprint('teacher_panel', __name__)

@teacher_bp.route('/self_register_success', endpoint='self_register_success')
def self_register_success():
    return render_template('teacher/self_register_success.html')

# Сервисы
link_service = LinkService()
document_analyzer = DocumentAnalyzer()

def allowed_file(filename):
    """Проверка допустимого расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@teacher_bp.route('/school/<school_token>', methods=['GET', 'POST'])
def self_register(school_token):
    """
    Форма для самостоятельного заполнения учителем по ссылке для школы.
    """
    from models.application import Application
    from forms.teacher_forms import TeacherSelfRegisterForm
    application = Application.query.filter_by(school_link_token=school_token).first_or_404()
    school = application.school

    form = TeacherSelfRegisterForm()

    if form.validate_on_submit():
        from services.link_service import LinkService
        import uuid
        link_service = LinkService()
        teacher = Teacher(
            full_name=form.full_name.data,
            link_token=link_service.generate_token()
        )
        db.session.add(teacher)
        db.session.flush()

        # Обработка загрузки подтверждающего документа
        file = form.confirm_document.data
        if file:
            try:
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                documents_dir = os.path.join('static', 'documents')
                # Убедимся, что директория существует
                os.makedirs(documents_dir, exist_ok=True)
                file_path = os.path.join(documents_dir, unique_filename)
                file.save(file_path)
                # Сохраняем относительный путь для использования в шаблонах/БД
                teacher.document_path = os.path.join('documents', unique_filename)
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при загрузке файла: {str(e)}', 'danger')
                return render_template('teacher/self_register.html', school=school, form=form)

        teacher_school = TeacherSchool(
            teacher_id=teacher.id,
            school_id=school.id,
            start_year=form.start_year.data,
            end_year=form.end_year.data,
            subjects=form.subjects.data
        )
        db.session.add(teacher_school)
        db.session.commit()

        flash('Информация успешно сохранена!', 'success')
        return redirect(url_for('teacher_panel.self_register_success'))

    if request.method == 'POST' and not form.validate():
        flash('Пожалуйста, заполните все обязательные поля корректно', 'danger')

    return render_template('teacher/self_register.html', school=school, form=form)

@teacher_bp.route('/<token>', methods=['GET', 'POST'], endpoint='form')
def form(token):
    """Форма для заполнения информации о местах работы"""
    print(f"[DEBUG] Получен токен учителя: {token}")
    teacher = Teacher.query.filter_by(link_token=token).first()
    if teacher:
        print(f"[DEBUG] Учитель найден: id={teacher.id}, full_name={teacher.full_name}")
    else:
        print("[DEBUG] Учитель с таким токеном не найден!")
        from flask import abort
        abort(404)
    
    if request.method == 'POST':
        # Получаем данные о школах из формы
        school_names = request.form.getlist('school_name')
        school_start_years = request.form.getlist('start_year')
        school_end_years = request.form.getlist('end_year')
        school_subjects = request.form.getlist('subjects')
        
        # Проверяем, что все списки имеют одинаковую длину
        if len(school_names) != len(school_start_years) or len(school_names) != len(school_end_years) or len(school_names) != len(school_subjects):
            flash('Ошибка при обработке данных', 'danger')
            return render_template('teacher/form.html', teacher=teacher)
        
        # Обрабатываем каждую школу
        for i in range(len(school_names)):
            if not school_names[i]:
                continue
                
            # Ищем школу по названию
            school = School.query.filter_by(name=school_names[i]).first()
            
            if not school:
                # Создаем новую школу
                school = School(name=school_names[i])
                db.session.add(school)
                db.session.flush()  # Получаем ID школы
            
            # Создаем связь учителя со школой
            teacher_school = TeacherSchool(
                teacher_id=teacher.id,
                school_id=school.id,
                start_year=school_start_years[i],
                end_year=school_end_years[i],
                subjects=school_subjects[i]
            )
            db.session.add(teacher_school)
        
        db.session.commit()
        flash('Информация о местах работы успешно сохранена', 'success')
        return redirect(url_for('teacher_panel.document', token=token))
    
    return render_template('teacher/form.html', teacher=teacher)

@teacher_bp.route('/<token>/document', methods=['GET', 'POST'])
def document(token):
    """Загрузка подтверждающего документа"""
    teacher = Teacher.query.filter_by(link_token=token).first_or_404()
    
    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'document' not in request.files:
            flash('Не выбран файл', 'danger')
            return redirect(request.url)
            
        file = request.files['document']
        
        # Если пользователь не выбрал файл
        if file.filename == '':
            flash('Не выбран файл', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Создаем уникальное имя файла
            unique_filename = f"{teacher.id}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Сохраняем путь к документу
            teacher.document_path = file_path
            
            # Анализируем документ
            teacher_data = {
                'full_name': teacher.full_name,
                'schools': [{'name': ts.school.name, 'start_year': ts.start_year, 'end_year': ts.end_year, 'subjects': ts.subjects} for ts in teacher.schools]
            }
            
            verification_score = document_analyzer.analyze_document(file_path, teacher_data)
            teacher.verification_score = verification_score
            
            db.session.commit()
            
            flash('Документ успешно загружен и проанализирован', 'success')
            return render_template('teacher/thank_you.html', verification_score=verification_score)
    
    return render_template('teacher/document.html', teacher=teacher)