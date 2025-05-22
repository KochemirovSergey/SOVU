from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.school import School
from models.teacher import Teacher, TeacherSchool
from models.application import Application
from services.link_service import LinkService

school_bp = Blueprint('school_panel', __name__)

# Сервисы
link_service = LinkService()

@school_bp.route('/<token>', methods=['GET', 'POST'])
def form(token):
    """Форма для заполнения информации об учителях"""
    # Находим заявку по токену
    application = Application.query.filter_by(school_link_token=token).first_or_404()
    school = application.school

    # Получаем учителей и заявки, связанные с данной школой
    # Формируем список учителей с предметами и периодами работы в этой школе
    teacher_objs = Teacher.query.join(TeacherSchool).filter(TeacherSchool.school_id == school.id).all()
    teachers = []
    for teacher in teacher_objs:
        # Все связи учителя с этой школой
        ts_links = TeacherSchool.query.filter_by(teacher_id=teacher.id, school_id=school.id).all()
        # Собираем все предметы (разделяем по запятым, убираем дубли)
        all_subjects = []
        periods = []
        for ts in ts_links:
            if ts.subjects:
                all_subjects.extend([s.strip() for s in ts.subjects.split(',') if s.strip()])
            periods.append(f"{ts.start_year}–{ts.end_year}")
        # Убираем дубли и сортируем предметы
        unique_subjects = sorted(set(all_subjects))
        teachers.append({
            'full_name': teacher.full_name,
            'subjects': ', '.join(unique_subjects) if unique_subjects else '',
            'periods': periods
        })
    applications = Application.query.filter_by(school_id=school.id).all()

    # Формируем список словарей для шаблона с нужными полями по каждой заявке
    application_dicts = []
    for app in applications:
        grad = app.graduate
        application_dicts.append({
            'id': app.id,
            'graduate_full_name': grad.full_name if grad else '',
            'start_year': app.start_year,
            'end_year': app.end_year,
            'start_grade': app.start_grade,
            'end_grade': app.end_grade,
            'status': app.status,
        })

    if request.method == 'POST':
        print('DEBUG POST request.form:', request.form)
        print('DEBUG POST request.values:', request.values)
        # Получаем данные о учителях из формы
        teacher_names = request.form.getlist('teacher_name')
        teacher_subjects = request.form.getlist('teacher_subjects')
        teacher_start_years = request.form.getlist('teacher_start_year')
        teacher_end_years = request.form.getlist('teacher_end_year')
        
        # Проверяем, что все списки имеют одинаковую длину
        if len(teacher_names) != len(teacher_subjects) or len(teacher_names) != len(teacher_start_years) or len(teacher_names) != len(teacher_end_years):
            flash('Ошибка при обработке данных', 'danger')
            return render_template(
                'school/form.html',
                application=application,
                school=school,
                teachers=teachers,
                applications=application_dicts
            )
        
        # Обрабатываем каждого учителя
        for i in range(len(teacher_names)):
            if not teacher_names[i]:
                continue
                
            # Создаем нового учителя
            generated_token = link_service.generate_token()
            teacher = Teacher(
                full_name=teacher_names[i],
                link_token=generated_token
            )
            db.session.add(teacher)
            db.session.flush()  # Получаем ID учителя
            print(f"[DEBUG] Создан учитель: id={teacher.id}, full_name={teacher.full_name}, link_token={teacher.link_token}")
            
            # Создаем связь учителя со школой
            teacher_school = TeacherSchool(
                teacher_id=teacher.id,
                school_id=school.id,
                start_year=teacher_start_years[i],
                end_year=teacher_end_years[i],
                subjects=teacher_subjects[i]
            )
            db.session.add(teacher_school)
        
        # Обновляем статус заявки
        application.status = 'completed'
        db.session.commit()
        
        flash('Информация об учителях успешно сохранена', 'success')
        return redirect(url_for('school_panel.form', token=token))
    
    return render_template(
        'school/form.html',
        application=application,
        school=school,
        teachers=teachers,
        applications=application_dicts
    )

@school_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    """Обновление информации о школе"""
    school = School.query.get_or_404(id)
    
    if request.method == 'POST':
        school.name = request.form.get('name')
        school.full_name = request.form.get('full_name')
        school.address = request.form.get('address')
        school.inn = request.form.get('inn')
        school.director = request.form.get('director')
        school.email = request.form.get('email')
        school.status = request.form.get('status')
        
        db.session.commit()
        flash('Информация о школе обновлена', 'success')
        return redirect(url_for('school_panel.update', id=school.id))
    
    return render_template('school/update.html', school=school)