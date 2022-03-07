from random import shuffle

from flask import Flask, Response, render_template, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user, \
    LoginManager
from flask_restful import Api, abort
from requests import get, delete
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import redirect

from data.db_session import create_session, global_init
from data.forms.LoginForm import LoginForm
from data.forms.NewVideoForm import NewVideoForm
from data.forms.RegisterForm import RegisterForm
from data.resources import video_resources
from data.tools.get_preview import get_preview
from data.users import User
from data.videos import Video
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')

api = Api(app)
api.add_resource(video_resources.VideosListResource, '/videos')
api.add_resource(video_resources.VideosResource, '/videos/<int:video_id>')


@app.route('/')
def main():
    db_sess = create_session()
    videos = get('http://127.0.0.1:8080/videos').json()
    for video in videos['videos'][:12]:
        video['creator_nick'] = db_sess.query(User).get(
            video['creator_id']).nickname
    videos = videos['videos']
    shuffle(videos)

    return render_template('view_videos.html', title='Goty',
                           current_user=current_user, videos=videos)


@app.route('/user/<string:user_id>')
def account(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    #  user.id == current_user.id
    return render_template('account.html', title=user.nickname,
                           current_user=current_user, user=user)


@app.route('/video_delete/<int:video_id>')
@login_required
def delete_video(video_id):
    delete(f'http://127.0.0.1:8080/videos/{video_id}')
    return redirect('/')


@app.route('/watch/<string:video_hash>')
def watch_video(video_hash):
    index = 0
    db_sess = create_session()
    video_orig = db_sess.query(Video).filter(
        Video.path.like("%" + video_hash + "%")).first()

    videos = get('http://127.0.0.1:8080/videos').json()
    try:
        for video in videos['videos']:
            if video['id'] == video_orig.id:
                index = videos['videos'].index(video)
            video['creator_nick'] = db_sess.query(User).get(
                video['creator_id']).nickname
    except AttributeError:
        abort(404, message=f"Video {video_hash} not found")
    videos['videos'].pop(index)
    videos['videos'] = videos['videos'][:4]
    shuffle(videos['videos'])
    videos = videos['videos']

    return render_template('watch.html', title=video_orig.title,
                           current_user=current_user, video=video_orig,
                           author=video_orig.creator.nickname, videos=videos)


@app.route('/video/post', methods=['GET', 'POST'])
@login_required
def video_post():
    ALLOWED_EXTENSIONS_VIDEO = {'avi', 'mp4'}
    ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'bmp', 'jpeg'}

    def allowed_file_video(filename):
        return '.' in filename and filename.rsplit('.', 1)[
            1].lower() in ALLOWED_EXTENSIONS_VIDEO

    def allowed_file_image(filename):
        return '.' in filename and filename.rsplit('.', 1)[
            1].lower() in ALLOWED_EXTENSIONS_IMAGE

    def allowed_file_image_size(file):
        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size / 1024 > 5120:
            return False
        return True

    form = NewVideoForm()
    if form.validate_on_submit():
        f = request.files['file']
        try:
            preview = request.files['preview']
        except BadRequestKeyError:
            preview = None
        if not allowed_file_video(f.filename):
            return '<h3>Неверный формат видеофайла!</h3>'
        if preview is not None and not allowed_file_image(preview.filename):
            return '<h3>Неверный формат предварительного изображения!</h3>'
        if preview is not None and not allowed_file_image_size(preview):
            return '<h3>Размер изображения слишком велик!</h3>'

        db_sess = create_session()
        video = Video(
            title=form.title.data,
            description=form.description.data,
            creator_id=current_user.id
        )
        video.set_video(f)
        if preview is None:
            preview = get_preview(video.path)  # str
        video.set_preview(preview)

        db_sess.add(video)
        db_sess.commit()
        return '<h3>Успешная загрузка!</h3>'

    if request.method == 'GET':
        return render_template('new_video.html', title='Goty - Upload a video',
                               current_user=current_user, form=form)
    else:
        return ''


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
