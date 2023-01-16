from flask import Blueprint, request, jsonify

questions = Blueprint('questions', __name__, url_prefix='/questions')

@questions.route('/getQuestions/<id>', methods=['GET'])
def getQuestions(questionID):
    return []

@questions.route('/addQuestion', methods=['POST'])
def addQuestion():
    data = request.json
    return jsonify(data)

