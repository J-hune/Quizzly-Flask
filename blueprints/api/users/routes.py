from flask import Blueprint
import app

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/getUsers', methods=['GET'])
def getUsers():
    return []

@users.route('/getUser/<id>', methods=['GET'])
def getUser(userID):
    return []

@users.route('/addUser', methods=['POST'])
def addUser():
    return []