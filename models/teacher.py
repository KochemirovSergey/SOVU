from datetime import datetime
from models import db

class Teacher(db.Model):
    """Модель учителя"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    link_token = db.Column(db.String(64), unique=True, nullable=True)
    document_path = db.Column(db.String(512))  # Путь к подтверждающему документу
    verification_score = db.Column(db.Float)  # Вероятность соответствия (0-1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    schools = db.relationship('TeacherSchool', back_populates='teacher')
    votes = db.relationship('Vote', back_populates='teacher')
    
    def __repr__(self):
        return f'<Teacher {self.full_name}>'


class TeacherSchool(db.Model):
    """Связующая таблица между учителями и школами"""
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    subjects = db.Column(db.String(512))  # Предметы через запятую
    
    # Отношения
    teacher = db.relationship('Teacher', back_populates='schools')
    school = db.relationship('School', back_populates='teacher_schools')
    
    def __repr__(self):
        return f'<TeacherSchool {self.teacher_id}-{self.school_id}>'