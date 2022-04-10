import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class VideoStats(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'video_stats'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    video_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("videos.id"))
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    participants = sqlalchemy.Column(sqlalchemy.String, default='')

    comments = orm.relation('Comments', overlaps="video_stats")
    video = orm.relation('Video')
