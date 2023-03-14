import sqlite3
from datetime import datetime, time


# Calcule le pourcentage de réussite total parmi toutes les diffusions d'un enseignant
# Param : - cursor : cursor de la BDD
#         - enseignant : id de l'enseignant (int)
# Return : le pourcentage de réussite totale (float)
def countTotalPourcentage(cursor, enseignant):
    try:
        # Compte le nombre de réponses et le nombre de bonnes réponses
        cursor.execute("SELECT COUNT(AR.id), SUM(AR.est_correcte) \
                        FROM ArchivesDiffusions AD \
                        JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                        JOIN ArchivesReponses AR ON AQ.id = AR.question \
                        WHERE enseignant = ?;", (enseignant,))
        result = cursor.fetchone()
        return (result[1]/result[0])*100  # Calcule le pourcentage et le renvoie

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du pourcentage :", error)
        return 0


# Compte le nombre de diffusions et le nombre de questions posées d'un enseignant
# Param : - cursor : cursor de la BDD
#         - enseignant : l'id de l'enseignant (int)
# Return : le nombre de diffusions et le nombre de questions posées (int)
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

        # Additionne les participants de toutes les diffusions
        nb_participant = 0
        for i in range(len(result)):
            nb_participant += result[i][0]

        if len(result) > 0:
            # Calcule la moyenne des participants du jour (nb participant total / nb diffusion)
            nb_participant = nb_participant/len(result)
        return nb_participant

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du nombre de participants :", error)
        return 0


# Renvoie un dictionnaire avec toutes les statistiques générales sur les diffusions de l'enseignant
# Param : - enseignant : l'id de l'enseignant (int)
#         - nb_jour : le nombre de jours à calculer par rapport à aujourd'hui (int)
# Return : un dico avec les statistiques générales de l'enseignant
#
#          /!\ chaque index des tableaux correspondent à la même donnée (pour le jour jours[i],
#          participantsSequences[i] ont participé à des séquences et participantsQuestions[i]
#          ont participé à des questions) /!\

#             {
#               "jours": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#               "participantsSequences": [10, 20, 0, 40, 50],
#               "participantsQuestions": [2, 0, 4, 50, 0],
#               "totalQuestions": 10,
#               "totalSequences": 21
#             }
def getOverallStats(enseignant, nb_jour):
    try:
        # Date du jour actuel (à minuit pile)
        jour = datetime.timestamp(datetime.combine(datetime.now(), time.min))

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")



        # Compte le nombre total de diffusions de question et de quiz (diffusion), puis ordonne les données
        total = countTotalQuiz(cursor, enseignant)
        data = {
            "jours": [],
            "participantsSequences": [],
            "participantsQuestions": [],
            "totalQuestions": total[1],
            "totalQuiz": total[0],
            "pourcentage": countTotalPourcentage(cursor, enseignant)
        }

        # Compte le nombre de participants aux diffusions pour les "nb_jour" dernier jour, et l'ajoute à data
        for i in range(nb_jour):

            data["jours"].append(jour)
            data["participantsQuestions"].append(countParticipantByDay(cursor, jour, 0, enseignant))
            data["participantsSequences"].append(countParticipantByDay(cursor, jour, 1, enseignant))

            jour -= 86400  # Jour précédent

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False
