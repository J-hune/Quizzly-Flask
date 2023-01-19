from flask import Blueprint, request, jsonify, session
import app
import functions.questions as functionQuestions

questions = Blueprint('questions', __name__, url_prefix='/questions')


# Route qui renvoie les questions selon l'id d'un utilisateur
@questions.route('/getQuestions/<label>', methods=['GET'])
def getQuestions(label):
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


# Route qui permet l'ajout de nouvelles questions
@questions.route('/addQuestion', methods=['POST'])
def addQuestion():

    # Je suis parti du principe que data est de cette forme
    # {"enonce" : "Est-ce que l'algo et le php sont amusants ?",
    #     # "liensEtiquettesQuestions": ["algo", "php"],
    #     # "reponses": [ {"reponse": "Non", "reponseJuste":0 }, {"reponse": "Oui", "reponseJuste":1 } ]
    #     # }

    # Vérification que l'utilisateur est en session
    if 'user' in session:
        data = request.get_json(force=True)
        user = session.get("user")
        if functionQuestions.addQuestions(
                data["enonce"],
                user["id"],
                data["liensEtiquettesQuestions"],
                data["reponses"]
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
    # Je suis parti du principe que data est de cette forme {"question" : 2, "reponse" : "Non"}
    data = request.get_json(force=True)

    # Vérifie si on a nos données
    if not (data["question"] and data["reponse"] and data["reponseJuste"]):
        return jsonify({
            "status": 400,
            "reason": "First Name, Surname or Password Incomplete"
        }), 400

    # La fonction renvoie True si elle a ajouté dans la table et False sinon
    if functionQuestions.addReponses(data["question"], data["reponse"], data["reponseJuste"]):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 400,
            "reason": "Insertion impossible dans la base de donnée"
        }), 400


@questions.route('/deleteQuestion/<id>', methods=['GET'])
def deleteQuestion(id):

    # Vérification que l'utilisateur est en session
    if 'user' in session:
        user = session.get("user")
        if functionQuestions.deleteQuestion(id, user["id"]):
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
