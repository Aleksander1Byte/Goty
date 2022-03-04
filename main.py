from flask import Flask, Response, render_template
from flask_login import login_user, login_required, logout_user, current_user, \
    LoginManager

from data.db_session import create_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return
    #  db_sess = create_session()
    #  return db_sess.query().get(user_id)


def main():
    pass


@app.route('/')
def page():
    return render_template('index.html', title='Goty',
                           current_user=current_user)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
