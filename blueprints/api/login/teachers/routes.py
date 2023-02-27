from flask import Blueprint, jsonify, request, session
from functions.login import registerUser, teacherExists

teachers = Blueprint('teachers', __name__, url_prefix='/teachers')


@teachers.route('/signup', methods=['POST'])
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
        registerUser(firstname, surname, password, "Enseignants")
        return jsonify(success=True), 200


@teachers.route('/signin', methods=['POST'])
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
        teacher = teacherExists(firstname, surname, password)

        # Si l'enseignant existe en base de donnée
        if teacher:
            return jsonify({
                "success": True,
                "user": teacher
            }), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "First Name, Surname or Password Invalid"
            }), 401


@teachers.route('/logged', methods=['GET'])
def logged():
    print(session)
    if 'user' in session:
        return jsonify(session["user"])
    else:
        return jsonify({
            "status": 200,
            "reason": "not Logged"
        }), 200
