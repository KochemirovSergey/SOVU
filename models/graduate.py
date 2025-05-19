from datetime import datetime
from models import db

class Graduate(db.Model):
    """Модель выпускника"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    link_token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    schools = db.relationship('GraduateSchool', back_populates='graduate')
    votes = db.relationship('Vote', back_populates='graduate')
    applications = db.relationship('Application', back_populates='graduate')
    
    def __repr__(self):
        return f'<Graduate {self.full_name}>'


class GraduateSchool(db.Model):
    """Связующая таблица между выпускниками и школами"""
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduate.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    start_grade = db.Column(db.Integer, nullable=False)
    end_grade = db.Column(db.Integer, nullable=False)
    
    # Отношения
    graduate = db.relationship('Graduate', back_populates='schools')
    school = db.relationship('School', back_populates='graduate_schools')
    
    def __repr__(self):
        return f'<GraduateSchool {self.graduate_id}-{self.school_id}>'


class Vote(db.Model):
    """Модель голосования выпускника за учителя"""
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduate.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    graduate = db.relationship('Graduate', back_populates='votes')
    teacher = db.relationship('Teacher', back_populates='votes')
    
    def __repr__(self):
        return f'<Vote {self.graduate_id}-{self.teacher_id}>'