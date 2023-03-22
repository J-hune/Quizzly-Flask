from flask import Blueprint, request, jsonify, session

import functions.sequences as function_sequences

sequences = Blueprint('sequences', __name__, url_prefix='/sequences')


# Ajoute une séquence
# Param POST : un dico avec les infos de la séquence
#               {"titre": "Le système solaire", "questions": [4,52,12,9]}
@sequences.route('/addSequence', methods=['POST'])
def addSequence():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est un enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)
            if function_sequences.addSequence(session["user"]["id"],  data['titre'], data['questions']):
                return jsonify({"success": True}), 200
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Modifie une Séquence
# Param GET : id de la séquence (int)
# Param POST : nouvelles infos de la séquence (dico)
#               {"titre": "Le sens de la vie", "questions": [42]}
@sequences.route('/editSequence/<id>', methods=['POST'])
def editSequence(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Vérifie que la séquence lui appartient et qu'elle existe
            if session["user"]["id"] == function_sequences.getEnseignant(id):
                # Récupère les données en POST
                data = request.get_json(force=True)
                if function_sequences.editSequence(id, data['titre'], data['questions']):
                    return jsonify(success=True), 200
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Échec de la requête"
                    }), 400
            # Ce n'est pas sa séquence
            else:
                return jsonify({
                    "status": 400,
                    "reason": "La séquence sélectionnée est introuvable ou ne vous appartient pas"
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


# Supprime une Séquence
# Param GET : id de la séquence (int)
@sequences.route('/removeSequence/<id>', methods=['GET'])
def removeSequence(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Vérifie que la séquence lui appartient et qu'elle existe
            if session["user"]["id"] == function_sequences.getEnseignant(id):
                if function_sequences.removeSequence(id):
                    return jsonify(success=True), 200
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Échec de la requête"
                    }), 400
            # Ce n'est pas sa séquence
            else:
                return jsonify({
                    "status": 400,
                    "reason": "La séquence sélectionnée est introuvable ou ne vous appartient pas"
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


# Renvoie une séquence
# Param GET : l'id de la séquence (int)
# Return : les informations de la séquence (dico)
#             {"id":1,
#              "titre":"Les Array list en java",
#              "questions":[6, 18]
#             }
@sequences.route("/getSequence/<id>", methods=["GET", "POST"])
def getSequence(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Vérifie que la séquence existe et qu'elle lui appartient
            if session["user"]["id"] == function_sequences.getEnseignant(id):
                result = function_sequences.getSequence(id)
                if result:
                    return jsonify(result)
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Échec de la requête"
                    }), 400
            # Ce n'est pas sa séquence
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
            "reason": "La connection a échouée"
        }), 400


# Renvoie toutes les séquences d'un enseignant
# Param GET : l'id de l'enseignant (int)
# Return : les informations de la séquence (dico)
#             [{"id":1,
#              "titre":"Les Array list en java",
#              "questions":[6, 18]}
#              "listeEtiquettes":["{"nom":"Java", "couleur":"c47f31"}, {...}]
#              }, {...}, ...]
@sequences.route("/getAllSequences", methods=["GET"])
def getAllSequences():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est un enseignant
        if session["user"]["type"] == "Enseignant":
            result = function_sequences.getAllSequences(session["user"]["id"])
            if result == 0:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
            else:
                return jsonify(result)
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
