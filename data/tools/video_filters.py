from random import shuffle

from flask_restful import abort
from requests import get

from data.db_session import create_session
from data.users import User
from data.videos import Video


def get_random_videos(db_sess, video_orig, ADDRESS):
    index = 0
    videos = get(f'http://{ADDRESS}/videos').json()
    try:
        for video in videos['videos']:
            if video['id'] == video_orig.id:
                index = videos['videos'].index(video)
            video['creator_nick'] = db_sess.query(User).get(
                video['creator_id']).nickname
    except AttributeError:
        abort(404, message=f"Video not found")
    videos['videos'].pop(index)
    videos['videos'] = videos['videos'][:4]
    shuffle(videos['videos'])
    videos = videos['videos']
    return videos


def get_liked_videos(user):
    db_sess = create_session()
    videos = list()
    for id in user.liked_videos.split():
        videos.append(db_sess.query(Video).get(id))
    return videos


def get_disliked_videos(user):
    db_sess = create_session()
    videos = list()
    for id in user.disliked_videos.split():
        videos.append(db_sess.query(Video).get(id))
    return videos


def get_liked_and_disliked_videos(user: User) -> tuple:
    db_sess = create_session()

    liked_videos = list()
    for id in user.liked_videos.split():
        liked_videos.append(db_sess.query(Video).get(id))

    disliked_videos = list()
    for id in user.disliked_videos.split():
        disliked_videos.append(db_sess.query(Video).get(id))

    return liked_videos, disliked_videos
