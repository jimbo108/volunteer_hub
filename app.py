from random import randint
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import backend.data_model.db_interface as db_int
import backend.api.api as api
import backend.api.secrets as secrets

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_SECRET_KEY'] = secrets.JWT_KEY

logging.basicConfig(filename='logfile', level=logging.DEBUG)


@app.route('/random', methods=['GET'])
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)


@app.route('/login-user', methods=['POST'])
def login_user():
    json_request = request.get_json()
    return api.login_user(json_request)


@app.route('/register-user', methods=['POST'])
def register_user():
    json_request = request.get_json()
    return api.register_user(json_request)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
