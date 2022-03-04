from flask_restful import abort, Resource
from flask import jsonify

from data import db_session
from data.videos import Video

from data.reg_parse_video import parser


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    video = session.query(Video).get(video_id)
    if not video:
        abort(404, message=f"Video {video_id} not found")


class VideosResource(Resource):
    def get(self, video_id):
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        return jsonify({'videos': video.to_dict(
            only=('id', 'path', 'creator_id', 'title', 'description'))})

    def delete(self, video_id):
        import os
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        os.remove(video.path)
        session.delete(video)
        session.commit()
        return jsonify({'success': 'OK'})


class VideosListResource(Resource):
    def get(self):
        session = db_session.create_session()
        videos = session.query(Video).all()
        return jsonify({'videos': [item.to_dict(
            only=('id', 'path', 'creator_id', 'title', 'description')) for item in videos]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if session.query(Video).filter(Video.id == args['id']).first():
            return jsonify({'error': 'video with that id already exists'})
        video = Video(
            id=args['id'],
            path=args['path'],
            creator_id=args['creator_id'],
            description=args['description'],
            title=args['title']
        )
        session.add(video)
        session.commit()
        return jsonify({'success': 'OK'})
