from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from models.application import Application

class GraduateForm(FlaskForm):
    """Форма для создания и редактирования выпускника"""
    full_name = StringField('ФИО выпускника', validators=[DataRequired(), Length(min=3, max=255)])
    submit = SubmitField('Сохранить')

class ApplicationFilterForm(FlaskForm):
    """Форма для фильтрации заявок"""
    status = SelectField('Статус', choices=[
        ('all', 'Все'),
        ('created', 'Создана'),
        ('sent', 'Отправлена'),
        ('completed', 'Завершена')
    ], default='all')
    submit = SubmitField('Применить')

class ApplicationStatusForm(FlaskForm):
    """Форма для изменения статуса заявки"""
    status = SelectField('Статус', choices=[
        ('created', 'Создана'),
        ('sent', 'Отправлена'),
        ('completed', 'Завершена')
    ], validators=[DataRequired()])
    submit = SubmitField('Обновить статус')

class ApplicationForm(FlaskForm):
    """Форма для создания и редактирования заявки"""
    graduate_id = IntegerField('ID выпускника', validators=[DataRequired()])
    school_id = IntegerField('ID школы', validators=[DataRequired()])
    start_year = IntegerField('Год начала обучения', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    end_year = IntegerField('Год окончания обучения', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    start_grade = IntegerField('Класс начала обучения', validators=[DataRequired(), NumberRange(min=1, max=11)])
    end_grade = IntegerField('Класс окончания обучения', validators=[DataRequired(), NumberRange(min=1, max=11)])
    status = SelectField('Статус', choices=[
        ('created', 'Создана'),
        ('sent', 'Отправлена'),
        ('completed', 'Завершена')
    ], validators=[DataRequired()])
    document_path = StringField('Путь к документу', validators=[Optional()])
class SchoolForm(FlaskForm):
    """Форма для создания и редактирования школы"""
    name = StringField('Краткое название', validators=[DataRequired(), Length(max=255)])
    full_name = StringField('Полное название', validators=[Optional(), Length(max=512)])
    address = StringField('Адрес', validators=[Optional(), Length(max=512)])
    inn = StringField('ИНН', validators=[Optional(), Length(max=12)])
    director = StringField('Директор', validators=[Optional(), Length(max=255)])
    email = StringField('Email', validators=[Optional(), Length(max=255)])
    status = SelectField('Статус', choices=[
        ('действующая', 'Действующая'),
        ('ликвидирована', 'Ликвидирована')
    ], validators=[Optional()])
    city = StringField('Город', validators=[Optional(), Length(max=255)])
    successor_id = IntegerField('ID правопреемника', validators=[Optional()])
    submit = SubmitField('Сохранить')
    submit = SubmitField('Сохранить')