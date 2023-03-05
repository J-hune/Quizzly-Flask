from flask import Blueprint, request, jsonify, session
import functions.questions as functionQuestions

questions = Blueprint('questions', __name__, url_prefix='/questions')


# Route qui renvoie les questions selon l'id d'un utilisateur
@questions.route('/getQuestions/', methods=['GET'])
@questions.route('/getQuestions/<label>', methods=['GET'])
def getQuestions(label=None):
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        questions = functionQuestions.getQuestions(user['id'], label)
        return jsonify(questions)
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route qui renvoie la question ayant l'id donné
@questions.route('/getQuestion/<id>', methods=['GET'])
def getQuestion(id):
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        question = functionQuestions.getQuestion(id)
        if not question:
            return jsonify({
                "status": 400,
                "reason": "Question non valide"
            }), 400
        return jsonify(question)
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route qui permet l'ajout de nouvelles questions
@questions.route('/addQuestion', methods=['POST'])
def addQuestion():
    # Je suis parti du principe que data est de cette forme
    # data = {
    #   "enonce": "Ceci est une question de test avec beaucoup de mots",
    #   "type": 0,
    #   "id": 5,
    #   "numerique" : 332,33
    #   "etiquettes": [
    #     {
    #       "couleur": "000000",
    #       "nom": "algo"
    #     }
    #   ],
    #   "reponses": [
    #     {
    #       "reponse": "",
    #       "reponseJuste": False
    #     }
    #   ],
    # }

    # Vérification que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        user = session.get("user")
        if functionQuestions.addQuestion(
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
            "reason": "Session non disponible"
        }), 400


# Route qui permet l'ajout de nouvelles réponses
@questions.route('/addReponses', methods=['POST'])
def addReponses():
    # Je suis parti du principe que data est de cette forme {"type":1, "question" : 2, "reponse" : "Non", "reponseJuste" : 0}
    data = request.get_json(force=True)

    # Vérifie si on a nos données
    if not (data["question"] and data["reponse"] and data["reponseJuste"]):
        return jsonify({
            "status": 400,
            "reason": "First Name, Surname or Password Incomplete"
        }), 400

    # La fonction renvoie True si elle a ajouté dans la table et False sinon
    if functionQuestions.addReponse(data["reponse"], data["reponseJuste"], data["question"]):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 400,
            "reason": "Insertion impossible dans la base de donnée"
        }), 400


# Route qui permet de supprimer une question
@questions.route('/deleteQuestion/<id>', methods=['GET'])
def deleteQuestion(id):
    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        if functionQuestions.deleteQuestion(id):
            return jsonify(success=True), 200
        else:
            return jsonify({
                "status": 400,
                "reason": "Impossible de supprimer la question"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "reason": "Session non disponible"
        }), 400


# Route qui permet d'editer une question
@questions.route('/editQuestion/<id>', methods=['POST', 'GET'])
def editQuestion(id):
    # Je suis parti du principe que data est de cette forme
    # {
    #   "enonce": "Ceci est une question de test avec beaucoup de mots",
    #   "type": 0,
    #   "etiquettes": [
    #     {
    #       "couleur": "000000",
    #       "nom": "algo"
    #     }
    #   ],
    #   "numerique": 332, 33,
    #   "id": 8,
    #   "reponses": [
    #     {
    #       "reponse": "",
    #       "reponseJuste": False
    #     }
    #   ],
    #   "user": 5
    # }

    # Vérification que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        user = session.get("user")
        if functionQuestions.editQuestion(id,
                                          data["enonce"],
                                          data["type"],
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
            "reason": "Session non disponible"
        }), 400
