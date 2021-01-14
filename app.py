import datetime
import hashlib
import uuid
import jwt
from flask_mongoengine import MongoEngine
import pymongo as pymongo
from bson import json_util
from flask import Flask, request
from flask_cors import CORS, cross_origin
import secrets
import os

os.environ['SECRET_KEY'] = secrets.token_urlsafe(16)
SECRET_KEY = os.getenv('SECRET_KEY')
DB_URI = "mongodb+srv://dummy_jojo:m4AQAcwgzq4PejKG@cluster0.eglly.mongodb.net/alto_touch?retryWrites=true&w=majority"


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = SECRET_KEY
app.config["MONGODB_HOST"] = DB_URI

database = MongoEngine(app)
client = pymongo.MongoClient(DB_URI)
db = client.alto_touch

template_cards = ["Customer Segments", "Value Propositions", "Key Activities", "Key Resources", "Customer Relationships", "Key Partners", "Channels", "Cost Structure", "Revenue Streams"]


class User(database.Document):
    name = database.StringField()
    email = database.StringField()
    password = database.StringField()
    container = database.StringField()
    salt = database.BinaryField()
    hash = database.BinaryField()
    iter = database.IntField()

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def encode_auth_token(self, email):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60),
                'iat': datetime.datetime.utcnow(),
                'sub': email
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def decode_auth_token(self, auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms="HS256")
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


def create_template(container_id):
    for card in template_cards:
        card_id = str(uuid.uuid4())
        db.bmc_content.insert({"container_id": container_id, "card_id": card_id,"title": card, "content": []})


# @app.route('/')
# def get_bmc_data():
#     return json_util.dumps(db.bmc_content.find_one())


@app.route('/api/card/container')
@cross_origin()
def get_container():
    #fix this
    # get the auth token
    auth_token = request.headers.get('Authorization')
    #print(auth_token)
    if not auth_token:
        auth_token = ''
    if auth_token:
        email = User().decode_auth_token(auth_token)
        print(email)
        result = User.objects.get(email=email)
        return json_util.dumps(result.container)
    else:
        return json_util.dumps("Fail")


@app.route('/api/card/get')
@cross_origin()
def get_card():
    container = request.args.get("container_id")
    card_id = request.args.get("card_id", None)

    if card_id:
        query = db.bmc_content.find_one({"card_id": card_id})
        result = query
    else:
        query = db.bmc_content.find({"container_id": container})
        result = query
    return json_util.dumps(result)


@app.route('/api/card/update', methods=['POST'])
@cross_origin()
def update_card():
    auth_token = request.headers.get('Authorization')
    #do something with this
    card_id = request.json["card_id"]
    card_content = request.json["card_content"]
    db.bmc_content.update({"card_id": card_id}, {"$set": {"content": card_content}})
    return "Success"


@app.route('/api/user/create', methods=['POST'])
@cross_origin()
def create_user():
    record = request.form
    salt = uuid.uuid4().bytes
    container_id = str(uuid.uuid4())
    iter = 5000
    hash_pass = hashlib.pbkdf2_hmac('sha256', record['password'].encode('utf-8'), salt, iter)
    user = User(name=record['name'], email=record['email'], container=container_id, salt=salt, hash=hash_pass, iter=iter)
    user.save()
    create_template(container_id)
    auth_token = user.encode_auth_token(record['email'])
    return json_util.dumps(auth_token)


@app.route('/api/user/exist', methods=['GET'])
@cross_origin()
def user_exist():
    email = request.args.get("email")
    query = User.objects(email=email).first()
    if query is None:
        #If no records found query will be empty
        return json_util.dumps("False")
    return json_util.dumps("True")


@app.route('/api/user/login', methods=['POST'])
def query_records():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.objects(email=email).first()
    if user is None:
        return json_util.dumps("error: data not found")
    else:
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), user.salt, user.iter)
        if hashed_password == user.hash:
            auth_token = user.encode_auth_token(email)
            return json_util.dumps(auth_token)
        else:
            return json_util.dumps("Fail")


if __name__ == '__main__':
    app.run()
