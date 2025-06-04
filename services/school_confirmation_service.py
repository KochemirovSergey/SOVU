from models import db
from models.graduate import Graduate, GraduateSchool
from models.school import School
from models.application import Application

def confirm_school(graduate: Graduate, school: School, start_year: int, end_year: int):
    """
    Добавляет выбранную школу выпускнику и создает заявку для действующей школы.
    Если выбранная школа ликвидирована — ищет правопреемника по ИНН и создает заявку для него.
    """
    # Добавить GraduateSchool для выбранной школы
    gs = GraduateSchool(
        graduate_id=graduate.id,
        school_id=school.id,
        start_year=start_year,
        end_year=end_year
    )
    db.session.add(gs)
    db.session.flush()

    # Определить действующую школу (сама или правопреемник)
    active_school = school
    if school.status.strip().lower() == "ликвидирована" and school.successor_inn:
        successor = School.query.filter_by(inn=school.successor_inn).first()
        if successor:
            active_school = successor

    # Создать заявку для действующей школы
    application = Application(
        graduate_id=graduate.id,
        school_id=active_school.id,
        start_year=start_year,
        end_year=end_year,
        school_link_token="",
        teacher_link_token=""
    )
    db.session.add(application)
    db.session.commit()
    return gs, application