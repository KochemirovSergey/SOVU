from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class GraduateSchoolForm(FlaskForm):
    city = StringField('Город', validators=[DataRequired(message="Выберите город")])
    school_name = StringField('Название школы', validators=[DataRequired(message="Введите название школы")])
    start_year = IntegerField('Год начала', validators=[DataRequired(message="Выберите год начала"), NumberRange(min=1900, max=2100, message="Некорректный год")])
    end_year = IntegerField('Год окончания', validators=[DataRequired(message="Выберите год окончания"), NumberRange(min=1900, max=2100, message="Некорректный год")])

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators=extra_validators)
        if not rv:
            return False
        if self.start_year.data is not None and self.end_year.data is not None:
            try:
                if int(self.end_year.data) < int(self.start_year.data):
                    self.end_year.errors.append("Год окончания не может быть меньше года начала")
                    return False
            except Exception:
                self.end_year.errors.append("Ошибка в годах")
                return False
        return True