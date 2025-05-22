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
@teacher_bp.route('/application/<token>', methods=['GET', 'POST'])
def application_form(token):
    """
    Форма для заполнения информации учителем по ссылке из заявки (teacher_link_token).
    """
    application = Application.query.filter_by(teacher_link_token=token).first_or_404()
    school = application.school
    graduate = application.graduate

    if request.method == 'POST':
        # Пример: учитель может заполнить ФИО, предмет, годы работы и т.д.
        # Здесь можно добавить обработку данных формы, например:
        teacher_full_name = request.form.get('teacher_full_name')
        teacher_subject = request.form.get('teacher_subject')
        teacher_start_year = request.form.get('teacher_start_year')
        teacher_end_year = request.form.get('teacher_end_year')
        # Здесь можно создать Teacher и TeacherSchool, связав их с school и application
        if teacher_full_name and teacher_subject and teacher_start_year and teacher_end_year:
            teacher = Teacher(full_name=teacher_full_name)
            db.session.add(teacher)
            db.session.commit()
            teacher_school = TeacherSchool(
                teacher_id=teacher.id,
                school_id=school.id,
                start_year=teacher_start_year,
                end_year=teacher_end_year,
                subject=teacher_subject
            )
            db.session.add(teacher_school)
            db.session.commit()
            flash('Данные учителя успешно сохранены', 'success')
            return redirect(url_for('teacher_panel.application_form', token=token))
        else:
            flash('Пожалуйста, заполните все поля', 'danger')

    return render_template(
        'teacher/application_form.html',
        application=application,
        school=school,
        graduate=graduate
    )

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
    application = Application.query.filter_by(school_link_token=school_token).first_or_404()
    school = application.school

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        subjects = request.form.get('subjects')
        start_year = request.form.get('start_year')
        end_year = request.form.get('end_year')

        if not full_name or not subjects or not start_year or not end_year:
            flash('Пожалуйста, заполните все обязательные поля', 'danger')
            return render_template('teacher/self_register.html', school=school)

        # Создаём учителя
        from services.link_service import LinkService
        link_service = LinkService()
        teacher = Teacher(
            full_name=full_name,
            email=email,
            link_token=link_service.generate_token()
        )
        db.session.add(teacher)
        db.session.flush()

        # Связываем учителя со школой
        teacher_school = TeacherSchool(
            teacher_id=teacher.id,
            school_id=school.id,
            start_year=start_year,
            end_year=end_year,
            subjects=subjects
        )
        db.session.add(teacher_school)
        db.session.commit()

        flash('Информация успешно сохранена!', 'success')
        return render_template('teacher/thank_you.html', teacher=teacher, school=school)

    return render_template('teacher/self_register.html', school=school)
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