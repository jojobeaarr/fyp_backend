import hashlib
import uuid

import pymongo
from flask import request, jsonify, make_response, Blueprint
from flask.views import MethodView
from app import User

auth_blueprint = Blueprint('auth', __name__)

DB_URI = "mongodb+srv://dummy_jojo:m4AQAcwgzq4PejKG@cluster0.eglly.mongodb.net/alto_touch?retryWrites=true&w=majority"
client = pymongo.MongoClient(DB_URI)
db = client.alto_touch


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        email = post_data.get('email')
        # check if user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                password = post_data.get('password')
                salt = uuid.uuid4().bytes
                container_id = str(uuid.uuid4())
                iter = 5000
                hash_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iter)
                user = User(name=post_data.get('name'), email=email, container=container_id, salt=salt,
                            hash=hash_pass, iter=iter)
                user.save()
                # create_template(container_id)
                # generate the auth token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202

# define the API resources
registration_view = RegisterAPI.as_view('register_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)