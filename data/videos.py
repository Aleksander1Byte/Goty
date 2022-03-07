from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.datastructures import FileStorage

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import os
import datetime

from .tools.hash import generate_hash
from PIL import Image
from multipledispatch import dispatch


class Video(SqlAlchemyBase, UserMixin, SerializerMixin):
    PREVIEW_SIZE = (400, 600)
    __tablename__ = 'videos'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    preview_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("users.id"),
                                   nullable=False)
    creator = orm.relation('User')

    def set_video(self, video):
        from main import app
        """Создаёт путь к видео"""
        self.path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'videos/' + generate_hash() + video.filename[-4:]  # .mp4
        video.save(self.path)

    @dispatch(FileStorage)
    def set_preview(self, preview):
        from main import app
        """Создаёт путь к превью и задаёт его размеры"""
        self.preview_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'previews/' + generate_hash() + preview.filename[-4:]
        preview = self.fix_preview(preview)
        preview.save(self.preview_path, 'png')

    @dispatch(str)
    def set_preview(self, temp_preview_path):

        from main import app
        """Создаёт путь к превью, задаёт его размеры и удаляет врмееный файл"""
        self.preview_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'previews/' + generate_hash() + temp_preview_path[-4:]
        preview = self.fix_preview(temp_preview_path)
        preview.save(self.preview_path, 'jpeg')
        os.remove(temp_preview_path)

    @staticmethod
    def fix_preview(preview_1):
        im = Image.open(preview_1)
        im.thumbnail(Video.PREVIEW_SIZE, Image.ANTIALIAS)
        return im
