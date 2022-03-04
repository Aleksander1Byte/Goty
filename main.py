from flask import Flask, Response, render_template, request
from flask_login import login_user, login_required, logout_user, current_user, \
    LoginManager
from flask_restful import Api
from werkzeug.utils import redirect, secure_filename

from data.db_session import create_session, global_init
from data.forms.LoginForm import LoginForm
from data.forms.NewVideoForm import NewVideoForm
from data.forms.RegisterForm import RegisterForm
from data.resources import video_resources
from data.users import User
from data.videos import Video
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/videos/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')

api = Api(app)
api.add_resource(video_resources.VideosListResource, '/videos')
api.add_resource(video_resources.VideosResource, '/videos/<int:video_id>')


@app.route('/')
def main():
    return render_template('index.html', title='Goty',
                           current_user=current_user)


@app.route('/video/post', methods=['GET', 'POST'])
def video_post():
    ALLOWED_EXTENSIONS = {'avi', 'mp4'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[
            1].lower() in ALLOWED_EXTENSIONS

    form = NewVideoForm()
    if form.validate_on_submit():
        if not allowed_file(form.title.data):
            render_template('new_video.html',
                            title='Goty - Upload a video',
                            current_user=current_user, form=form,
                            message='Неверный формат файла')

        db_sess = create_session()
        f = request.files['file']
        video = Video(
            title=form.title.data,
            description=form.description.data,
            creator_id=current_user.id
        )
        video.set_video(f)

        db_sess.add(video)
        db_sess.commit()
        return redirect('/')

    return render_template('new_video.html', title='Goty - Upload a video',
                           current_user=current_user, form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form,
                           current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   current_user=current_user)
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   current_user=current_user)
        user = User(
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form,
                           current_user=current_user)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
