from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.school import School
from models.teacher import Teacher, TeacherSchool
from models.application import Application
from services.link_service import LinkService

from models.graduate import GraduateSchool

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
    teachers = TeacherSchool.query.filter_by(school_id=school.id).all()
    applications = Application.query.filter_by(school_id=school.id).all()

    # Формируем список словарей для шаблона с нужными полями по каждой заявке
    application_dicts = []
    for app in applications:
        grad = app.graduate
        # Получаем связку GraduateSchool только для выбранной пользователем школы (той, что указана у выпускника)
        gs = GraduateSchool.query.filter_by(graduate_id=app.graduate_id).first()
        application_dicts.append({
            'id': app.id,
            'graduate_id': app.graduate_id,
            'graduate_full_name': grad.full_name if grad else '',
            'start_year': app.start_year,
            'end_year': app.end_year,
            'status': app.status,
            'is_confirmed': gs.is_confirmed if gs else False,
            'graduate_school_id': gs.id if gs else None,
            'graduate_school_name': gs.school.name if gs and gs.school else '',
            'graduate_school_address': gs.school.address if gs and gs.school else '',
        })

    if request.method == 'POST':
        print('DEBUG POST request.form:', request.form)
        print('DEBUG POST request.values:', request.values)

        # Поддержка обоих вариантов: id и link_id
        link_id = request.form.get('link_id') or request.form.get('id')
        link_type = request.form.get('link_type')
        csrf_token = request.form.get('csrf_token')

        print(f"[form] Проверка параметров подтверждения: id={request.form.get('id')}, link_id={request.form.get('link_id')}, link_type={link_type}, csrf_token={csrf_token}")

        if link_id and link_type and csrf_token:
            print(f"[form] Получены параметры для подтверждения: link_id={link_id}, link_type={link_type}, csrf_token={csrf_token}")
            link_obj = None
            if link_type == 'teacher':
                link_obj = TeacherSchool.query.get(link_id)
            elif link_type == 'graduate':
                link_obj = GraduateSchool.query.get(link_id)
            else:
                print("[form] Некорректный тип связки:", link_type)
            if link_obj:
                print(f"[form] Найден объект: {link_obj} (is_confirmed={getattr(link_obj, 'is_confirmed', None)})")
                link_obj.is_confirmed = not link_obj.is_confirmed
                print(f"[form] Новое значение is_confirmed: {link_obj.is_confirmed}")
                db.session.commit()
                print("[form] Изменения сохранены в базе данных (db.session.commit())")
                flash('Статус подтверждения изменён', 'success')
            else:
                flash('Связка не найдена', 'danger')
            return redirect(url_for('school_panel.form', token=token))

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

@school_bp.route('/confirm_link', methods=['POST'])
def confirm_link():
    """
    Обработка POST-запроса для смены статуса подтверждения связки "Учитель-Школа" или "Выпускник-Школа".
    Ожидает: id (int), link_type ('teacher'/'graduate'), csrf_token, is_confirmed (bool).
    """
    from flask import abort

    link_id = request.form.get('id')
    link_type = request.form.get('link_type')
    csrf_token = request.form.get('csrf_token')
    # is_confirmed из формы не нужен, мы инвертируем текущее значение
    print(f"[confirm_link] Получены параметры формы: link_id={link_id}, link_type={link_type}, csrf_token={csrf_token}")

    # Проверка наличия обязательных параметров
    if not link_id or not link_type or not csrf_token:
        flash('Некорректные данные запроса', 'danger')
        return abort(400)

    # CSRF-проверка (если есть глобальная — будет работать, если нет — просто проверяем наличие)
    # Можно добавить свою функцию проверки, если требуется

    # Определяем модель по типу связки
    if link_type == 'teacher':
        link_obj = TeacherSchool.query.get(link_id)
    elif link_type == 'graduate':
        link_obj = GraduateSchool.query.get(link_id)
    else:
        flash('Некорректный тип связки', 'danger')
        return abort(400)

    print(f"[confirm_link] Найден объект: {link_obj} (is_confirmed={getattr(link_obj, 'is_confirmed', None)})")

    if not link_obj:
        flash('Связка не найдена', 'danger')
        return abort(404)

    # Инвертируем статус подтверждения
    link_obj.is_confirmed = not link_obj.is_confirmed
    print(f"[confirm_link] Новое значение is_confirmed: {link_obj.is_confirmed}")
    db.session.commit()
    print("[confirm_link] Изменения сохранены в базе данных (db.session.commit())")

    # Получаем токен школы для редиректа
    school = getattr(link_obj, 'school', None)
    if not school or not hasattr(school, 'applications') or not school.applications:
        # Если нет прямой связи, пробуем получить через Application
        from models.application import Application
        application = Application.query.filter_by(school_id=school.id).first()
        if application:
            token = application.school_link_token
        else:
            flash('Не удалось определить школу для редиректа', 'danger')
            return abort(400)
    else:
        # Берём токен из первой заявки
        token = school.applications[0].school_link_token

    return redirect(url_for('school_panel.form', token=token))


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