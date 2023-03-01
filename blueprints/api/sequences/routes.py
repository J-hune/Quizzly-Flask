from flask import Blueprint, request, jsonify, session

import functions.sequences as functionSequences

sequences = Blueprint('sequences', __name__, url_prefix='/sequences')

# Route pour insérer une Sequence
@sequences.route('/AddSequence', methods=['POST'])
def AddSequence():
    # Si il est en session
    if 'user' in session:

        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)
            questions = data['questions']
            if functionSequences.addSequence('user', questions):
                return jsonify({"success": True}), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Insert question Invalid"
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
@sequences.route('/editSequence/<id>', methods=['GET', 'POST'])
def editSequence(id):

    # Si il est en session
    if 'user' in session:
        if 'user' == functionSequences.GetEnseignant(id):
            # Si c'est un enseignant
            if session["user"]["type"] == "Enseignant":
                data = request.get_json(force=True)
                questions = data['questions']
                # Renvoie 0 si bon
                # 1 si mauvaise request
                # 2 si l'étudiant n'est pas trouvé
                edit = functionSequences.editSequence(id, questions)
                if edit == 0:
                    return jsonify(success=True), 200
                elif edit == 2:
                    return jsonify({
                        "status": 400,
                        "reason": "Sequence not found"
                    }), 400
                elif edit == 1:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
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

@sequences.route('/removeSequence/<id>', methods=['GET'])
def removeSequence(id):
    # Si il est en session
    if 'user' in session:
        if 'user' == functionSequences.GetEnseignant(id):
            # Si c'est un enseignant
            if session["user"]["type"] == "Enseignant":
                # Renvoie 0 si bon
                # 1 si mauvaise request
                # 2 si l'étudiant n'est pas trouvé
                remove = functionSequences.RemoveSequence(id)
                if remove == 0:
                    return jsonify(success=True), 200
                elif remove == 2:
                    return jsonify({
                        "status": 400,
                        "reason": "Sequence not found"
                    }), 400
                elif remove == 1:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
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