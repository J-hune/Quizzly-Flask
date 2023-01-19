from flask import Blueprint, jsonify, session
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


@label.route('/getLabels', methods=['GET'])
def getLabels():
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


@label.route('/getLabel/<name>', methods=['GET'])
def getLabelData(name):
    # Si l'obtention de l'étiquette a réussi
    res = fonctionLabels.searchLabel(name)
    if res:
        return res
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


# Routes pour ajouter de nouvelles étiquettes
@label.route('/addLiensEtiquettesQuestions/<etiquette>/<question>', methods=['GET'])
def addLiensEtiquettesQuestions(etiquette, question):

    # Si l'ajout de l'étiquette se passe bien
    if fonctionLabels.addLiensEtiquettesQuestions(etiquette, question):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 400,
            "reason": "Impossible d'ajouter le lien entre l'etiquette et la question"
        }), 400


# Routes pour get les étiquettes en fonction des questions
@label.route('/getLiensEtiquettes/<questionId>', methods=['GET'])
def getLiensEtiquettes(questionId):
    return fonctionLabels.getLiensEtiquettes(questionId)

