from flask import Blueprint, jsonify, session, request
import functions.fonctionLabels as fonctionLabels

label = Blueprint('labels', __name__, url_prefix='/labels')


# Ajoute une étiquette
# Param GET : - name : nom de l'étiquette (string)
#             - hexa : couleur de l'étiquette en hexa (string)
# Return : l'id de l'étiquette ajoutée (int)
@label.route('/addLabel/<name>/<hexa>', methods=['POST', 'GET'])
def addLabel(name, hexa):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            user = session.get("user")
            label_id = fonctionLabels.addLabel(name, hexa, user["id"])
            # Si l'ajout de l'étiquette a réussi
            if label_id:
                return jsonify({
                    "success": True,
                    "id": label_id
                }), 200
            else:
                return jsonify({
                    "status": 401,
                    "reason": "Impossible d'ajouter l'étiquette"
                }), 401
        # Ce n'est pas un enseignant
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


# Modifie une étiquette
# Param POST : un dico avec les nouvelles infos
#               {"id": 1, "nom": Python", "couleur": "FFFF00"}
@label.route('/editLabel', methods=['POST'])
def editLabel():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            data = request.get_json(force=True)
            # Vérifie si l'étiquette existe et qu'elle lui appartient
            if fonctionLabels.searchLabelWithId(data["id"], session["user"]["id"]):
                if fonctionLabels.editLabel(data["id"], data["nom"], data["couleur"]):
                    return jsonify(success=True), 200
                else:
                    return jsonify({
                        "status": 401,
                        "reason": "Impossible de modifier l'étiquette"
                    }), 401
            else:
                return jsonify({
                    "status": 403,
                    "reason": "Cette etiquette ne vous appartient pas ou n'existe pas"
                }), 403
        # Ce n'est pas un enseignant
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


# Supprime une étiquette
# Param GET : id de l'étiquette (int)
@label.route('/deleteLabel/<id>', methods=['GET'])
def deleteLabel(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            # Vérifie si l'étiquette existe et qu'elle lui appartient
            if fonctionLabels.searchLabelWithId(id, session["user"]["id"]):
                if fonctionLabels.deleteLabel(id):
                    return jsonify(success=True), 200
                else:
                    return jsonify({
                        "status": 401,
                        "reason": "Impossible de supprimer l'étiquette"
                    }), 401
            else:
                return jsonify({
                    "status": 403,
                    "reason": "Cette etiquette ne vous appartient pas ou n'existe pas"
                }), 403
        # Ce n'est pas un enseignant
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


# Renvoie toutes les étiquettes de l'enseignant
# Return : les étiquettes de l'enseignant (tab de dico)
#             [{"id":666, "nom":"Modèle de calcul", "couleur":"FF0000"}, {...}, ...]
@label.route('/getLabels', methods=['GET'])
def getLabels():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            user = session.get("user")
            labels = fonctionLabels.getLabels(user['id'])
            return jsonify(labels)
        # Ce n'est pas un enseignant
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
