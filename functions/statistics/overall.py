import sqlite3
from datetime import datetime, time


# Compte le nombre de diffusions et le nombre de questions posées d'un enseignant
# Param : - cursor : cursor de la BDD
#         - enseignant : l'id de l'enseignant (int)
# Return : le nombre de diffusions et le nombre de questions posées (tuple d'int)
def countTotalQuiz(cursor, enseignant):
    try:
        # Compte le nombre diffusion d'un enseignant selon le mode
        #                         nbQuiz                 nbQuestion
        cursor.execute("SELECT COUNT(DISTINCT AD.id), COUNT(DISTINCT AQ.id) \
                            FROM ArchivesDiffusions AD \
                            JOIN ArchivesQuestions AQ \
                            WHERE enseignant = ?;", (enseignant,))
        result = cursor.fetchone()
        return result

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du nombre de diffusion :", error)
        return 0


# Calcule le pourcentage de réussite total (moyenne) parmi toutes les diffusions d'un enseignant
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
# Return : le pourcentage de réussite totale (float)
def countTotalPourcentage(cursor, enseignant):
    try:
        # Compte le nombre de réponses et le nombre de bonnes réponses
        #                        nbRéponse      nbBonneRéponse
        cursor.execute("SELECT COUNT(AR.id), SUM(AR.est_correcte) \
                        FROM ArchivesDiffusions AD \
                        JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                        JOIN ArchivesReponses AR ON AQ.id = AR.question \
                        WHERE enseignant = ? \
                        GROUP BY AD.id;", (enseignant,))
        result = cursor.fetchall()

        nb_quiz = len(result)
        pourcentage = 0
        # Si au moins une diffusion (sinon le pourcentage total reste à 0%)
        if nb_quiz > 0:
            # Pour chaque diffusion
            for i in range(nb_quiz):
                pourcentage += result[i][1] / result[i][0]  # Additionne le pourcentage de toutes les diffusions

            pourcentage = (pourcentage / nb_quiz) * 100  # Calcule la moyenne de toutes les diffusions

        return pourcentage

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du pourcentage :", error)
        return 0


# Compte le nombre de participants à une diffusion pour un jour et un mode donné
# Param : - cursor : cursor BDD
#         - jour : la date du jour en timestamp (int)
#         - mode_diffusion : le mode de diffusion choisi, 0 pour une question, 1 pour une séquence (int)
# Return : le nombre de participants à une diffusion de question (si plus d'une diffusion, moyenne de ces diffusions)
def countParticipantByDay(cursor, jour, mode_diffusion, enseignant):
    try:
        # Compte le nombre de participants pour chaque diffusion du jour (ne compte pas les diffusions vides)
        cursor.execute("SELECT COUNT(DISTINCT AR.etudiant) \
                        FROM ArchivesDiffusions AD \
                        JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                        JOIN ArchivesReponses AR ON AQ.id = AR.question \
                        WHERE AD.date >= ? AND AD.date <= ? \
                        AND AD.mode = ? \
                        AND AD.enseignant = ? \
                        GROUP BY AD.id;",
                       (jour, jour + 86399.999999, mode_diffusion, enseignant))  # le début du jour (00:00) et la fin du jour (23:59)
        result = cursor.fetchall()

        nb_quiz = len(result)
        nb_participant = 0
        if nb_quiz > 0:
            # Additionne les participants de toutes les diffusions du jour
            for i in range(nb_quiz):
                nb_participant += result[i][0]

            # Calcule la moyenne des participants du jour (nb participant total / nb diffusion)
            nb_participant = nb_participant / nb_quiz

        return nb_participant

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du nombre de participants :", error)
        return 0


# Récupère le taux de réussite pour chaque quiz
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
# Return : un dico de tableau avec le taux de réussite
def getSuccessByDay(cursor, jour, enseignant):
    try:
        # Compte le nombre de réponses et le nombre de bonnes réponses
        #                        nbRéponse      nbBonneRéponse
        cursor.execute("SELECT COUNT(AR.id), SUM(AR.est_correcte) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.date >= ? AND AD.date <= ? \
                                AND AD.enseignant = ? \
                                GROUP BY AD.id;", (jour, jour + 86399.999999, enseignant))
        result = cursor.fetchall()

        nb_quiz = len(result)
        taux_reussite = 0
        # Si au moins une diffusion (sinon taux de réussite reste à 0)
        if nb_quiz > 0:
            # Additionne les taux de réussite de toutes les diffusions du jour
            for i in range(nb_quiz):
                taux_reussite += result[i][1]/result[i][0]

            taux_reussite = (taux_reussite * 100) / nb_quiz  # Calcule la moyenne du taux de réussite du jour

        return taux_reussite

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du taux de réussite des quiz :", error)
        return 0


# Récupère toutes les archives des anciennes diffusions (quiz) d'un enseignant
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
# Return : un tableau de dico avec les archives des quiz
#           [
#            { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#            { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#            {...}, ...
#           ]
def getArchives(cursor, enseignant):
    try:
        # Récupère l'id du quizz, son titre, son code, sa date, son mode, le nombre de participant et le pourcentage de bonne réponse
        #                                                                       nbParticipant             nbRéponse        nbBonneRéponse
        cursor.execute("SELECT AD.id, AD.titre, AD.code, AD.date, AD.mode, COUNT(DISTINCT AR.etudiant), COUNT(AR.id), SUM(AR.est_correcte) \
                        FROM ArchivesDiffusions AD \
                        JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                        JOIN ArchivesReponses AR ON AQ.id = AR.question \
                        WHERE enseignant = ? \
                        GROUP BY AD.id \
                        ORDER BY AD.date DESC;",(enseignant, ))
        result = cursor.fetchall()

        # Ordonne les données dans un tableau de dico pour chaque quiz
        archives = []
        for i in range(len(result)):
            data = {"archiveId": result[i][0],
                    "title": result[i][1],
                    "id": result[i][2],
                    "date": result[i][3],
                    "mode": result[i][4],
                    "participantCount": result[i][5],
                    "percentCorrect": (result[i][7] / result[i][6]) * 100
                    }
            archives.append(data)

        return archives

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
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Compte le nombre total de diffusions de question et de quiz (diffusion), puis ordonne les données
        total = countTotalQuiz(cursor, enseignant)
        data = {
            "totalQuizzes": total[0],
            "totalQuestions": total[1],
            "successRate": countTotalPourcentage(cursor, enseignant),
            "participation": {"days": [], "sequences": [], "questions": []},
            "success": {"days": [], "quiz": []},
            "archives": getArchives(cursor, enseignant)
        }

        # Date du jour actuel (à minuit pile)
        jour = datetime.timestamp(datetime.combine(datetime.now(), time.min))

        # Pour tous les "nb_jour" dernier jour, on calcule le taux de réussite et le nombre de participants
        for i in range(nb_jour):

            data["participation"]["days"].append(jour)

            success = getSuccessByDay(cursor, jour, enseignant)
            # S'il y a au moins une diffusion ce jour-là
            if success:
                # On récupère la moyenne du taux de succès du jour
                data["success"]["days"].append(jour)
                data["success"]["quiz"].append(success)

                # On récupère la moyenne du nombre de participants du jour
                data["participation"]["questions"].append(countParticipantByDay(cursor, jour, 0, enseignant))
                data["participation"]["sequences"].append(countParticipantByDay(cursor, jour, 1, enseignant))

            # Sinon, on ajoute directement 0 pour la participation (on n'ajoute pas le taux de réussite si aucun quiz)
            else:
                data["participation"]["questions"].append(0)
                data["participation"]["sequences"].append(0)

            jour -= 86400  # Jour précédent

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False


print(getOverallStats(5,1))
