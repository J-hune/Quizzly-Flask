from flask import Blueprint, jsonify, session, request

evaluations = Blueprint('evaluations', __name__, url_prefix='/evaluations')


@evaluations.route('/generateEvaluations/', methods=['POST'])
def generateEvaluations():

    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            user = session.get("user")
            data = request.get_json(force=True)
            result = generateEvaluations(user['id'], data)
            if type(result) == tuple:
                if result[0] == 0:
                    return jsonify({"success": False, "value": "Impossible de faire les sujets avec la configuration actuel, questions maximum = "
                                                               + result[2][2][1]+" questions minimum = "+result[2][2][0]+
                                                               " sujets maximum ="+result[2][1]})
                if result[0] == 1:
                    return jsonify({"success": False, "value": result[1]})
            else:
                return jsonify({"success": True, "value": result})
        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400