import sqlite3
from datetime import datetime, time


# Récupère la moyenne du taux de réussite et la moyenne du nombre de participants pour chaque nb_jour derniers jours
# Pour le nombre participants, on affiche tous les jours même quand il n'y a pas eu de quiz diffusé
# Pour le taux de réussite, on affiche uniquement les jours où un quiz a été diffusé
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
#         - nb_jour : nombre de jours à calculer (int)
# Return : - participation : le nombre de participants au cours du temps (dico de tab)
#                   {     (-> nombre de participant à des questions et séquence pour chaque jour)
#                    "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                    "sequences": [10, 20, 0, 40, 50],
#                    "questions": [2, 0, 4, 50, 0]
#                   }
#           - success : les pourcentages de réussite au cours du temps (dico de tab)
#                   {           (-> taux de réussite pour chaque quiz/diffusion)
#                    "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                    "quiz":[10, 25, 7, 19, 13, 55, 28]
#                   }

#           /!\ chaque index des tableaux correspondent à la même donnée (pour le jour jours[i],
#               participantsSequences[i] personnes ont participé à des séquences et participantsQuestions[i]
#               personnes ont participé à des questions)
def getTemporalStats(cursor, enseignant, nb_jour):
    try:
        jour = datetime.timestamp(datetime.combine(datetime.now(), time.min))  # Date du jour actuel (à minuit pile)
        jour -= (86400 * (nb_jour-1))  # Jour il y a nb_jour

        # Récupère la date, le mode, le nombre de participants, le taux de réussite pour tous les quiz après le jour
        #                                           nbParticipant              nbRéponse      nbBonneRéponse
        cursor.execute("SELECT AD.date, AD.mode, COUNT(DISTINCT AR.etudiant), COUNT(AR.id), SUM(AR.est_correcte) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.date >= ? \
                                AND AD.enseignant = ? \
                                GROUP BY AD.id \
                                ORDER BY AD.date;", (jour, enseignant))
        result = cursor.fetchall()

        nb_quiz = len(result)  # Le nombre de quiz diffusés durant les nb_jour derniers jours
        participation = {"days": [], "sequences": [], "questions": []}
        success = {"days": [], "quiz": []}

        k = 0
        # Pour les nb_jour derniers jours
        for i in range(nb_jour):

            nb_quiz_jour = 0  # Nombre de quiz ce jour
            nb_participant_sequence = 0  # Nombre de participants à des séquences ce jour
            nb_participant_question = 0  # Nombre de participants à des questions ce jour
            success_rate = 0  # Nombre de quiz ce jour

            # Pour tous les quiz du jour
            while k < nb_quiz and result[k][0] < jour + 86400:
                nb_quiz_jour += 1
                success_rate += result[k][4] / result[k][3]
                # Si le quiz est une question
                if result[k][1] == 0:
                    nb_participant_question += result[k][2]
                # Sinon c'est une séquence
                else:
                    nb_participant_sequence += result[k][2]
                k += 1

            participation["days"].append(jour)
            # S'il y a eu un quiz ce jour-là, on fait une moyenne des stats
            if nb_quiz_jour > 0:
                success["days"].append(jour)
                success["quiz"].append((success_rate / nb_quiz_jour) * 100)
                participation["sequences"].append(nb_participant_sequence / nb_quiz_jour)
                participation["questions"].append(nb_participant_question / nb_quiz_jour)
            # Sinon, on met 0 pour les participants (et on n'enregistre pas le taux de succès du jour)
            else:
                participation["sequences"].append(0)
                participation["questions"].append(0)

            jour += 86400  # Jour suivant

        return participation, success

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques temporelles :", error)
        return 0


# Récupère toutes les archives des anciennes diffusions et ordonnes les données en statistiques
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
# Return : - nb_quiz : le nombre de diffusions total effectuées (int)
#          - nb_question_total : le nombre de questions total posées (int)
#          - taux_reussite_total : le taux de réussite total en pourcentage (float)
#          - archives : les stats de toutes les diffusions effectuées (tab de dico)
#               [
#                { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#                { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#                {...}, ...
#               ]
def getArchives(cursor, enseignant):
    try:
        # LEFT JOIN pour avoir également les diffusions vides (qui n'ont donc pas de liens avec ArchivesReponses)
        # L'id, le titre, le code, la date, le mode, le nombre de participants, le taux de réussite de chaque quiz
        #                                                                       nbParticipant             nbRéponse     #nbBonneRéponse       nbQuestion
        cursor.execute("SELECT AD.id, AD.titre, AD.code, AD.date, AD.mode, COUNT(DISTINCT AR.etudiant), COUNT(AR.id), SUM(AR.est_correcte), COUNT(DISTINCT AQ.id) \
                        FROM ArchivesDiffusions AD \
                        LEFT JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                        LEFT JOIN ArchivesReponses AR ON AQ.id = AR.question \
                        WHERE AD.enseignant = ? \
                        GROUP BY AD.id \
                        ORDER BY AD.date DESC;", (enseignant, ))
        result = cursor.fetchall()

        nb_quiz_done = 0  # Le nombre de diffusions réellement effectué
        nb_quiz = len(result)  # Le nombre de diffusions total
        nb_question_total = 0  # Le nombre de questions posées
        taux_reussite_total = 0  # Le pourcentage de réussite total
        archives = []  # Les archives des diffusions

        # Ordonne les données dans un tableau de dico pour chaque quiz
        for i in range(nb_quiz):
            data = {"archiveId": result[i][0],
                    "title": result[i][1],
                    "id": result[i][2],
                    "date": result[i][3],
                    "mode": result[i][4],
                    "participantCount": result[i][5]
                    }

            nb_question_total += result[i][8]  # Additionne les questions posées

            # Si le quiz a réellement été effectué (ce n'est pas une diffusion vide)
            if result[i][7] is not None:
                pourcentage = (result[i][7] / result[i][6]) * 100  # Calcule le pourcentage du quiz
                data["percentCorrect"] = pourcentage
                taux_reussite_total += pourcentage
                nb_quiz_done += 1
            # Sinon, on met le pourcentage à 0, et on ne le compte pas dans le pourcentage total
            else:
                data["percentCorrect"] = 0

            archives.append(data)

        taux_reussite_total = taux_reussite_total / nb_quiz_done

        return nb_quiz, nb_question_total, taux_reussite_total, archives

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des archives des quiz :", error)
        return 0


# Renvoie un dictionnaire avec toutes les statistiques générales sur les diffusions de l'enseignant
# Param : - enseignant : l'id de l'enseignant (int)
#         - nb_jour : le nombre de jours à calculer par rapport à aujourd'hui (int)
# Return : un dico avec les statistiques générales de l'enseignant
#
#          /!\ chaque index des tableaux correspondent à la même donnée (pour le jour jours[i],
#          participantsSequences[i] ont participé à des séquences et participantsQuestions[i]
#          ont participé à des questions)
#       {
#         "totalQuizzes": 21     (-> nombre de quiz/diffusions effectués)
#         "totalQuestions": 10,  (-> nombre de questions posé)
#         "successRate": 79      (-> pourcentage de réussite total)
#         "participation": {     (-> nombre de participant à des questions et séquence pour chaque jour)
#                           "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                           "sequences": [10, 20, 0, 40, 50],
#                           "questions": [2, 0, 4, 50, 0]
#                          }
#         "success": {           (-> taux de réussite pour chaque quiz/diffusion)
#                     "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                     "quiz":[10, 25, 7, 19, 13, 55, 28]
#                    }
#         "archives": [          (-> les stats de toutes les quiz/diffusions effectués)
#                      { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#                      { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#                      {...}, ...
#                     ]
#       }
def getOverallStats(enseignant, nb_jour):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('../database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        temporal_stats = getTemporalStats(cursor, enseignant, nb_jour)
        globalstats_and_archives = getArchives(cursor, enseignant)

        # Ordonne les données dans un dico
        data = {
            "totalQuizzes": globalstats_and_archives[0],
            "totalQuestions": globalstats_and_archives[1],
            "successRate": globalstats_and_archives[2],
            "participation": temporal_stats[0],
            "success": temporal_stats[1],
            "archives": globalstats_and_archives[3]
        }

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False

