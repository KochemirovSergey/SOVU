from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TeacherSelfRegisterForm(FlaskForm):
    full_name = StringField('ФИО учителя', validators=[DataRequired()])
    subjects = StringField('Предметы (через запятую)', validators=[DataRequired()])
    start_year = IntegerField('Год начала', validators=[DataRequired(), NumberRange(min=1950, max=2100)])
    end_year = IntegerField('Год окончания', validators=[DataRequired(), NumberRange(min=1950, max=2100)])
    submit = SubmitField('Сохранить')