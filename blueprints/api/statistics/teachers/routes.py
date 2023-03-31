from flask import Blueprint, jsonify, session
import functions.statistics.teachers.overall
from functions.statistics.save import removeDiffusion
from functions.statistics.teachers.exportStats import exportStatistics
from functions.statistics.teachers.students import getStatsByStudent

teachers = Blueprint('teachers', __name__, url_prefix='/teachers')


# Récupère les statistiques générales de l'enseignant
# Param GET : nb, le nombre de jours à calculer par rapport à aujourd'hui, de base à 120 (int)
# Return : un dico avec les statistiques générales de l'enseignant
#               {
#                "totalQuizzes": 21     (-> nombre de quiz/diffusions effectués)
#                "totalQuestions": 10,  (-> nombre de questions posé)
#                "successRate": 79      (-> pourcentage de réussite total)
#                "participation": {     (-> nombre de participant à des questions et séquence pour chaque jour)
#                                  "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                                  "sequences": [10, 20, 0, 40, 50],
#                                  "questions": [2, 0, 4, 50, 0]
#                                 }
#                "success": {           (-> taux de réussite pour chaque quiz/diffusion)
#                            "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                            "quiz":[10, 25, 7, 19, 13, 55, 28]
#                           }
#                "archives": [          (-> les stats de toutes les quiz/diffusions effectués)
#                             { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#                             { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#                             {...}, ...
#                            ]
#               }
#
#           /!\ chaque index des tableaux correspondent à la même donnée (pour le jour participation["days"][i],
#               participation["sequences"][i] ont participé à des séquences et participation["questions"][i]
#               ont participé à des questions)
#
@teachers.route('/getOverallStats', methods=['GET'])
@teachers.route('/getOverallStats/<nb>', methods=['GET'])  # Route non utilisée
def getOverallStats(nb=120):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            nb_jour = int(nb)  # Le convertit en int, car la route GET le donne en string
            stats = functions.statistics.teachers.overall.getOverallStats(session["user"]["id"], nb_jour)
            if stats:
                return jsonify(stats)
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
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


# Supprime une diffusion des archives
# Param GET : id de l'archive de diffusion
@teachers.route('/removeDiffusion/<id>', methods=['GET'])
def removeDiffusion(id):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
                if functions.statistics.save.removeDiffusion(id, session["user"]["id"]):
                    return jsonify(success=True), 200
                else:
                    return jsonify({
                        "status": 400,
                        "reason": "Échec de la requête"
                    }), 400
        # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    # Pas en session
    else:
        return jsonify({
            "status": 400,
            "reason": "La connection a échouée"
        }), 400


# Récupère les statistiques d'un étudiant de l'enseignant
# Param GET : - id : id de l'étudiant (int)
#             - nb : le nombre de jours à calculer par rapport à aujourd'hui, de base à 120 (int)
# Return : un dico avec les statistiques de l'étudiant de l'enseignant
#               {
#                 "etudiant": {"id": 22104627, "nom": "Bienlebonjour", "prenom": "Ceciestunprenom", "avatar": "data:image/png;base64,iVBORw0KGgo..."}
#                 "totalQuizzes": 21     (-> nombre de quiz/diffusions participé)
#                 "totalQuestions": 10,  (-> nombre de questions répondues)
#                 "successRate": 79      (-> pourcentage de réussite total)
#                 "success" = {          (-> les pourcentages de réussite au cours du temps)
#                              "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                              "sequences":[10, 25, 7, 19, 13, 0, 28]
#                              "questions":[78, 0, 0, 19, 0, 55, 44]
#                             }
#                 "archives": [          (-> les stats de toutes les quiz/diffusions effectués)
#                              { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#                              { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#                              {...}, ...
#                             ]
#               }
#
#           /!\ chaque index des tableaux correspondent à la même donnée
#
@teachers.route('/getStatsByStudent/<id>', methods=['GET'])
@teachers.route('/getStatsByStudent/<id>/<nb>', methods=['GET'])  # Route non utilisée
def getStatsByStudent(id, nb=120):
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            nb_jour = int(nb)  # Le convertit en int, car la route GET le donne en string
            stats = functions.statistics.teachers.students.getStatsByStudent(id, session["user"]["id"], nb_jour)
            if stats == -1:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
            elif stats == 0:
                return jsonify({
                    "status": 400,
                    "reason": "L'étudiant n'existe pas"
                }), 400
            else:
                return jsonify(stats)
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

@teachers.route('/exportStats/', methods=['GET'])
def exportStats():
    # Vérifie que l'utilisateur est en session
    if 'user' in session:
        # Vérifie qu'il est enseignant
        if session["user"]["type"] == "Enseignant":
            dictionnaireArchiveStat = exportStatistics(session["user"]["id"])
            if dictionnaireArchiveStat:
                return jsonify(dictionnaireArchiveStat)
            else:
                return jsonify({
                    "status": 400,
                    "reason": "Échec de la requête"
                }), 400
                # Ce n'est pas un enseignant
        else:
            return jsonify({
                "status": 403,
                "reason": "Permission non accordée"
            }), 403
    else:
        return jsonify({
            "status": 400,
            "reason": "Permission non accordée"
        }), 400
