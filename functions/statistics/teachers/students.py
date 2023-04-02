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

        # Récupère la date, le mode, le taux de réussite pour tous les quiz après le jour
        #                                         nbRéponse      nbBonneRéponse
        cursor.execute("SELECT AD.date, AD.mode, COUNT(AR.id), SUM(AR.est_correcte) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.date >= ? \
                                AND AD.enseignant = ? \
                                AND AR.etudiant = ? \
                                AND AQ.type != 2 \
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
                    success_rate_question += result[k][3] / result[k][2]
                    nb_question += 1
                # Sinon c'est une séquence
                else:
                    success_rate_sequence += result[k][3] / result[k][2]
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
#
#           /!\ Spécifications stats :
#                   - si une séquence est diffusée avec que des questions ouvertes, on envoie -1 (le front s'en charge)
#                   - si une séquence est diffusée avec une question ouverte, on ne la compte pas
#                   - si une question est diffusée avec une question ouverte, on envoie le nb de participant et
#                     la réponse de l'élève
def getArchives(cursor, etudiant, enseignant):
    try:
        # L'id, le titre, le code, la date, le mode, le nombre de participants de chaque quiz
        #                                                                      nbParticipant
        cursor.execute("SELECT AD.id, AD.titre, AD.code, AD.date, AD.mode, COUNT(DISTINCT AR.etudiant) \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.id IN (SELECT DISTINCT AD2.id \
                                                FROM ArchivesDiffusions AD2 \
                                                JOIN ArchivesQuestions AQ2 ON AD2.id = AQ2.diffusion \
                                                JOIN ArchivesReponses AR2 ON AQ2.id = AR2.question \
                                                WHERE AD.enseignant = ? \
                                                AND AR2.etudiant = ?) \
								GROUP BY AD.id \
                                ORDER BY AD.date DESC;", (enseignant, etudiant))
        result_quiz = cursor.fetchall()

        # L'id, l'id de diffusion, le type, la réussite et la réponse de chaque question
        cursor.execute("SELECT AQ.id, AQ.diffusion, AQ.type, AR.est_correcte, AR.reponse \
                                FROM ArchivesDiffusions AD \
                                JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                WHERE AD.enseignant = ? \
								AND AR.etudiant = ? \
								GROUP BY AQ.id, AD.id \
                                ORDER BY AD.date DESC;", (enseignant, etudiant))
        result_question = cursor.fetchall()

        nb_quiz = len(result_quiz)  # Le nombre total de diffusions
        nb_quiz_done = 0  # Le nombre de diffusions réellement effectué (au moins une question non ouverte)
        nb_question = len(result_question)  # Le nombre total de questions posées
        taux_reussite_total = 0  # Le pourcentage de réussite total
        archives = []  # Les archives des diffusions

        k = 0
        # Ordonne les données dans un tableau de dico pour chaque quiz
        for i in range(nb_quiz):

            taux_reussite_quiz = 0  # Taux de succès du quiz
            nb_question_quiz = 0  # Nombre de questions dans le quiz
            nb_question_ouverte = 0  # Nombre de questions ouvertes dans le quiz

            data = {"id": result_quiz[i][0],
                    "title": result_quiz[i][1],
                    "code": result_quiz[i][2],
                    "date": result_quiz[i][3],
                    "mode": result_quiz[i][4],
                    "participantCount": result_quiz[i][5]
                    }

            # Pour toutes les questions du quiz
            while k < nb_question and result_quiz[i][0] == result_question[k][1]:
                # Si c'est une question ouverte
                if result_question[k][2] == 2:
                    nb_question_ouverte += 1
                # Sinon c'est une question multiple ou numérique, on calcule alors le taux de réussite
                else:
                    taux_reussite_quiz += result_question[k][3]
                nb_question_quiz += 1
                k += 1

            # C'est une diffusion normale (au moins une question non ouverte répondue)
            if nb_question_quiz - nb_question_ouverte > 0:
                pourcentage = (taux_reussite_quiz / (nb_question_quiz - nb_question_ouverte)) * 100  # Moyenne du quiz
                data["percentCorrect"] = pourcentage
                taux_reussite_total += pourcentage
                nb_quiz_done += 1
            # C'est une question diffusée avec une question ouverte
            elif result_quiz[i][4] == 0 and nb_question_ouverte == 1:
                data["reponsesOuvertes"] = result_question[k-1][4]
            # C'est une séquence diffusée avec que des questions ouvertes
            elif result_quiz[i][4] == 1 and 0 < nb_question_quiz == nb_question_ouverte:
                data["reponsesOuvertes"] = -1

            archives.append(data)

        # S'il a déjà participé à un quiz normal (au moins une question non ouverte répondue)
        if nb_quiz_done > 0:
            taux_reussite_total = taux_reussite_total / nb_quiz_done

        return nb_quiz, nb_question, taux_reussite_total, archives

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des archives des quiz de l'étudiant:", error)
        return 0


# Renvoie un dictionnaire avec toutes les statistiques générales sur l'étudiant de l'enseignant
# Param : - etudiant : id de l'étudiant (int)
#         - enseignant : id de l'enseignant (int)
#         - nb_jour : le nombre de jours à calculer par rapport à aujourd'hui pour les stats temporelles (int)
# Return : un dico avec les statistiques générales de l'étudiant (ou -1 si échec requête, ou 0 si étudiant n'existe pas)
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
    if getStudent(etudiant):
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
            return -1
    else:
        return 0
