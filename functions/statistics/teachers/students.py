import sqlite3
from datetime import datetime, time
from functions.students import getStudent


# Récupère la moyenne du taux de réussite à des questions et à des séquences pour chaque nb_jour derniers jours
# Pour le taux de réussite, on affiche uniquement les jours où un quiz a été diffusé
# Param : - cursor : cursor de la BDD
#         - etudiant : id de l'étudiant (int)
#         - enseignant : id de l'enseignant (int)
#         - nb_jour : nombre de jours à calculer (int)
# Return : les pourcentages de réussite au cours du temps (dico de tab)
#                   {
#                    "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                    "sequences":[10, 25, 7, 19, 13, 0, 28]
#                    "questions":[78, 0, 0, 19, 0, 55, 44]
#                   }
#
#           /!\ chaque index des tableaux correspondent à la même donnée
#
def getTemporalStats(cursor, etudiant, enseignant, nb_jour):
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
                                AND AR.etudiant = ? \
                                GROUP BY AD.id \
                                ORDER BY AD.date;", (jour, enseignant, etudiant))
        result = cursor.fetchall()

        nb_quiz = len(result)
        success = {"days": [], "sequences": [], "questions": []}

        k = 0
        # Pour les nb_jour derniers jours
        for i in range(nb_jour):

            nb_sequence = 0  # Nombre de séquences ce jour
            nb_question = 0  # Nombre de questions ce jour
            success_rate_sequence = 0  # Taux de succès à des séquences ce jour
            success_rate_question = 0  # Taux de succès à des questions ce jour

            # Pour tous les quiz du jour
            while k < nb_quiz and result[k][0] < jour + 86400:
                # Si c'est une question
                if result[k][1] == 0:
                    success_rate_question += result[k][4] / result[k][3]
                    nb_question += 1
                # Sinon c'est une séquence
                else:
                    success_rate_sequence += result[k][4] / result[k][3]
                    nb_sequence += 1
                k += 1

            # S'il y a eu un quiz ce jour-là
            if nb_sequence + nb_question > 0:
                success["days"].append(jour)
                # S'il y a eu une séquence, on fait la moyenne
                if nb_sequence > 0:
                    success["sequences"].append((success_rate_sequence / nb_sequence) * 100)
                # Sinon, on met le taux de succès à 0%
                else:
                    success["sequences"].append(0)
                # S'il y a eu une question, on fait la moyenne
                if nb_question > 0:
                    success["questions"].append((success_rate_question / nb_question) * 100)
                # Sinon, on met le taux de succès à 0%
                else:
                    success["questions"].append(0)

            jour += 86400  # Jour suivant

        return success

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques temporelles de l'étudiant :", error)
        return 0


# Récupère toutes les archives des anciennes diffusions et ordonnes les données en statistiques
# Param : - cursor : cursor de la BDD
#         - etudiant : id de l'étudiant (int)
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
def getArchives(cursor, etudiant, enseignant):
    try:
        # L'id, le titre, le code, la date, le mode, le nombre de participants, le taux de réussite de chaque quiz
        #                                                                       nbParticipant             nbRéponse     #nbBonneRéponse       nbQuestion
        cursor.execute("SELECT AD.id, AD.titre, AD.code, AD.date, AD.mode, COUNT(DISTINCT AR.etudiant), COUNT(AR.id), SUM(AR.est_correcte), COUNT(DISTINCT AQ.id) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.enseignant = ? \
                                AND AR.etudiant = ? \
                                GROUP BY AD.id \
                                ORDER BY AD.date DESC;", (enseignant, etudiant))
        result = cursor.fetchall()

        nb_quiz = len(result)  # Le nombre de diffusions total
        nb_question_total = 0  # Le nombre de questions posées
        taux_reussite_total = 0  # Le pourcentage de réussite total
        archives = []  # Les archives des diffusions

        # S'il a déjà participé à au moins un quiz (pour éviter la division par 0)
        if nb_quiz > 0:
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
                # Sinon, on met le pourcentage à 0, et on ne le compte pas dans le pourcentage total
                else:
                    data["percentCorrect"] = 0

                archives.append(data)

            taux_reussite_total = taux_reussite_total / nb_quiz

        return nb_quiz, nb_question_total, taux_reussite_total, archives

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des archives des quiz de l'étudiant:", error)
        return 0


# Renvoie un dictionnaire avec toutes les statistiques générales sur l'étudiant de l'enseignant
# Param : - etudiant : id de l'étudiant (int)
#         - enseignant : id de l'enseignant (int)
#         - nb_jour : le nombre de jours à calculer par rapport à aujourd'hui pour les stats temporelles (int)
# Return : un dico avec les statistiques générales de l'étudiant
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
def getStatsByStudent(etudiant, enseignant, nb_jour):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        globalstats_and_archives = getArchives(cursor, etudiant, enseignant)

        # Ordonne les données dans un dico
        data = {
            "etudiant": getStudent(etudiant),
            "totalQuizzes": globalstats_and_archives[0],
            "totalQuestions": globalstats_and_archives[1],
            "successRate": globalstats_and_archives[2],
            "success": getTemporalStats(cursor, etudiant, enseignant, nb_jour),
            "archives": globalstats_and_archives[3]
        }

        data["etudiant"]["id"] = etudiant

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques de l'étudiant :", error)
        return False

