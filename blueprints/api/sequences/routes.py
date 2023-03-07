from flask import Blueprint, request, jsonify, session

import functions.sequences as functionSequences

sequences = Blueprint('sequences', __name__, url_prefix='/sequences')


# Route pour insérer une Sequence
@sequences.route('/addSequence', methods=['POST'])
def addSequence():
    # S'il est en session
    if 'user' in session:

        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)

            titre = data['titre']
            questions = data['questions']

            if functionSequences.addSequence(session["user"]["id"], titre, questions):
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
                "reason": "Permission non accordée"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route pour modifier une Séquence
@sequences.route('/editSequence/<id>', methods=['POST'])
def editSequence(id):

    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            if session["user"]["id"] == functionSequences.getEnseignant(id):
                data = request.get_json(force=True)
                titre = data['titre']
                questions = data['questions']

                # Renvoie 0 si bon
                # 1 si mauvaise request
                # 2 si la sequence n'est pas trouvé
                edit = functionSequences.editSequence(id, titre, questions)
                if edit == 0:
                    return jsonify(success=True), 200
                elif edit == 2:
                    return jsonify({
                        "status": 400,
                        "reason": "sequence introuvable"
                    }), 400
                elif edit == 1:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
                    }), 400
            # Ce n'est pas sa sequence
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Ce n'est pas votre sequence, ou sequence introuvable"
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
            "reason": "Session non disponible"
        }), 400


# Route pour supprimer une Séquence
@sequences.route('/removeSequence/<id>', methods=['GET'])
def removeSequence(id):
    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            if session["user"]["id"] == functionSequences.getEnseignant(id):
                # Renvoie 0 si bon
                # 1 si mauvaise request
                # 2 si la sequence n'est pas trouvé
                get = functionSequences.getSequence(id)
                if get == 0:
                    return jsonify(success=True), 200
                elif get == 2:
                    return jsonify({
                        "status": 400,
                        "reason": "Sequence introuvable"
                    }), 400
                elif get == 1:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
                    }), 400
            # Ce n'est pas sa sequence
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Ce n'est pas votre sequence, ou sequence introuvable"
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
            "reason": "Session non disponible"
        }), 400


@sequences.route("/getSequence/<id>", methods=["GET", "POST"])
def getSequence(id):
    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Si c'est sa sequence ou qu'elle existe
            if session["user"]["id"] == functionSequences.getEnseignant(id):
                result = functionSequences.getSequence(id)
                if result:
                    return jsonify(result)
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
                    }), 400
            # Ce n'est pas sa sequence
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Ce n'est pas votre sequence, ou sequence introuvable"
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
            "reason": "Session non disponible"
        }), 400


@sequences.route("/getAllSequences", methods=["GET"])
def getAllSequences():
    # S'il est en session
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
                result = functionSequences.getAllSequences(session["user"]["id"])
                if result:
                    return jsonify(result)
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Edit sequence Invalid"
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
            "reason": "Session non disponible"
        }), 400
