from flask import Blueprint, jsonify, request, session

import functions.users
from functions.students import addStudent, removeStudent

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
def removeStudent(studentId):
    # Si il est en session
    if 'user' in session:

        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":

            # Renvoie 0 si bon
            # 1 si mauvaise requete
            # 2 si l'étudiant n'est pas trouvé
            remove = functions.students.removeStudent(studentId)

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
    # Si il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":

            # Renvoie True si tout s'est bien passé
            if functions.students.removeAllStudent():
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
