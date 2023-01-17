from flask import Blueprint, request, jsonify
import app
import functions.users as functionUsers

users = Blueprint('users', __name__, url_prefix='/users')


# Route qui récupère tous les utilisateurs
@users.route('/getUsers', methods=['GET'])
def getUsers():
    return functionUsers.getUsers()


# Route qui récupère un utilisateur selon son id
@users.route('/getUser/<id>', methods=['GET'])
def getUser(id):
    if not (id):
        return jsonify({
            "status": 400,
            "reason": "Id Invalid"
        }), 400
    data = functionUsers.getUser(id)

    # Si on a une taille different de 1 c'est que l'on a un autre utilisateur
    if len(data) != 1:
        return jsonify({
            "status": 400,
            "reason": "Id Invalid"
        }), 400
    return data


# Route qui ajoute un utilisateur
@users.route('/addUser', methods=['POST'])
def addUser():
    # Je suis parti du principe que data est de cette forme
    # {"nom" : "Bernard","prenom" : "Rapoe", "password" : "AZERTYUIOP"}
    data = request.json

    # Vérifie si on a nos données
    try:
        var = data["nom"]
        var = data["prenom"]
        var = data["password"]
    except KeyError:
        return jsonify({
            "status": 400,
            "reason": "First Name, Surname or Password Incomplete"
        }), 400

    # La fonction renvoie True si elle a ajouté dans la table et False sinon
    if functionUsers.addUser(data["nom"], data["prenom"], data["password"]):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 400,
            "reason": "Insertion impossible dans la base de donnée"
        }), 400
