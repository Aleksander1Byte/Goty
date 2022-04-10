from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class VideoStats(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'video_stats'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    video_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("videos.id"))
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    comments = orm.relation('Comments')
    video = orm.relation('Video')
