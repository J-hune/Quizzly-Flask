from flask import Blueprint, request, jsonify
import app
import functions.users as functionUsers

users = Blueprint('users', __name__, url_prefix='/users')


# Route qui récupère tous les utilisateurs
@users.route('/getUsers/<type>', methods=['GET'])
def getUsers(type):
    return functionUsers.getUsers(type)


# Route qui récupère un utilisateur selon son id
@users.route('/getUser/<type>/<id>', methods=['GET'])
def getUser(type, id):
    if not (id and type):
        return jsonify({
            "status": 400,
            "reason": "Id or type invalid"
        }), 400
    data = functionUsers.getUser(type, id)

    # Si on a une taille different de 1, c'est que l'on a un autre utilisateur
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
    # {"nom" : "Bernard","prenom" : "Rapoe", "password" : "AZERTYUIOP", "type" : "Etudiants"}
    data = request.get_json(force=True)

    # Vérifie si on a nos données
    try:
        var = data["nom"]
        var = data["prenom"]
        var = data["password"]
        var = data["type"]
    except KeyError:
        return jsonify({
            "status": 400,
            "reason": "First Name, Surname, Password or TYPE Incomplete"
        }), 400

    # La fonction renvoie True si elle a ajouté dans la table et False sinon
    if functionUsers.addUser(data["nom"], data["prenom"], data["password"], data["type"]):
        return jsonify(success=True), 200
    else:
        return jsonify({
            "status": 400,
            "reason": "Insertion impossible dans la base de donnée"
        }), 400
