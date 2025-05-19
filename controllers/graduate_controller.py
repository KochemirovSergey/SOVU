from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.graduate import Graduate, Vote
from models.school import School
from models.teacher import Teacher
from models.application import Application
from services.link_service import LinkService
from services.qr_service import QRService
from services.document_service import DocumentService
from services.voting_service import VotingService
from llm_search_school import get_school_info

graduate_bp = Blueprint('graduate_panel', __name__)

# Сервисы
link_service = LinkService()
qr_service = QRService()
document_service = DocumentService()
voting_service = VotingService()

@graduate_bp.route('/<token>', methods=['GET', 'POST'])
def form(token):
    """Форма для заполнения информации о школе"""
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    
    if request.method == 'POST':
        city = request.form.get('city')
        school_name = request.form.get('school_name')
        start_year = request.form.get('start_year')
        end_year = request.form.get('end_year')
        start_grade = request.form.get('start_grade')
        end_grade = request.form.get('end_grade')
        
        if not all([city, school_name, start_year, end_year, start_grade, end_grade]):
            flash('Пожалуйста, заполните все поля', 'danger')
            return render_template('graduate/form.html', graduate=graduate)
        
        # Поиск информации о школе
        basic_info, detailed_info = get_school_info(city, school_name)
        
        # Проверяем, существует ли школа в базе
        school = School.query.filter_by(name=basic_info.name).first()
        
        if not school:
            # Создаем новую школу
            school = School(
                name=basic_info.name,
                full_name=detailed_info.full_name,
                address=detailed_info.address,
                inn=detailed_info.inn,
                director=detailed_info.director,
                email=detailed_info.email,
                status=basic_info.status
            )
            db.session.add(school)
            db.session.commit()
        
        # Создаем заявку
        application = Application(
            graduate_id=graduate.id,
            school_id=school.id,
            start_year=start_year,
            end_year=end_year,
            start_grade=start_grade,
            end_grade=end_grade,
            school_link_token=link_service.generate_token(),
            teacher_link_token=link_service.generate_token()
        )
        db.session.add(application)
        db.session.commit()
        
        # Генерируем документ
        document_path = document_service.generate_school_request(application.id)
        application.document_path = document_path
        db.session.commit()
        
        flash('Информация о школе успешно сохранена', 'success')
        return redirect(url_for('graduate_panel.vote', token=token))
    
    return render_template('graduate/form.html', graduate=graduate)

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