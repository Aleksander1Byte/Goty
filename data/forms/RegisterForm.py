from wtforms import EmailField, PasswordField, StringField, SubmitField, \
    IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    nickname = StringField('Ваш никнейм',
                           validators=[DataRequired()])
    submit = SubmitField('Вперёд!')
