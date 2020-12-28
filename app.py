import pymongo as pymongo
from bson import json_util
from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = pymongo.MongoClient("mongodb+srv://dummy_jojo:m4AQAcwgzq4PejKG@cluster0.eglly.mongodb.net/alto_touch?retryWrites=true&w=majority")
db = client.alto_touch


@app.route('/')
def get_bmc_data():
    return json_util.dumps(db.bmc_content.find_one())


@app.route('/api/card/container')
@cross_origin()
def get_container():
    username = request.args.get("username")
    result = db.bmc_users.find_one({"username": username })
    return json_util.dumps(result["container_id"])


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
    card_id = request.json["card_id"]
    card_content = request.json["card_content"]
    db.bmc_content.update({"card_id": card_id}, {"$set": {"content": card_content}})
    card = db.bmc_content.find_one({"card_id": card_id})
    print(card)
    return "Success"


if __name__ == '__main__':
    app.run()
