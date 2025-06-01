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
# from llm_search_school import get_school_info

from extensions import csrf

graduate_bp = Blueprint('graduate_panel', __name__)

# Сервисы
link_service = LinkService()
qr_service = QRService()
document_service = DocumentService()
voting_service = VotingService()

import logging

@graduate_bp.route('/<token>', methods=['GET', 'POST'])
@csrf.exempt
def form(token):
    """Форма для заполнения информации о школе"""
    from forms.graduate_forms import GraduateSchoolForm
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()

    search_done = False
    success_message = None

    form = GraduateSchoolForm()

    if request.method == 'POST':
        action = request.form.get('action', 'search')
        if form.validate_on_submit():
            form_data = {
                "city": form.city.data.strip(),
                "school_name": form.school_name.data.strip(),
                "start_year": str(form.start_year.data).strip(),
                "end_year": str(form.end_year.data).strip()
            }

            from llm_search_school import extract_school_chain
            school_chain = extract_school_chain(form_data["city"], form_data["school_name"])

            db_schools = []
            main_school = None
            main_school_idx = None

            for idx, school_data in enumerate(school_chain):
                if str(school_data.status).strip().lower() == "действующая" and main_school is None:
                    main_school_idx = idx
                school = None
                if school_data.inn:
                    school = School.query.filter_by(inn=school_data.inn).first()
                if not school and school_data.inn:
                    school = School.query.filter_by(name=school_data.name, address=school_data.address).first()
                elif not school:
                    school = School.query.filter_by(name=school_data.name, address=school_data.address).first()
                if not school:
                    school = School(
                        name=school_data.name,
                        full_name=school_data.full_name,
                        address=school_data.address,
                        inn=school_data.inn,
                        director=school_data.director,
                        email=school_data.email,
                        phone=school_data.phone,
                        status=school_data.status,
                        city=form_data["city"],
                        successor_name=school_data.successor_name,
                        successor_inn=school_data.successor_inn,
                        successor_address=school_data.successor_address,
                        is_application=False
                    )
                    db.session.add(school)
                    db.session.flush()
                else:
                    school.name = school_data.name
                    school.full_name = school_data.full_name
                    school.address = school_data.address
                    school.inn = school_data.inn
                    school.director = school_data.director
                    school.email = school_data.email
                    school.phone = school_data.phone
                    school.status = school_data.status
                    school.city = form_data["city"]
                    school.successor_name = school_data.successor_name
                    school.successor_inn = school_data.successor_inn
                    school.successor_address = school_data.successor_address
                    school.is_application = False
                    db.session.flush()
                db_schools.append(school)
            db.session.commit()

            gs_selected = GraduateSchool(
                graduate_id=graduate.id,
                school_id=db_schools[0].id,
                start_year=form_data["start_year"],
                end_year=form_data["end_year"],
            )
            db.session.add(gs_selected)
            db.session.commit()

            if main_school_idx is not None:
                main_school = db_schools[main_school_idx]
                if main_school_idx != 0:
                    gs_active = GraduateSchool(
                        graduate_id=graduate.id,
                        school_id=main_school.id,
                        start_year=form_data["start_year"],
                        end_year=form_data["end_year"],
                    )
                    db.session.add(gs_active)
                    db.session.commit()
                application = Application(
                    graduate_id=graduate.id,
                    school_id=main_school.id,
                    start_year=form_data["start_year"],
                    end_year=form_data["end_year"],
                    school_link_token="",
                    teacher_link_token=""
                )
                db.session.add(application)
                db.session.commit()

                link_service = LinkService()
                link_service.generate_school_link(application.id)
                link_service.generate_teacher_link(application.id)
                db.session.commit()

                success_message = "Школа успешно добавлена"
                errors = {}
            else:
                errors = {"school_name": "Не удалось найти действующую школу в цепочке. Заявка не создана."}
                success_message = None

            search_done = True
            return render_template(
                'graduate/form.html',
                graduate=graduate,
                cities=[],
                selected_city=form_data["city"],
                form_data=form_data,
                errors=errors,
                search_done=search_done,
                success_message=success_message,
                form=form
            )

    # GET-запрос или первый показ формы
    form_data = {
        "city": "",
        "school_name": "",
        "start_year": "",
        "end_year": ""
    }
    errors = {}
    return render_template(
        'graduate/form.html',
        graduate=graduate,
        cities=[],
        selected_city="",
        form_data=form_data,
        errors=errors,
        search_done=False,
        success_message=None,
        form=form
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
        if not all([school_name, city, start_year, end_year,]):
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
        db.session.commit()
        flash('Данные школы обновлены', 'success')
        return redirect(url_for('graduate_panel.form', token=token))
    return render_template('graduate/edit_school.html', gs=gs, token=token, cities=cities_with_regions, selected_city=selected_city)
