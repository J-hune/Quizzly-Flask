from flask import Blueprint, jsonify, session
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