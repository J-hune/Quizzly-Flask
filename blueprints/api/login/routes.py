from flask import Blueprint, jsonify, request, session
from functions.login import registerUser, userExists

login = Blueprint('login', __name__, url_prefix='/login')


@login.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    firstname = data.get("firstname")
    surname = data.get("surname")
    password = data.get("password")

    # Si un des champs est vide (en plus de la vérification client)
    if not (firstname and surname and password):
        return jsonify({
            "status": 401,
            "reason": "First Name, Surname or Password Invalid"
        }), 401
    else:
        registerUser(firstname, surname, password)
        return jsonify(success=True), 200


@login.route('/signin', methods=['POST'])
def signin():
    data = request.get_json(force=True)
    firstname = data.get("firstname")
    surname = data.get("surname")
    password = data.get("password")

    # Si un des champs est vide (en plus de la vérification client)
    if not (firstname and surname and password):
        return jsonify({
            "status": 401,
            "reason": "First Name, Surname or Password Invalid"
        }), 401
    else:
        # Si l'utilisateur existe en base de donnée
        if userExists(firstname, surname, password):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "First Name, Surname or Password Invalid"
            }), 401


@login.route('/logged', methods=['GET'])
def logged():
    print(session)
    if 'user' in session:
        return jsonify(session["user"])
    else:
        return jsonify({
            "status": 200,
            "reason": "not Logged"
        }), 200
