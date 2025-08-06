from flask import jsonify

from app_prepare import app


@app.route("/")
def hello():
    return jsonify("The CAN platform backend API branches off here!")
