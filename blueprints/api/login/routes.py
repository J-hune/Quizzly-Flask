from flask import Blueprint, request, jsonify

login = Blueprint('login', __name__, url_prefix='/login')

@login.route('/', methods=['POST'])
def logUser():
    data = request.json
    return jsonify(data)