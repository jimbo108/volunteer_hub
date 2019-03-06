from random import randint
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import backend.data_model.db_interface as db_int
import backend.api.api as api

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

logging.basicConfig(filename='logfile', level=logging.DEBUG)


@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)


@app.route('/api/submit_login', methods=['POST'])
def submit_login():
    json_request = request.get_json()
    return api.submit_login(json_request)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
