@graduate_bp.route('/<token>', methods=['GET', 'POST'])
@csrf.exempt
def form(token):
    """Форма для заполнения информации о школе"""
    graduate = Graduate.query.filter_by(link_token=token).first_or_404()
    
    if request.method == 'POST':
        return handle_post_request(graduate, token)
    
    # GET-запрос
    return render_form(graduate)

def render_form(graduate, form_data=None, errors=None, search_done=False, success_message=None):
    """Отображение формы с данными"""
    from forms.graduate_forms import GraduateSchoolForm
    
    if form_data is None:
        form_data = {
            "city": "",
            "school_name": "",
            "start_year": "",
            "end_year": ""
        }
    
    if errors is None:
        errors = {}
    
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
        form=form
    )

def handle_post_request(graduate, token):
    """Обработка POST-запроса"""
    from forms.graduate_forms import GraduateSchoolForm
    
    form = GraduateSchoolForm()
    
    if form.validate_on_submit():
        form_data = extract_form_data(form)
        school_chain = get_school_chain(form_data)
        
        db_schools = process_school_chain(school_chain, form_data)
        
        # Создаем связь выпускника с первой школой в цепочке
        create_graduate_school_relation(graduate.id, db_schools[0].id, form_data)
        
        # Ищем действующую школу и создаем заявку
        main_school_idx = find_active_school_index(school_chain)
        
        if main_school_idx is not None:
            success_message, errors = create_application(graduate, db_schools, main_school_idx, form_data)
        else:
            errors = {"school_name": "Не удалось найти действующую школу в цепочке. Заявка не создана."}
            success_message = None
        
        return render_form(
            graduate, 
            form_data=form_data,
            errors=errors,
            search_done=True,
            success_message=success_message
        )
    
    # Если форма не прошла валидацию
    return render_form(graduate)

def extract_form_data(form):
    """Извлечение данных из формы"""
    return {
        "city": form.city.data.strip(),
        "school_name": form.school_name.data.strip(),
        "start_year": str(form.start_year.data).strip(),
        "end_year": str(form.end_year.data).strip()
    }

def get_school_chain(form_data):
    """Получение цепочки школ"""
    from llm_search_school import extract_school_chain
    return extract_school_chain(form_data["city"], form_data["school_name"])

def find_active_school_index(school_chain):
    """Поиск индекса действующей школы в цепочке"""
    for idx, school_data in enumerate(school_chain):
        if str(school_data.status).strip().lower() == "действующая":
            return idx
    return None

def process_school_chain(school_chain, form_data):
    """Обработка цепочки школ - создание или обновление записей в БД"""
    db_schools = []
    
    for school_data in school_chain:
        school = find_existing_school(school_data)
        
        if not school:
            school = create_new_school(school_data, form_data["city"])
        else:
            update_school(school, school_data, form_data["city"])
        
        db_schools.append(school)
    
    db.session.commit()
    return db_schools

def find_existing_school(school_data):
    """Поиск существующей школы в БД"""
    school = None
    if school_data.inn:
        school = School.query.filter_by(inn=school_data.inn).first()
    if not school and school_data.inn:
        school = School.query.filter_by(name=school_data.name, address=school_data.address).first()
    elif not school:
        school = School.query.filter_by(name=school_data.name, address=school_data.address).first()
    return school

def create_new_school(school_data, city):
    """Создание новой школы в БД"""
    school = School(
        name=school_data.name,
        full_name=school_data.full_name,
        address=school_data.address,
        inn=school_data.inn,
        director=school_data.director,
        email=school_data.email,
        phone=school_data.phone,
        status=school_data.status,
        city=city,
        successor_name=school_data.successor_name,
        successor_inn=school_data.successor_inn,
        successor_address=school_data.successor_address,
        is_application=False
    )
    db.session.add(school)
    db.session.flush()
    return school

def update_school(school, school_data, city):
    """Обновление данных существующей школы"""
    school.name = school_data.name
    school.full_name = school_data.full_name
    school.address = school_data.address
    school.inn = school_data.inn
    school.director = school_data.director
    school.email = school_data.email
    school.phone = school_data.phone
    school.status = school_data.status
    school.city = city
    school.successor_name = school_data.successor_name
    school.successor_inn = school_data.successor_inn
    school.successor_address = school_data.successor_address
    school.is_application = False
    db.session.flush()
    return school

def create_graduate_school_relation(graduate_id, school_id, form_data):
    """Создание связи между выпускником и школой"""
    gs = GraduateSchool(
        graduate_id=graduate_id,
        school_id=school_id,
        start_year=form_data["start_year"],
        end_year=form_data["end_year"],
    )
    db.session.add(gs)
    db.session.commit()
    return gs

def create_application(graduate, db_schools, main_school_idx, form_data):
    """Создание заявки для действующей школы"""
    main_school = db_schools[main_school_idx]
    
    # Если действующая школа не первая в списке, создаем дополнительную связь
    if main_school_idx != 0:
        create_graduate_school_relation(graduate.id, main_school.id, form_data)
    
    # Создаем заявку
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
    
    # Генерируем ссылки
    link_service = LinkService()
    link_service.generate_school_link(application.id)
    link_service.generate_teacher_link(application.id)
    db.session.commit()
    
    return "Школа успешно добавлена", {}
