from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewVideoForm(FlaskForm):
    file = FileField('Файл (<5ГБ)',
                     validators=[DataRequired()])
    title = StringField('Название видео',
                        validators=[DataRequired(), Length(max=300)])
    description = TextAreaField("Описание видео")
    preview = FileField("Превью видео (<5МБ)")
    submit = SubmitField('Загрузить видео')
