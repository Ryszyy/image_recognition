from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
import bcrypt
import errors
import requests
import subprocess
import json
import os

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.ImageRecognition
users = db["users"]


def invalid_data(data: dict, func_name: str = ""):
    try:
        data["username"]
        data["password"]
        if func_name == "detect":
            data["text1"]
            data["text2"]
    except Exception:
        return True
    return False


def user_exist(username: str):
    user = users.find_one({"Username": username})
    return True if user else False


def verified_password(username: str, password: str):
    if not user_exist(username):
        return False
    db_password = users.find_one({
        "Username": username
    })["Password"]
    return True if bcrypt.hashpw(password.encode(encoding='UTF-8'), db_password) == db_password else False


def weak_password(password: str):
    return True if 8 < len(password) else False


def enough_tokens(username: str):
    return True if users.find_one({"Username": username})["Tokens"] else False


def count_tokens(username: str):
    return users.find_one({"Username": username})["Tokens"]


def generate_return_dict(status, msg):
    return {"status": status, "msg": msg}


def verify_credentials(username, password):
    if not user_exist:
        return generate_return_dict(301, "Invalid username"), True
    if not verified_password(username, password):
        return generate_return_dict(302, "Invalid password"), True
    else:
        return None, False


class Register(Resource):
    def post(self):
        try:
            request_data = request.get_json()
            if invalid_data(request_data):
                raise errors.InvalidDataProvided
            username = request_data["username"]
            password = request_data["password"]

            if user_exist(username):
                raise errors.UserAlreadyExist
            elif weak_password(password):
                raise errors.WeakPassword
        except (errors.InvalidDataProvided, errors.UserAlreadyExist, errors.WeakPassword) as e:
            status = e.status_code
            msg = str(e)
            ret_json = {
                "status": status,
                "msg": msg
            }
            return jsonify(ret_json)
        else:
            hashed_password = bcrypt.hashpw(password.encode(encoding='UTF-8'), bcrypt.gensalt())
            users.insert({
                "Username": username,
                "Password": hashed_password,
                "Tokens": 3
            })
            ret_json = {
                "status": 200,
                "msg": "Successfully registered user"
            }
            return jsonify(ret_json)


class Classify(Resource):
    def post(self):
        request_data = request.get_json()
        if invalid_data(request_data):
            raise errors.InvalidDataProvided
        username = request_data["username"]
        password = request_data["password"]
        url = request_data["url"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return jsonify(ret_json)

        tokens = count_tokens(username)

        if tokens <= 0:
            return jsonify(generate_return_dict(303, "Not enough tokens"))

        r = requests.get(url)
        ret_json = {}
        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg',
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            var = proc.communicate()[0]
            proc.wait()
            with open("text.txt") as t:
                ret_json = json.load(t)

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": tokens - 1
            }
        })
        return ret_json


class Refill(Resource):
    def post(self):
        request_data = request.get_json()
        if invalid_data(request_data):
            raise errors.InvalidDataProvided
        username = request_data["username"]
        password = request_data["admin_pw"]
        amount = request_data["amount"]

        if user_exist(username):
            return jsonify(generate_return_dict(301, "Invalid Username"))

        correct_pw = "secretpassword"
        if not password == correct_pw:
            return jsonify(generate_return_dict(302, "Incorrect Password"))

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": amount
            }
        })
        return jsonify(generate_return_dict(200, "Refilled"))


api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host='0.0.0.0')