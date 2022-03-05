from wtforms import SubmitField, FileField, TextAreaField, StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class NewVideoForm(FlaskForm):
    file = FileField('Файл (<5ГБ)',
                     validators=[DataRequired()])
    title = StringField('Название видео', validators=[DataRequired()])
    description = TextAreaField("Описание видео")
    submit = SubmitField('Загрузить видео')
