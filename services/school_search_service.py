from ai.llm_search_school import extract_school_chain
from models import db
from models.school import School

def _llm_to_db_school(school_data):
    """Преобразует LLM модель в БД модель (без ID)"""
    # Используем dict() для получения всех полей из Pydantic модели
    return school_data.dict()

def _update_school_from_llm(school, school_data):
    """Обновляет существующую школу данными из LLM"""
    school_dict = school_data.dict()
    
    # Обновляем все поля (кроме id, который не должен изменяться)
    for field, value in school_dict.items():
        if hasattr(school, field) and field != 'id':
            setattr(school, field, value)

def search_and_save_schools(city: str, school_name: str, inn: str = None):
    """
    Ищет школы через LLM, сохраняет все найденные школы в БД.
    Возвращает школу, выбранную выпускником (is_selected_by_graduate=True).
    """
    school_chain = extract_school_chain(city, school_name, school_name, inn)
    selected_school = None

    for school_data in school_chain:
        # Поиск по ИНН или имени+адресу
        school = None
        if school_data.inn:
            school = School.query.filter_by(inn=school_data.inn).first()
        if not school:
            school = School.query.filter_by(name=school_data.name, address=school_data.address).first()
        
        if not school:
            # Создание новой школы - прямое преобразование LLM модели в БД
            school_dict = _llm_to_db_school(school_data)
            school = School(**school_dict)
            db.session.add(school)
            db.session.flush()
        else:
            # Обновление существующей школы
            _update_school_from_llm(school, school_data)
            db.session.flush()
        
        if getattr(school_data, "is_selected_by_graduate", False):
            selected_school = school

    db.session.commit()
    return selected_school