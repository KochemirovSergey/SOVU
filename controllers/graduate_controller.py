from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.graduate import Graduate, Vote, GraduateSchool
from models.school import School
from models.teacher import Teacher
from models.application import Application
from services.link_service import LinkService
from services.qr_service import QRService
from services.document_service import DocumentService
from services.voting_service import VotingService
from llm_search_school import get_school_info

from extensions import csrf

graduate_bp = Blueprint('graduate_panel', __name__)

# Сервисы
link_service = LinkService()
qr_service = QRService()
document_service = DocumentService()
voting_service = VotingService()

@graduate_bp.route('/<token>', methods=['GET', 'POST'])
@csrf.exempt
def form(token):
    import pandas as pd
    """Форма для заполнения информации о школе"""
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()

    # Чтение списка городов
    try:
        df = pd.read_csv('cities.csv')
        cities_with_regions = df.apply(lambda row: f"{row['Город']} ({row['Регион']})", axis=1).tolist()
    except Exception:
        cities_with_regions = []

    selected_city = ""
    form_data = {
        "city": "",
        "school_name": "",
        "start_year": "",
        "end_year": "",
        "start_grade": "",
        "end_grade": ""
    }
    errors = {}
    search_done = False
    success_message = None

    if request.method == 'POST':
        action = request.form.get('action', 'search')
        # Сохраняем значения полей
        form_data["city"] = request.form.get('city', '').strip()
        form_data["school_name"] = request.form.get('school_name', '').strip()
        form_data["start_year"] = request.form.get('start_year', '').strip()
        form_data["end_year"] = request.form.get('end_year', '').strip()
        form_data["start_grade"] = request.form.get('start_grade', '').strip()
        form_data["end_grade"] = request.form.get('end_grade', '').strip()

        # Если пользователь изменил город или название школы — сбросить этап подтверждения
        if action == "search" or not (form_data["city"] and form_data["school_name"]):
            # Валидация только города и названия школы
            if not form_data["city"]:
                errors["city"] = "Выберите город"
            if not form_data["school_name"]:
                errors["school_name"] = "Введите название школы"
            if not errors:
                search_done = True
            return render_template(
                'graduate/form.html',
                graduate=graduate,
                cities=cities_with_regions,
                selected_city=form_data["city"],
                form_data=form_data,
                errors=errors,
                search_done=search_done,
                success_message=success_message
            )

        # Если подтверждение школы
        if action == "confirm":
            # Валидация всех полей
            if not form_data["city"]:
                errors["city"] = "Выберите город"
            if not form_data["school_name"]:
                errors["school_name"] = "Введите название школы"
            if not form_data["start_year"]:
                errors["start_year"] = "Выберите год начала"
            if not form_data["end_year"]:
                errors["end_year"] = "Выберите год окончания"
            if not form_data["start_grade"]:
                errors["start_grade"] = "Укажите класс начала"
            if not form_data["end_grade"]:
                errors["end_grade"] = "Укажите класс окончания"
            # Дополнительная валидация
            try:
                if form_data["start_year"] and form_data["end_year"]:
                    if int(form_data["end_year"]) < int(form_data["start_year"]):
                        errors["end_year"] = "Год окончания не может быть меньше года начала"
                if form_data["start_grade"] and form_data["end_grade"]:
                    if int(form_data["end_grade"]) < int(form_data["start_grade"]):
                        errors["end_grade"] = "Класс окончания не может быть меньше класса начала"
            except Exception:
                pass

            if errors:
                search_done = True
                return render_template(
                    'graduate/form.html',
                    graduate=graduate,
                    cities=cities_with_regions,
                    selected_city=form_data["city"],
                    form_data=form_data,
                    errors=errors,
                    search_done=search_done,
                    success_message=success_message
                )

            # Найти или создать школу
            school = School.query.filter_by(name=form_data["school_name"]).first()
            if not school:
                school = School(name=form_data["school_name"], city=form_data["city"])
                db.session.add(school)
                db.session.commit()
            else:
                school.city = form_data["city"]
                db.session.commit()

            # Создать запись GraduateSchool
            gs = GraduateSchool(
                graduate_id=graduate.id,
                school_id=school.id,
                start_year=form_data["start_year"],
                end_year=form_data["end_year"],
                start_grade=form_data["start_grade"],
                end_grade=form_data["end_grade"]
            )
            db.session.add(gs)
            db.session.commit()

            # === СОЗДАНИЕ ЗАЯВКИ (Application) ===
            application = Application(
                graduate_id=graduate.id,
                school_id=school.id,
                start_year=form_data["start_year"],
                end_year=form_data["end_year"],
                start_grade=form_data["start_grade"],
                end_grade=form_data["end_grade"],
                school_link_token="",  # временно пусто
                teacher_link_token=""  # временно пусто
            )
            db.session.add(application)
            db.session.commit()

            # Генерация токенов для заявки
            link_service = LinkService()
            link_service.generate_school_link(application.id)
            link_service.generate_teacher_link(application.id)
            db.session.commit()
            # === КОНЕЦ БЛОКА СОЗДАНИЯ ЗАЯВКИ ===

            success_message = "Школа успешно добавлена"
            search_done = True
            # Оставляем значения в форме
            return render_template(
                'graduate/form.html',
                graduate=graduate,
                cities=cities_with_regions,
                selected_city=form_data["city"],
                form_data=form_data,
                errors={},
                search_done=search_done,
                success_message=success_message
            )

    # GET-запрос или первый показ формы
    return render_template(
        'graduate/form.html',
        graduate=graduate,
        cities=cities_with_regions,
        selected_city=selected_city,
        form_data=form_data,
        errors=errors,
        search_done=False,
        success_message=None
    )
@graduate_bp.route('/<token>/school/<int:school_id>/delete', methods=['POST'])
@csrf.exempt
def delete_school(token, school_id):
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    gs = GraduateSchool.query.filter_by(id=school_id, graduate_id=graduate.id).first_or_404()
    db.session.delete(gs)
    db.session.commit()
    flash('Школа удалена', 'success')
    return redirect(url_for('graduate_panel.form', token=token))

@graduate_bp.route('/<token>/school/<int:school_id>/edit', methods=['GET', 'POST'])
@csrf.exempt
def edit_school(token, school_id):
    import pandas as pd
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    gs = GraduateSchool.query.filter_by(id=school_id, graduate_id=graduate.id).first_or_404()

    # Чтение списка городов
    try:
        df = pd.read_csv('cities.csv')
        cities_with_regions = df.apply(lambda row: f"{row['Город']} ({row['Регион']})", axis=1).tolist()
    except Exception:
        cities_with_regions = []

    selected_city = gs.school.city if gs.school and gs.school.city else ""

    if request.method == 'POST':
        school_name = request.form.get('school_name')
        city = request.form.get('city')
        start_year = request.form.get('start_year')
        end_year = request.form.get('end_year')
        start_grade = request.form.get('start_grade')
        end_grade = request.form.get('end_grade')
        if not all([school_name, city, start_year, end_year, start_grade, end_grade]):
            flash('Пожалуйста, заполните все поля', 'danger')
            return render_template('graduate/edit_school.html', gs=gs, token=token, cities=cities_with_regions, selected_city=city)
        # Найти или создать школу
        school = School.query.filter_by(name=school_name).first()
        if not school:
            school = School(name=school_name, city=city)
            db.session.add(school)
            db.session.commit()
        else:
            school.city = city
            db.session.commit()
        gs.school_id = school.id
        gs.start_year = start_year
        gs.end_year = end_year
        gs.start_grade = start_grade
        gs.end_grade = end_grade
        db.session.commit()
        flash('Данные школы обновлены', 'success')
        return redirect(url_for('graduate_panel.form', token=token))
    return render_template('graduate/edit_school.html', gs=gs, token=token, cities=cities_with_regions, selected_city=selected_city)

@graduate_bp.route('/<token>/vote', methods=['GET', 'POST'])
def vote(token):
    """Голосование за учителей"""
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    
    # Получаем список школ выпускника
    schools = [gs.school for gs in graduate.schools]
    
    # Получаем список учителей из этих школ
    teachers = []
    for school in schools:
        for ts in school.teacher_schools:
            teachers.append(ts.teacher)
    
    if request.method == 'POST':
        teacher_ids = request.form.getlist('teachers')
        
        if not teacher_ids:
            flash('Пожалуйста, выберите хотя бы одного учителя', 'danger')
            return render_template('graduate/vote.html', graduate=graduate, teachers=teachers)
        
        # Голосуем за выбранных учителей
        for teacher_id in teacher_ids:
            vote = Vote(graduate_id=graduate.id, teacher_id=teacher_id)
            db.session.add(vote)
        
        db.session.commit()
        flash('Ваш голос учтен', 'success')
        return render_template('graduate/thank_you.html')
    
    return render_template('graduate/vote.html', graduate=graduate, teachers=teachers)