from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=False)
parser.add_argument('path', required=True)
parser.add_argument('creator_id', required=True)
parser.add_argument('title', required=True)
parser.add_argument('description', required=False)
parser.add_argument('preview_path', required=False)
