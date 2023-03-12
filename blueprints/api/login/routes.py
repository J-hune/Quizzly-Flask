from flask import Blueprint, jsonify, session
from blueprints.api.login.teachers.routes import teachers
from blueprints.api.login.students.routes import students
from functions.students import getAvatar

login = Blueprint('login', __name__, url_prefix='/login')

login.register_blueprint(teachers)
login.register_blueprint(students)


# Route qui renvoie les données de session de l'utilisateur
# Return : La session de l'utilisateur, un dictionnaire sous la forme suivante
#   {
#     "avatar": "data:image/png;base64...",     (<-- Clé présente uniquement si l'utilisateur est un étudiant)
#     "firstname": "donov",
#     "id": 22100000,
#     "surname": "zst",
#     "type": "Etudiant"
# }
@login.route('/logged', methods=['GET'])
def logged():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:

        # Si l'utilisateur est un étudiant, on retourne ses données de session et son avatar
        if session["user"]["type"] == "Etudiant":
            return jsonify({**session["user"], "avatar": getAvatar(session["user"]["id"])})

        # Sinon, on retourne les données de session uniquement
        else:
            return jsonify(session["user"])

    # Si l'utilisateur n'est pas connecté, on retourne un message d'erreur
    else:
        return jsonify({
            "status": 200,
            "reason": "La connection a échouée"
        }), 200
