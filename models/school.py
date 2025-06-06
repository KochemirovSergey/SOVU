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

    is_application = db.Column(db.Boolean, default=False)  # Флаг "школа из заявки"

    successor_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)
    
    # Отношения
    successor = db.relationship('School', remote_side=[id])
    graduate_schools = db.relationship('GraduateSchool', back_populates='school')
    teacher_schools = db.relationship('TeacherSchool', back_populates='school')
    applications = db.relationship('Application', back_populates='school')
    
    def __repr__(self):
        return f'<School {self.name}>'