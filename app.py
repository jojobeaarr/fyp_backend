import pymongo as pymongo
from bson import json_util
from flask import Flask, jsonify, request

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://dummy_jojo:m4AQAcwgzq4PejKG@cluster0.eglly.mongodb.net/alto_touch?retryWrites=true&w=majority")
db = client.alto_touch


@app.route('/')
def get_bmc_data():
    return json_util.dumps(db.bmc_content.find_one())


@app.route('/api/card/container')
def get_container():
    user_id = request.args.get("user_id")
    result = db.bmc_content.find_one({"userid": user_id})
    print(result)
    return result["container_id"]


@app.route('/api/card/get')
def get_card():
    container = request.args.get("container_id")
    card_id = request.args.get("card_id", None)

    if card_id:
        query = db.bmc_content.find_one({f"bmc_cards.{card_id}.card_id": card_id})
        result = query["bmc_cards"][card_id]
    else:
        query = db.bmc_content.find_one({"container_id": container})
        result = query["bmc_cards"]
    return json_util.dumps(result)


@app.route('/api/card/update', methods=['POST'])
def update_card():
    card_id = request.json["card_id"]
    card_content = request.json["data"]
    print(card_content)
    db.bmc_content.update({f"bmc_cards.{card_id}.card_id": card_id}, {"$set": {f"bmc_cards.{card_id}.content": card_content}})
    card = db.bmc_content.find_one({f"bmc_cards.{card_id}.card_id": card_id})
    print(card)
    return "Success"


if __name__ == '__main__':
    app.run()
