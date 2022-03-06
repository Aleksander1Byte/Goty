from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import os

from .tools.hash import generate_hash
from PIL import Image


class Video(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'videos'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    preview_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
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

    def set_preview(self, preview):
        def fix_preview(preview_1):
            im = Image.open(preview_1)
            im.thumbnail((400, 600), Image.ANTIALIAS)
            return im

        from main import app
        """Создаёт путь к превью и задаёт его размеры"""
        self.preview_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'previews/' + generate_hash() + preview.filename[-4:]
        preview = fix_preview(preview)
        preview.save(self.preview_path, 'jpeg')
