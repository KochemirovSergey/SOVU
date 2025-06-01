from datetime import datetime
from models import db

class Application(db.Model):
    """Модель заявки"""
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduate.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    school_link_token = db.Column(db.String(64), unique=True, nullable=False)
    teacher_link_token = db.Column(db.String(64), unique=True, nullable=False)
    document_path = db.Column(db.String(512))  # Путь к сгенерированному письму
    status = db.Column(db.String(50), default='created')  # created, sent, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    graduate = db.relationship('Graduate', back_populates='applications')
    school = db.relationship('School', back_populates='applications')
    
    def __repr__(self):
        return f'<Application {self.id} - {self.status}>'