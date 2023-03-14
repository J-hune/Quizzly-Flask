from flask import Blueprint, jsonify, request
from functions.teachers import registerTeacher, teacherExists

teachers = Blueprint('teachers', __name__, url_prefix='/teachers')


# Créer le compte d'un enseignant et le met en session
# Param POST : les infos de connection de l'enseignant
#               {"firstname": "Matéo",
#                "surname": "Avventuriero",
#                "password": "DoctorWhoCestCool"}
@teachers.route('/signup', methods=['POST'])
def signup():
    # Récupère les données en POST
    data = request.get_json(force=True)
    firstname = data.get("firstname")
    surname = data.get("surname")
    password = data.get("password")

    # Si un des champs est vide (en plus de la vérification client)
    if not (firstname and surname and password):
        return jsonify({
            "status": 401,
            "reason": "Prénom, nom ou mot de passe invalide"
        }), 401
    else:
        registerTeacher(firstname, surname, password)
        return jsonify(success=True), 200


# Met en session un enseignant
# Param POST : les infos de connection de l'enseignant
#               {"firstname": "Hugo",
#                "surname": "Vaillant",
#                "password": "StarWarsCestNul"}
@teachers.route('/signin', methods=['POST'])
def signin():
    # Récupère les données en POST
    data = request.get_json(force=True)
    firstname = data.get("firstname")
    surname = data.get("surname")
    password = data.get("password")

    # Si un des champs est vide (en plus de la vérification client)
    if not (firstname and surname and password):
        return jsonify({
            "status": 401,
            "reason": "Prénom, nom ou mot de passe invalide"
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
                "reason": "Prénom, nom ou mot de passe invalide"
            }), 401
