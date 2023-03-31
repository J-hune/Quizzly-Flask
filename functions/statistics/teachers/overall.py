import sqlite3
from datetime import datetime, time


# Récupère la moyenne du taux de réussite et la moyenne du nombre de participants pour chaque nb_jour derniers jours
# Pour les participants : requête qui récupère le nb de participants de chaque quiz, on regroupe ensuite par jour
#                         pour faire une moyenne
# Pour le taux de réussite : requête qui récupère le taux de réussite de chaque question, on fait la moyenne de
#                            de toutes les questions non ouvertes du quiz, puis on fait la moyenne des moyennes de tous
#                            les quiz du jours
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
#                    "days": [1646937600, 1647283200],
#                    "quiz":[10, 25]
#                   }
#
#           /!\ chaque index des tableaux correspondent à la même donnée (pour le jour participation["days"][i],
#               participation["sequences"][i] ont participé à des séquences et participation["questions"][i]
#               ont participé à des questions)
#
#           /!\ Spécifications stats :
#                 - quand il y a une question ouverte, on compte ses participants
#                   mais pas son taux de réussite (puisqu'il n'y a pas de bonne ou mauvaise réponse)
#                 - pour le nombre participants, on affiche tous les jours même quand il n'y a pas eu de quiz diffusé
#                 - pour le taux de réussite, on affiche uniquement les jours où un quiz a été diffusé
#
def getTemporalStats(cursor, enseignant, nb_jour):
    try:
        jour = datetime.timestamp(datetime.combine(datetime.now(), time.min))  # Date du jour actuel (à minuit pile)
        jour -= (86400 * (nb_jour-1))  # Jour il y a nb_jour

        # Récupère les données du nombre de participants de chaque quiz pour les derniers nb_jour jours
        # Récupère l'id du quiz, la date du quiz, le mode du quiz et le nombre de participants total du quiz
        #                                                    nbParticipant
        cursor.execute("SELECT AD.id, AD.date, AD.mode, COUNT(DISTINCT AR.etudiant) \
                                                FROM ArchivesDiffusions AD \
                                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                                WHERE AD.date >= ? \
                                                AND AD.enseignant = ? \
                                                GROUP BY AD.id \
                                                ORDER BY AD.date;", (jour, enseignant))
        result_participant = cursor.fetchall()

        # Récupère les données du taux de succès de chaque question pour les derniers nb_jour jours
        # Récupère la date du quiz, le type de la question et le taux de réussite du quiz
        #                                        nbRéponse      nbBonneRéponse
        cursor.execute("SELECT AD.id, AQ.type, COUNT(AR.id), SUM(AR.est_correcte) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.date >= ? \
                                AND AD.enseignant = ? \
                                GROUP BY AQ.id \
                                ORDER BY AD.date;", (jour, enseignant))
        result_success = cursor.fetchall()

        nb_quiz = len(result_participant)  # Le nombre de quiz diffusés durant les nb_jour derniers jours
        nb_question = len(result_success)  # Le nombre de questions posées durant les nb_jour derniers jours
        participation = {"days": [], "sequences": [], "questions": []}
        success = {"days": [], "quiz": []}

        k = 0  # Compteur pour avancer dans result_participant
        m = 0  # Compteur pour avancer dans result_success

        # Pour les nb_jour derniers jours
        for i in range(nb_jour):

            nb_sequence_jour = 0  # Nombre de quiz ce jour
            nb_question_jour = 0  # Nombre de questions diffusées ce jour
            nb_participant_sequence = 0  # Nombre de participants à des séquences ce jour
            nb_participant_question = 0  # Nombre de participants à des questions ce jour
            success_rate = 0  # Taux de réussite du jour
            nb_quiz_not_opened = 0  # Nombre de quiz avec au moins une question non ouverte

            # Pour tous les quiz du jour
            while k < nb_quiz and result_participant[k][1] < jour + 86400:

                nb_question_quiz = 0  # Nombre de questions à ce quiz
                success_rate_quiz = 0  # Taux de succès du quiz

                # Si le quiz est une question
                if result_participant[k][2] == 0:
                    nb_participant_question += result_participant[k][3]
                    nb_question_jour += 1
                # Sinon c'est une séquence
                else:
                    nb_participant_sequence += result_participant[k][3]
                    nb_sequence_jour += 1

                # Pour toutes les questions du quiz
                while m < nb_question and result_success[m][0] == result_participant[k][0]:
                    # Si ce n'est pas une question ouverte
                    if result_success[m][1] != 2:
                        success_rate_quiz += result_success[m][3] / result_success[m][2]  # Moyenne de la question
                        nb_question_quiz += 1
                    m += 1

                # S'il y a eu au moins une question non ouverte au quiz
                if nb_question_quiz > 0:
                    success_rate += success_rate_quiz / nb_question_quiz  # Moyenne du quiz
                    nb_quiz_not_opened += 1

                k += 1

            participation["days"].append(jour)
            # S'il y a eu une diffusion de séquence ce jour-là, on fait une moyenne des participants
            if nb_sequence_jour > 0:
                participation["sequences"].append(nb_participant_sequence / nb_sequence_jour)
            else:
                participation["sequences"].append(0)
            # S'il y a eu une diffusion de question ce jour-là, on fait une moyenne des participants
            if nb_question_jour > 0:
                participation["questions"].append(nb_participant_question / nb_question_jour)
            else:
                participation["questions"].append(0)
            # Si au moins un quiz avec une question non ouverte
            if nb_quiz_not_opened > 0:
                success["days"].append(jour)
                success["quiz"].append((success_rate / nb_quiz_not_opened) * 100)  # Moyenne du jour
            # Sinon, on met 0 pour les participants (et on n'enregistre pas le taux de succès du jour)

            jour += 86400  # Jour suivant

        return participation, success

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques temporelles :", error)
        return 0


# Récupère toutes les réponses à une question ouverte
# Param : - cursor : cursor BDD
#         - id_question : id de l'archive de la question (int)
# Return : les réponses à la question ouverte (tab de string)
#           ['Python', 'pithon', 'pyton', 'monty python']
def getReponsesQuestionOuverte(cursor, id_question):
    try:
        # Requêtes pour récupérer toutes les réponses associées à la question grâce à l'id de celle-ci
        cursor.execute("SELECT reponse FROM ArchivesReponses WHERE question = ?;", (id_question,))
        result = cursor.fetchall()

        # On range les réponses dans un tableau
        reponses = []
        for i in range(len(result)):
            reponses.append(result[i][0])

        return reponses

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des réponses de la question ouverte :", error)
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
#
#           /!\ Spécifications stats :
#                   - on récupère les diffusions vides (sans réponse)
#                   - si une diffusion est vide, 0 participants et 0% (et on ne compte pas dans le pourcentage total)
#                   - si une séquence est diffusée avec que des questions ouvertes, on envoie -1 (le front s'en charge)
#                   - si une séquence est diffusée avec une question ouverte, on ne la compte pas
#                   - si une question est diffusée avec une question ouverte, on envoie le nb de participant et
#                     toutes les réponses (le front triera les réponses et affichera la plus répondue)
#
def getArchives(cursor, enseignant):
    try:
        # LEFT JOIN pour avoir également les diffusions vides (qui n'ont donc pas de liens avec ArchivesReponses)
        # Récupère les données du nombre de participants de chaque quiz pour les derniers nb_jour jours
        # Récupère l'id du quiz, la date du quiz, le mode du quiz et le nombre de participants total du quiz
        #                                                                       nbParticipant
        cursor.execute("SELECT AD.id, AD.date, AD.mode, AD.titre, AD.code, COUNT(DISTINCT AR.etudiant) \
                                                        FROM ArchivesDiffusions AD \
                                                        LEFT JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                                        LEFT JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                                        AND AD.enseignant = ? \
                                                        GROUP BY AD.id \
                                                        ORDER BY AD.date DESC;", (enseignant,))
        result_quiz = cursor.fetchall()

        # Récupère les données du taux de succès de chaque question pour les derniers nb_jour jours
        # Récupère l'id de la question, le numéro de sa diffusion, le type et le taux de réussite de la question
        #                                                     nbRéponse      nbBonneRéponse
        cursor.execute("SELECT AQ.id, AQ.diffusion, AQ.type, COUNT(AR.id), SUM(AR.est_correcte) \
                                        FROM ArchivesDiffusions AD \
                                        LEFT JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                        LEFT JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                        AND AD.enseignant = ? \
                                        GROUP BY AQ.id, AD.id \
                                        ORDER BY AD.date DESC;", (enseignant,))
        result_question = cursor.fetchall()

        print(result_question)

        nb_quiz = len(result_quiz)  # Le nombre de diffusions total
        nb_quiz_done = 0  # Le nombre de diffusions réellement effectué (au moins une question non ouverte)
        nb_question_total = len(result_question)
        taux_reussite_total = 0  # Le pourcentage de réussite total
        archives = []  # Les archives des diffusions

        k = 0
        # Pour tous les quiz
        for i in range(nb_quiz):

            nb_question_quiz = 0  # Nombre de questions répondues à ce quiz
            success_rate_quiz = 0  # Taux de succès du quiz
            nb_question_ouverte = 0  # Nombre de questions ouvertes dans le quiz

            data = {"id": result_quiz[i][0],
                    "title": result_quiz[i][3],
                    "code": result_quiz[i][4],
                    "date": result_quiz[i][1],
                    "mode": result_quiz[i][2],
                    "participantCount": result_quiz[i][5]
                    }

            # Pour toutes les questions du quiz
            while k < nb_question_total and result_quiz[i][0] == result_question[k][1]:
                # Si la question a au moins une réponse (non vide)
                if result_question[k][4] is not None:
                    # Si c'est une question ouverte
                    if result_question[k][2] == 2:
                        nb_question_ouverte += 1
                    # Sinon c'est une question multiple ou numérique, on calcule alors le taux de réussite
                    else:
                        success_rate_quiz += result_question[k][4] / result_question[k][3]  # Moyenne de la question
                    nb_question_quiz += 1
                k += 1

            # C'est une diffusion normale (au moins une question non ouverte répondue)
            if nb_question_quiz - nb_question_ouverte > 0:
                pourcentage = (success_rate_quiz / (nb_question_quiz - nb_question_ouverte)) * 100  # Moyenne du quiz
                data["percentCorrect"] = pourcentage
                taux_reussite_total += pourcentage
                nb_quiz_done += 1
            # C'est une question diffusée avec une question ouverte
            elif result_quiz[i][2] == 0 and nb_question_ouverte == 1:
                data["reponsesOuvertes"] = getReponsesQuestionOuverte(cursor, result_question[k-1][0])
            # C'est une séquence diffusée avec que des questions ouvertes
            elif result_quiz[i][2] == 1 and 0 < nb_question_quiz == nb_question_ouverte:
                data["reponsesOuvertes"] = -1
            # C'est une diffusion vide (sans réponse)
            else:
                data["percentCorrect"] = 0.

            archives.append(data)

        # S'il a au moins fait un quiz normal (au moins une question non ouverte répondue)
        if nb_quiz_done > 0:
            taux_reussite_total = taux_reussite_total / nb_quiz_done

        return nb_quiz, nb_question_total, taux_reussite_total, archives

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des archives des quiz :", error)
        return 0


# Renvoie un dictionnaire avec toutes les statistiques générales sur les diffusions de l'enseignant
# Param : - enseignant : l'id de l'enseignant (int)
#         - nb_jour : le nombre de jours à calculer par rapport à aujourd'hui (int)
# Return : un dico avec les statistiques générales de l'enseignant
#               {
#                 "totalQuizzes": 21     (-> nombre de quiz/diffusions effectués)
#                 "totalQuestions": 10,  (-> nombre de questions posé)
#                 "successRate": 79      (-> pourcentage de réussite total)
#                 "participation": {     (-> nombre de participant à des questions et séquence pour chaque jour)
#                                   "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                                   "sequences": [10, 20, 0, 40, 50],
#                                   "questions": [2, 0, 4, 50, 0]
#                                  }
#                 "success": {           (-> taux de réussite pour chaque quiz/diffusion)
#                             "days": [1646937600, 1647024000, 1647110400, 1647196800, 1647283200],
#                             "quiz":[10, 25, 7, 19, 13, 55, 28]
#                            }
#                 "archives": [          (-> les stats de toutes les quiz/diffusions effectués)
#                              { "archiveId": 1, "title": "Séquence algorithmie", "id": "Fxa4t3xr", "date": 1678667302, "participantCount": 15, "percentCorrect": 42 },
#                              { "archiveId": 2, "title": "Les questions de sciences", "id": "Gxa4t3xr", "date": 1678667402, "participantCount": 15, "percentCorrect": 32},
#                              {...}, ...
#                             ]
#               }
#           /!\ chaque index des tableaux correspondent à la même donnée (pour le jour participation["days"][i],
#               participation["sequences"][i] ont participé à des séquences et participation["questions"][i]
#               ont participé à des questions)
#
def getOverallStats(enseignant, nb_jour):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
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
