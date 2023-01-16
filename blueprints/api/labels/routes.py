from flask import Blueprint, request

label = Blueprint('labels', __name__, url_prefix='/labels')

@label.route('/getLabels', methods=['GET'])
def getLabelsData():
    return {'key': 'value'}

@label.route('/addLabel/<id>', methods=['POST'])
def addLabel(label):
    print(label)
    data = request.json
    return {'key': 'value'}