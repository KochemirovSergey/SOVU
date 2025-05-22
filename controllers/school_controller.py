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
            return render_template('school/form.html', application=application, school=school)
        
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
        return render_template('school/thank_you.html')
    
    return render_template('school/form.html', application=application, school=school)

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