from flask import Flask, Response


app = Flask(__name__)


def main():
    pass


@app.route('/')
def page():
    return 'Текст'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
