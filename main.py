import os.path
from random import shuffle
from typing import Union

from flask import Flask, render_template, request
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_restful import Api
from requests import delete, get
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import redirect

from data.db_session import create_session, global_init
from data.forms.LoginForm import LoginForm
from data.forms.NewVideoForm import NewVideoForm
from data.forms.RegisterForm import RegisterForm
from data.resources import video_resources
from data.tools.get_preview import get_preview
from data.tools.video_filters import (get_liked_and_disliked_videos,
                                      get_random_videos)
from data.users import User
from data.video_statistics import VideoStats
from data.videos import Video

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')

DEBUG = True
api = Api(app)
api.add_resource(video_resources.VideosListResource, '/videos')
api.add_resource(video_resources.VideosResource, '/videos/<int:video_id>')


@app.route('/')
def main():
    db_sess = create_session()
    videos = get(f'http://{ADDRESS}/videos').json()
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
    return render_template('account.html', title=user.nickname,
                           current_user=current_user, user=user,
                           liked_disliked_videos=get_liked_and_disliked_videos(
                               user))


@app.route('/video_delete/<int:video_id>')
@login_required
def delete_video(video_id):
    delete(f'http://{ADDRESS}/videos/{video_id}')
    return redirect('/')


@app.route('/watch/<string:video_hash>', methods=['GET', 'POST'])
def watch_video(video_hash):
    db_sess = create_session()
    video_orig = db_sess.query(Video).where(
        Video.path.like(f'%{video_hash}%')).first()

    if request.method == 'POST' and current_user.is_authenticated:

        user = db_sess.get(User, current_user.id)

        method = list(request.form.keys())[0].split('.')[0]  # like or dislike
        stats = video_orig.stats[0]
        if str(video_orig.id) in set(user.liked_videos.split()) | set(
                user.disliked_videos.split()):
            if method == 'like':
                if str(video_orig.id) in user.liked_videos:
                    change_mark(stats, user, video_orig, None)
                elif str(video_orig.id) in user.disliked_videos:
                    change_mark(stats, user, video_orig, 'dislike')
            else:
                if str(video_orig.id) in user.disliked_videos:
                    change_mark(stats, user, video_orig, None)
                elif str(video_orig.id) in user.liked_videos:
                    change_mark(stats, user, video_orig, 'like')
            db_sess.commit()

            return redirect(f'/watch/{video_hash}')

        if method == 'like':
            user.liked_videos += str(video_orig.id) + ' '
            stats.likes += 1
        elif method == 'dislike':
            user.disliked_videos += str(video_orig.id) + ' '
            stats.dislikes += 1
        db_sess.commit()
        return redirect(f'/watch/{video_hash}')
    elif request.method == 'POST':
        return redirect(f'http://{ADDRESS}/register')
    else:
        videos = get_random_videos(db_sess, video_orig, ADDRESS)
        return render_template('watch.html', title=video_orig.title,
                               current_user=current_user, video=video_orig,
                               author=video_orig.creator.nickname,
                               videos=videos)


def change_mark(stats, user, video_orig, method: Union[str, None]) -> None:
    if method == 'dislike':
        user.disliked_videos = user.disliked_videos.replace(
            str(video_orig.id) + ' ', '', 1)
        user.liked_videos += str(video_orig.id) + ' '
        stats.likes += 1
        stats.dislikes -= 1
    elif method == 'like':
        user.disliked_videos += str(video_orig.id) + ' '

        user.liked_videos = user.liked_videos.replace(
            str(video_orig.id) + ' ', '', 1)
        stats.likes -= 1
        stats.dislikes += 1
    else:
        if str(video_orig.id) in user.liked_videos:
            user.liked_videos = user.liked_videos.replace(
                str(video_orig.id) + ' ', '', 1)
            stats.likes -= 1
        elif str(video_orig.id) in user.disliked_videos:
            user.disliked_videos = user.disliked_videos.replace(
                str(video_orig.id) + ' ', '', 1)
            stats.dislikes -= 1


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
        stats = VideoStats(video_id=video.id)
        db_sess.add(stats)
        db_sess.commit()
        return f"""<h3>Успешная загрузка! <a href="/watch/{video.__hash__()}">
Посмотрите видео тут</a></h3>"""

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


@app.route('/search', methods=['GET'])
def search():
    db_sess = create_session()
    query = request.args.get("search_query")
    videos = db_sess.query(Video).filter(
        Video.title.like(f'%{query}%') | Video.description.like(
            f'%{query}%') | User.nickname.like(f'%{query}%')).all()
    context = {
        'videos': videos
    }
    return render_template('query_result.html', **context)


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
        if db_sess.query(User).filter(
                (User.email == form.email.data) |
                (User.nickname == form.nickname.data)).first():
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
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           current_user=current_user)


if __name__ == '__main__':
    if DEBUG:
        PORT = 5050
        HOST = '127.0.0.1'
    else:
        PORT = int(os.environ.get("PORT", 5000))
        HOST = '0.0.0.0'
    ADDRESS = HOST + ':' + str(PORT)
    app.run(host=HOST, port=PORT)
