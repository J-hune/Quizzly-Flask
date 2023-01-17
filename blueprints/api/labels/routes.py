from flask import Blueprint, jsonify
import functions.fonctionLabels as fonctionLabels
import app

label = Blueprint('labels', __name__, url_prefix='/labels')


@label.route('/supprimerLabel/<name>', methods=['GET'])
def supprimerLabel(name):
    # Si la suppression de l'étiquette a réussi
    if fonctionLabels.supprLabel(name):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 401,
            "reason": "Impossible de supprimer l'étiquette"
        }), 401


@label.route('/getLabel/<name>', methods=['GET'])
def getLabelData(name):
    # Si l'obtention de l'étiquette a réussi
    if fonctionLabels.searchLabel(name):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 401,
            "reason": "Impossible de récupérer l'étiquette"
        }), 401


@label.route('/addLabel/<name>/<hexa>', methods=['POST', 'GET'])
def addLabel(name, hexa):
    # Si l'ajout de l'étiquette a réussi
    if fonctionLabels.addLabel(name, hexa):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 401,
            "reason": "Impossible d'ajouter l'étiquette"
        }), 401
