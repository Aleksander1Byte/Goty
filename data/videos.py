from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import os

from .tools.hash import generate_hash


class Video(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'videos'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("users.id"),
                                   nullable=False)
    creator = orm.relation('User')

    def set_video(self, video):
        from main import app
        """Создаёт путь к видео"""
        self.path = os.path.join(
            app.config['UPLOAD_FOLDER']) + generate_hash() + video.filename[
                                                             -4:]
        video.save(self.path)
