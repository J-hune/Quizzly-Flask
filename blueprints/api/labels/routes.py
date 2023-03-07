from flask import Blueprint, jsonify, session, request
import functions.fonctionLabels as fonctionLabels

label = Blueprint('labels', __name__, url_prefix='/labels')


@label.route('/getLabels', methods=['GET'])
def getLabels():
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")

        # Récupération des étiquettes sous la forme [["nom", "couleur_en_hexa"],...]
        labels = fonctionLabels.getLabelsUsed(user['id'])
        return jsonify(labels)
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


@label.route('/getAllLabels', methods=['GET'])
def getAllLabels():
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")

        # Récupération des étiquettes sous la forme [["nom", "couleur_en_hexa"],...]
        labels = fonctionLabels.getLabels(user['id'])
        return jsonify(labels)
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


@label.route('/addLabel/<name>/<hexa>', methods=['POST', 'GET'])
def addLabel(name, hexa):
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        # Si l'ajout de l'étiquette a réussi
        if fonctionLabels.addLabel(name, hexa, user["id"]):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "Impossible d'ajouter l'étiquette"
            }), 401
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route pour modifier une étiquette
# Reçoit en POST un dictionnaire {id, nom, couleur}
@label.route('/editLabel', methods=['POST'])
def editLabel():
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        # Si l'ajout de l'étiquette a réussi
        if fonctionLabels.editLabel(data["id"], data["nom"], data["couleur"]):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "Impossible de modifier l'étiquette"
            }), 401
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route pour supprimer une étiquette
# Reçoit en GET un id d'étiquette
@label.route('/deleteLabel/<id>', methods=['GET'])
def deleteLabel(id):
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        # Réussite de la suppression de l'étiquette
        if fonctionLabels.deleteLabel(id):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 401,
                "reason": "Impossible de supprimer l'étiquette"
            }), 401
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400