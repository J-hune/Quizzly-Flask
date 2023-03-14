from flask import Blueprint, jsonify, request, session
from functions.students import changePassword, studentExists

students = Blueprint('students', __name__, url_prefix='/students')


# Permet de se connecter en tant qu'étudiant
# Param POST : ?
# Return : ?
@students.route('/signin', methods=['POST'])
def signin():
    data = request.get_json(force=True)
    student_id = data.get("id")
    password = data.get("password")

    # Si un des champs est vide (en plus de la vérification client)
    if not (student_id and password):
        return jsonify({
            "status": 401,
            "reason": "Identifiant ou mot de passe invalide"
        }), 401
    else:
        student = studentExists(student_id, password)

        # Si l'étudiant existe en base de donnée
        if student:
            return jsonify({
                "success": True,
                "user": student
            }), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "Identifiant ou mot de passe invalide"
            }), 401


# Modifie le mot de passe d'un étudiant en session
# Param POST : le mot de passe dans un dico
#               {"password":"aertyuiop"}
@students.route('/editPassword', methods=['POST'])
def editPassword():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        if changePassword(session["user"]["id"], data["password"]):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 400,
                "reason": "Échec de la requête"
            }), 400

    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400
