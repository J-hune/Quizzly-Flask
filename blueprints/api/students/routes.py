from flask import Blueprint, jsonify, request, session

import functions.users
from functions.students import addStudent, removeStudent
from functions.sequences import getLastSequences


students = Blueprint('student', __name__, url_prefix='/students')


# Route pour insérer un étudiant
@students.route('/insertStudents', methods=['POST'])
def insertStudents():
    # Si il est en session
    if 'user' in session:

        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)

            # Renvoie -1 si on n'a pas réussi à insérer un étudiant, ou sinon le nombre d'étudiants réellement insérer
            nbStudent = addStudent(data)

            if nbStudent != -1:
                return jsonify({"success": True, "result": nbStudent}), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Insert etudiant Invalid"
                }), 400
        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Forbidden"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route pour supprimer un étudiant
@students.route('/removeStudent/<id>', methods=['GET'])
def removeStudent(id):

    # Si il est en session
    if 'user' in session:

        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":

            # 0 si réussite
            # 1 si mauvaise requête
            # 2 si l'étudiant n'est pas trouvé
            remove = functions.students.removeStudent(id)

            if remove == 0:
                return jsonify(success=True), 200
            elif remove == 2:
                return jsonify({
                    "status": 400,
                    "reason": "Etudiant not found"
                }), 400
            elif remove == 1:
                return jsonify({
                    "status": 400,
                    "reason": "Delete etudiant Invalid"
                }), 400

        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Forbidden"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route pour supprimer tous les étudiants
@students.route('/removeAllStudent/', methods=['GET'])
def removeAllStudent():
    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":

            # Renvoie True si tout s'est bien passé
            if functions.students.removeAllStudents():
                return jsonify(success=True), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Delete etudiant Invalid"
                }), 400

        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Forbidden"
            }), 403
    # Sinon pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


@students.route('/getAllStudents', methods=['GET'])
def getAllStudents():
    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
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
            "reason": "Ajout des données impossible"
        }), 400

@students.route('/editAvatar', methods=['POST'])
def editAvatar():
    # S'il est en session
    if 'user' in session:
        # Si c'est un étudiant
        if session["user"]["type"] == "Etudiant":
            user = session.get("user")
            data = request.get_json(force=True)
            # Renvoie True si tout s'est bien passé
            if functions.students.editAvatar(user["id"], data["avatar"]):
                return jsonify(success=True), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Edit d'avatar impossible"
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
            "reason": "Ajout des données impossible"
        }), 400


# Route qui récupère les 3 dernières participations d'un élève
@students.route('/getLastSequences', methods=['GET'])
def getLastSequences():
    if 'user' in session:
        # Si c'est un étudiant
        if session["user"]["type"] == "Etudiant":
            user = session.get("user")
            sequences = functions.sequences.getLastSequences(user["id"])
            if sequences != 0:
                return jsonify(sequences)
            # Si l'étudiant n'a participé à aucune séquence
            else:
                return jsonify({
            "status": 400,
            "reason": "Récupération des données impossible"
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
            "reason": "Récupération des données impossible"
        }), 400