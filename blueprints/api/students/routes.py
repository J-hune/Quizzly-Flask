from flask import Blueprint, jsonify, request, session

import functions.students
from functions.students import addStudent, removeStudent
from functions.statistics.students.overall import getLastSequences


students = Blueprint('student', __name__, url_prefix='/students')


# Insère les étudiants
# Param POST : un tableau avec les étudiants
#               [{"id" : 1332214, "nom":"DeLaTour", "prenom":"Jean"},
#                {"id" : 1322324, "nom":"DeLaTour", "prenom":"Jeanne"}, ...]
# Return : le nombre d'étudiants inséré (int)
@students.route('/insertStudents', methods=['POST'])
def insertStudents():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)

            nb_student = addStudent(data)
            if nb_student != -1:
                return jsonify({"success": True, "result": nb_student}), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Supprime un étudiant
# Param GET : id de l'étudiant (int)
@students.route('/removeStudent/<id>', methods=['GET'])
def removeStudent(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":

            check = functions.students.removeStudent(id)
            if check == 0:
                return jsonify(success=True), 200
            elif check == 2:
                return jsonify({
                    "status": 400,
                    "reason": "L'étudiant n'existe pas"
                }), 400
            elif check == 1:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400

        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Supprime tous les étudiants
@students.route('/removeAllStudent/', methods=['GET'])
def removeAllStudent():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":

            if functions.students.removeAllStudents():
                return jsonify(success=True), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400

        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Sinon pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Récupère tous les étudiants
# Return : tableau de dico d'étudiant sous la forme suivante
#            [
#              {
#                "id": 42,
#                "prenom": "John",
#                "nom": "Smith",
#                "avatar": "data:image/png;base64,iVBORw0KGgo..."
#               }, ...
#            ]
@students.route('/getAllStudents', methods=['GET'])
def getAllStudents():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            etudiants = functions.students.getAllStudents()
            return jsonify(etudiants)
        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # S'il n'est pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Modifie l'avatar de l'étudiant en session
# Param POST : l'avatar de l'étudiant (dico)
#                   {"avatar":"data:image/png;base64,iVBORw0KGgo..."}
@students.route('/editAvatar', methods=['POST'])
def editAvatar():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est étudiant
        if session["user"]["type"] == "Etudiant":
            user = session.get("user")
            data = request.get_json(force=True)
            # Renvoie True si tout s'est bien passé
            if functions.students.editAvatar(user["id"], data["avatar"]):
                return jsonify(success=True), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400

        # Ce n'est pas un étudiant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Sinon pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Récupère les 3 dernières participations d'un élève
# Return : les trois dernières diffusions de l'étudiant (tab de dico)
#                [{"id":7,                           (--> id de la séquence qui a été diffusé)
#                  "enseignant":"Michel Staelens",
#                  "participants":25,
#                  "pourcentage":"82,7",             (--> pourcentage de réussite de l'étudiant)
#                  "date":07032023
#                  }, ...]
@students.route('/getLastSequences', methods=['GET'])
def getLastSequences():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est étudiant
        if session["user"]["type"] == "Etudiant":
            user = session.get("user")
            last_sequences = functions.statistics.students.overall.getLastSequences(user["id"])
            if last_sequences != 0:
                return jsonify(last_sequences)
            # Si l'étudiant n'a participé à aucune séquence
            else:
                return jsonify({
            "status": 400,
            "reason": "Échec de la requête"
        }), 400
        # Ce n'est pas un étudiant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Sinon pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400