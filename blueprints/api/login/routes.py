from flask import Blueprint, jsonify, session
from blueprints.api.login.teachers.routes import teachers
from blueprints.api.login.students.routes import students
from functions.students import getAvatar

login = Blueprint('login', __name__, url_prefix='/login')

login.register_blueprint(teachers)
login.register_blueprint(students)


# ?
# Return : ?
@login.route('/logged', methods=['GET'])
def logged():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Si c'est un étudiant, envoyer l'avatar en plus
        if session["user"]["type"] == "Etudiant":
            return jsonify({**session["user"], "avatar": getAvatar(session["user"]["id"])})
        # Sinon c'est un enseignant
        else:
            return jsonify(session["user"])
    else:
        return jsonify({
            "status": 200,
            "reason": "Session non disponible"
        }), 200
