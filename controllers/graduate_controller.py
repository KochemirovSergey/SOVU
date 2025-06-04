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
from services.school_search_service import search_and_save_schools
from services.school_confirmation_service import confirm_school
from forms.graduate_forms import GraduateSchoolForm
# from llm_search_school import get_school_info

from extensions import csrf

graduate_bp = Blueprint('graduate_panel', __name__)

# Сервисы
link_service = LinkService()
qr_service = QRService()
document_service = DocumentService()
voting_service = VotingService()

import logging

# Константы
DEFAULT_FORM_DATA = {
    "city": "",
    "school_name": "",
    "start_year": "",
    "end_year": ""
}

def _get_form_data():
    """Извлекает данные из формы запроса"""
    return {
        "city": request.form.get("city", "").strip(),
        "school_name": request.form.get("school_name", "").strip(),
        "start_year": request.form.get("start_year", "").strip(),
        "end_year": request.form.get("end_year", "").strip()
    }

def _render_graduate_form(graduate, form_data=None, errors=None, search_done=False,
                         success_message=None, school=None, form=None):
    """Вспомогательная функция для рендеринга формы выпускника"""
    if form_data is None:
        form_data = DEFAULT_FORM_DATA.copy()
    if errors is None:
        errors = {}
    if form is None:
        form = GraduateSchoolForm()
    
    return render_template(
        'graduate/form.html',
        graduate=graduate,
        cities=[],
        selected_city=form_data.get("city", ""),
        form_data=form_data,
        errors=errors,
        search_done=search_done,
        success_message=success_message,
        form=form,
        school=school
    )

@graduate_bp.route('/<token>', methods=['GET'])
@csrf.exempt
def form(token):
    """Форма для заполнения информации о школе (только GET)"""
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    return _render_graduate_form(graduate)

# Новый маршрут: поиск школы
@graduate_bp.route('/<token>/search-school', methods=['POST'])
@csrf.exempt
def search_school(token):
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    form = GraduateSchoolForm()
    form_data = _get_form_data()
    errors = {}
    selected_school = None
    
    logging.info(f"Search school request: {form_data}")
    
    if form.validate_on_submit():
        try:
            logging.info("Form validation passed, calling search_and_save_schools")
            selected_school = search_and_save_schools(
                form_data["city"],
                form_data["school_name"],
                None
            )
            logging.info(f"Search result: {selected_school}")
            if selected_school:
                return _render_graduate_form(
                    graduate, form_data, errors,
                    search_done=True,
                    success_message="Школа найдена! Проверьте данные и подтвердите.",
                    school=selected_school, form=form
                )
            else:
                errors["school_name"] = "Не удалось найти школу"
        except Exception as e:
            logging.error(f"Error in search_and_save_schools: {str(e)}")
            errors["school_name"] = f"Ошибка поиска: {str(e)}"
    else:
        logging.warning(f"Form validation failed: {form.errors}")
        errors = form.errors

    return _render_graduate_form(graduate, form_data, errors, form=form, school=selected_school)

# Новый маршрут: подтверждение школы
@graduate_bp.route('/<token>/confirm-school', methods=['POST'])
@csrf.exempt
def confirm_school_route(token):
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    form = GraduateSchoolForm()
    form_data = _get_form_data()
    errors = {}
    
    # Найти выбранную школу
    selected_school = School.query.filter_by(
        is_selected_by_graduate=True,
        city=form_data["city"],
        name=form_data["school_name"]
    ).first()
    
    if not selected_school:
        errors["school_name"] = "Не найдена выбранная школа для подтверждения"
        return _render_graduate_form(
            graduate, form_data, errors,
            search_done=True, form=form, school=None
        )
    
    gs, application = confirm_school(
        graduate,
        selected_school,
        int(form_data["start_year"]),
        int(form_data["end_year"])
    )
    
    return _render_graduate_form(
        graduate, form_data, {},
        search_done=True,
        success_message="Школа успешно подтверждена и заявка создана",
        form=form, school=selected_school
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

