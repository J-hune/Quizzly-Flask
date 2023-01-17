from flask import Blueprint, request, jsonify
import app
import functions.questions as functionQuestions

questions = Blueprint('questions', __name__, url_prefix='/questions')


# Route qui renvoie les questions selon l'id d'un utilisateur
@questions.route('/getQuestions/<userId>', methods=['GET'])
def getQuestions(userId):
    return functionQuestions.getQuestions(userId)


# Route qui permet l'ajout de nouvelles questions
@questions.route('/addQuestion', methods=['POST'])
def addQuestion():

    # Je suis parti du principe que data est de cette forme
    # {"enonce" : "Est-ce que l'algo est amusant ?", "user" : 1}
    data = request.json

    if not (data["enonce"] and data["user"]):
        return jsonify({
            "status": 400,
            "reason": "Enonce and User Id Invalid"
        }), 400

    functionQuestions.addQuestions(data["enonce"], data["user"])
    return jsonify(data)


# Route qui permet l'ajout de nouvelles réponses
@questions.route('/addReponses', methods=['POST'])
def addReponses():
    # Je suis parti du principe que data est de cette forme {"question" : 2, "reponse" : "Non"}
    data = request.json

    # Vérifie si on a nos données
    try:
        var = data["question"]
        var = data["reponse"]
    except KeyError:
        return jsonify({
            "status": 400,
            "reason": "First Name, Surname or Password Incomplete"
        }), 400

    # La fonction renvoie True si elle a ajouté dans la table et False sinon
    if functionQuestions.addReponses(data["question"], data["reponse"]) :
        return jsonify(success=True), 200
    else :
        return jsonify({
            "status": 400,
            "reason": "Insertion impossible dans la base de donnée"
        }), 400

