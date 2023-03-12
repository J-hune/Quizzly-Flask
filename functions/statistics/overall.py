import sqlite3
from datetime import datetime, time


# Calcule le nombre de participants par jour aux diffusions d'un enseignant
# Param : - enseignant : l'id de l'enseignant (int)
#         - nb_jour : le nombre de jours souhaité (int)
# Return : le nombre de participants aux questions et séquences chaque jour,
#          chaque index de chaque tableau correspondent à la même donnée (dico de tab)
#               {
#                 "jours": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                 "participantsSequences": [10, 20, 0, 40, 50],
#                 "participantsQuestions": [2, 0, 4, 50, 0]
#               }
def overallStatistics(enseignant, nb_jour=10):
    try:
        # Date du jour actuel (à minuit pile)
        jour = datetime.timestamp(datetime.combine(datetime.now(), time.min))

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        overall = {
            "jours": [],
            "participantsSequences": [],
            "participantsQuestions": []
        }

        for i in range(nb_jour):

            overall["jours"].append(jour)
            overall["participantsSequences"].append(countParticipantByDay(cursor, jour, 1, enseignant))
            overall["participantsQuestions"].append(countParticipantByDay(cursor, jour, 0, enseignant))

            jour -= 86400  # Jour précédent

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return overall

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False


# Compte le nombre de participants à une diffusion pour un jour et un mode donné
# Param : - cursor : cursor BDD
#         - jour : la date du jour en timestamp (int)
#         - mode_diffusion : le mode de diffusion choisi, 0 pour une question, 1 pour une séquence
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

        # Calcule la moyenne des participants du jour (nb participant total / nb diffusion)

        if len(result) > 0:
            nb_participant = nb_participant/len(result)
        return nb_participant

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du nombre de participants :", error)
        return 0



