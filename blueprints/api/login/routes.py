from flask import Blueprint, jsonify, session
from blueprints.api.login.teachers.routes import teachers
from blueprints.api.login.students.routes import students
from functions.students import getAvatar

login = Blueprint('login', __name__, url_prefix='/login')

login.register_blueprint(teachers)
login.register_blueprint(students)


@login.route('/logged', methods=['GET'])
def logged():
    if 'user' in session:
        if session["user"]["type"] == "Etudiant":
            return jsonify({**session["user"], "avatar": getAvatar(session["user"]["id"])})
        else:
            return jsonify(session["user"])
    else:
        return jsonify({
            "status": 200,
            "reason": "La connection a échouée"
        }), 200
