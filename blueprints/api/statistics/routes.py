from flask import Blueprint, jsonify, session
import functions.statistics.overall

statistics = Blueprint('statistics', __name__, url_prefix='/statistics')


# Récupère les statistiques générales de l'enseignant
# Param GET : nb, le nombre de jours à calculer par rapport à aujourd'hui, de base à 120 (int)
# Return : un dico avec les statistiques générales de l'enseignant
#
#           /!\ chaque index des tableaux correspondent à la même donnée (pour le jour jours[i],
#           participantsSequences[i] ont participé à des séquences et participantsQuestions[i]
#           ont participé à des questions) /!\
#
#              {
#                "jours": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                "participantsSequences": [10, 20.5, 0, 40, 50],
#                "participantsQuestions": [2, 0, 4, 50, 0],
#                "totalQuestions": 10,
#                "totalSequences": 21
#              }
@statistics.route('/getOverallStats', methods=['GET'])
@statistics.route('/getOverallStats/<nb>', methods=['GET'])
def getOverallStats(nb=120):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Le convertit en int, car la route GET le donne en string
        nb_jour = int(nb)
        stats = functions.statistics.overall.getOverallStats(session["user"]["id"],  nb_jour)
        if stats:
            return jsonify(stats)
        else:
            return jsonify({
                "status": 400,
                "reason": "Échec de la requête"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400
