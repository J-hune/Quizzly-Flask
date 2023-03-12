from flask import Blueprint, request, jsonify, session
import functions.questions as function_questions

questions = Blueprint('questions', __name__, url_prefix='/questions')


# Ajoute une nouvelle question
# Param POST : les infos de la question (dico)
#               {
#                "enonce": "Ceci est une question de test avec beaucoup de mots",
#                "type": 0,
#                "id": 5,
#                "numerique" : "332,33"
#                "etiquettes": [{"couleur": "000000", "nom": "Algo"}, ...],
#                "reponses": [{"reponse": "La réponse D", "reponseJuste": False}, ...],
#               }
@questions.route('/addQuestion', methods=['POST'])
def addQuestion():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        user = session.get("user")
        if function_questions.addQuestion(
                data["type"],
                data["enonce"],
                user["id"],
                data["etiquettes"],
                data["reponses"],
                data["numerique"]
        ):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 400,
                "reason": "Ajout des données impossible"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Modifie une question
# Param GET : l'id de la question (int)
# Param POST : les infos de la question (dico)
#                 {
#                  "enonce": "Ceci est une question de test avec beaucoup de mots",
#                  "type": 0,
#                  "id": 5,
#                  "numerique" : "332,33"
#                  "etiquettes": [{"couleur": "000000", "nom": "Algo"}, ...],
#                  "reponses": [{"reponse": "La réponse D", "reponseJuste": False}, ...],
#                 }
@questions.route('/editQuestion/<id>', methods=['POST', 'GET'])
def editQuestion(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        if function_questions.editQuestion(
                id,
                data["type"],
                data["enonce"],
                data["etiquettes"],
                data["reponses"],
                data["numerique"]
        ):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 400,
                "reason": "Ajout des données impossible"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Supprime une question
# Param GET : un id de question
@questions.route('/deleteQuestion/<id>', methods=['GET'])
def deleteQuestion(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        if function_questions.deleteQuestion(id):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 400,
                "reason": "Impossible de supprimer la question"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Renvoie toutes les questions d'un enseignant selon les étiquettes choisies
# Param GET : les étiquettes sélectionnées
# Return : les infos des questions (tab de dico)
#            [
#             {
#               "id": 1,
#               "type": 0,
#               "enonce": "Combien vaut pi ?",
#               "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#               "numerique": "3.14",
#               "reponses": [{"id": 1, "question": 1, "reponse": "Trois quatorze", "reponseJuste": 1},...],
#             }, ...
#            ]
@questions.route('/getQuestions/', methods=['GET'])
@questions.route('/getQuestions/<label>', methods=['GET'])
def getQuestions(label=None):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        questions = function_questions.getQuestions(user['id'], label)
        return jsonify(questions)
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Renvoie une question
# Param GET : l'id de la question
# Return : les infos de la question (dico)
#              {
#                 "id": 1,
#                 "type": 0,
#                 "enonce": "Qui a calculé la circonférence de la terre en -200 av JC ?",
#                 "enseignant": 1
#                 "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#                 "numerique": ""
#                 "reponses": [{"id": 1, "question": 1, "reponse": "Ératosthène", "reponseJuste": 1},...],
#               }
@questions.route('/getQuestion/<id>', methods=['GET'])
def getQuestion(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        question = function_questions.getQuestion(id)
        if not question:
            return jsonify({
                "status": 400,
                "reason": "Question non valide"
            }), 400
        return jsonify(question)
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400