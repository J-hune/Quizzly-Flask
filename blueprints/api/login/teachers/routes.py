from flask import Blueprint, jsonify, request
from functions.teachers import registerTeacher, teacherExists

teachers = Blueprint('teachers', __name__, url_prefix='/teachers')


# Créer le compte d'un enseignant et le met en session
# Param POST : les infos de registration de l'enseignant (dico)
#               {"firstname": "Matéo",
#                "surname": "Avventuriero",
#                "password": "DoctorWhoCestCool"}
# Return : les infos de l'enseignant (session["user"])
#               {"id": 42
#                "firstname": "Matéo",
#                "surname": "Avventuriero",
#                "type": "Enseignant"}
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
        teacher = registerTeacher(firstname, surname, password)
        if teacher == 0:
            return jsonify({
                "status": 400,
                "reason": "Échec de la requête"
            }), 400
        else:
            return jsonify({
                "success": True,
                "user": teacher
            }), 200


# Met en session un enseignant
# Param POST : les infos de connexion de l'enseignant (dico)
#               {"firstname": "Hugo",
#                "surname": "Vaillant",
#                "password": "StarWarsCestNul"}
# Return : les infos de l'enseignant (session["user"])
#               {"id": 13
#                "firstname": "Hugo",
#                "surname": "Vaillant",
#                "type": "Enseignant"}
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
