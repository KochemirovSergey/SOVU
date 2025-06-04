from models import db

class School(db.Model):
    """Модель школы"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(512))
    address = db.Column(db.String(512))
    inn = db.Column(db.String(12))
    director = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))  # Новый: телефон школы
    status = db.Column(db.String(50))  # 'действующая' или 'ликвидирована'
    city = db.Column(db.String(255))  # Город школы

    # Новые поля для правопреемника
    successor_name = db.Column(db.String(255))
    successor_inn = db.Column(db.String(12))
    successor_address = db.Column(db.String(512))

    is_selected_by_graduate = db.Column(db.Boolean, default=False, nullable=False)  # Выбрана выпускником
    
    # Отношения
    graduate_schools = db.relationship('GraduateSchool', backref='school', cascade='all, delete-orphan', overlaps="school")
    teacher_schools = db.relationship('TeacherSchool', backref='school', cascade='all, delete-orphan', overlaps="school")
    applications = db.relationship('Application', backref='school', cascade='all, delete-orphan', overlaps="school")
    
    def __repr__(self):
        return f'<School {self.name}>'