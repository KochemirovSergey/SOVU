from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FileField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileAllowed

class TeacherSelfRegisterForm(FlaskForm):
    full_name = StringField('ФИО учителя', validators=[DataRequired()])
    subjects = StringField('Предметы (через запятую)', validators=[DataRequired()])
    start_year = IntegerField('Год начала', validators=[DataRequired(), NumberRange(min=1950, max=2100)])
    end_year = IntegerField('Год окончания', validators=[DataRequired(), NumberRange(min=1950, max=2100)])
    confirm_document = FileField(
        'Подтверждающий документ (PDF, DOC, DOCX, PNG, JPG, JPEG)',
        validators=[FileAllowed(['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'], 'Допустимые форматы: PDF, DOC, DOCX, PNG, JPG, JPEG')]
    )
    submit = SubmitField('Сохранить')