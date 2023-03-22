import sqlite3
from functions.questions import getQuestion


# Permet d'enregistrer en base de données toutes les infos concernant une diffusion
# Param : Un dico qui contient toutes les infos de la sequence :
# {
#      'name': 'GAHisbh5',
#      'titre' : titre de la sequence ou enonce de la question,
#      'enseignant': 'GEBXTRQbmhZOTXqrAAAF',
#      'id_enseignant' : 12,
#      'mode': 'sequence', (ou 'question')
#      'etudiants': [{'id': 22100000, 'nom': 'donov zst'}],
#      'questions': [],
#      'copieQuestions' : [],
#      'derQuestionTraitee': objet de type question,
#      'stopReponses': False,
#      'reponsesEtudiant': [
#          {'id': 22100000, 'question': 6, 'answer': 20,'date':1678558000},
#          {'id': 22100000, 'question': 18, 'answer': [33],'date':1678558989}
#      ],
#      'date':1678558957
# }
def saveDiffusions(sequence):

    # Appel a la fonction pour creer l'archive de la diffusion et récupère l'id de la diffusion
    diffusion_id = saveArchivesDiffusion(sequence["date"], sequence["mode"], sequence["id_enseignant"],
                                         sequence["titre"], sequence["name"])
    if not diffusion_id :
        return False

    # Récupère les id des questions utilisées lors de la diffusion
    tableau_questions = sequence["copieQuestions"]

    # Tableau qui contient des dictionnaires de questions sous cette forme {'id': 6, 'numerique': 206.0} (avec que les bonnes réponses pour un QCM)
    reponse_juste_question = []
    # Insère les données des questions dans la table d'archive des questions
    for i in range(len(tableau_questions)):
        # Appel a une fonction pour récupérer toutes les données de la question
        data_question = getQuestion(tableau_questions[i], sequence["id_enseignant"])

        # Enregistrer en base de donnée les données de la question
        saveArchivesQuestions(data_question, diffusion_id)

        # Extrait juste les bonnes réponses et l'id de la question
        if data_question["type"]==0:
            reponse_juste_question.append({
                "id": data_question["id"],
                "reponse": [r['id'] for r in data_question['reponses'] if r['reponseJuste']]
            })
        else:
            reponse_juste_question.append({
                "id": data_question["id"],
                "numerique": float(data_question["numerique"])
            })

    # Récupère les infos et réponses des étudiants qui ont participé à la diffusion, et ajoute s'il a correcte ou pas a la question
    tableau_reponses_etudiants = addEstCorrecte(sequence["reponsesEtudiant"],reponse_juste_question)

    # Insère les données des réponses dans la table d'archive des réponses
    for i in range(len(tableau_reponses_etudiants)):
        archivesReponses(tableau_reponses_etudiants[i], diffusion_id)


# Insère les infos (date, mode, enseignant) concernant la diffusion en BDD
# Param : - date : la date de la diffusion (int)
#         - mode : le mode de diffusion sequence (0) ou question (1) (int)
#         - enseignant : l'id de l'enseignant qui a lancé la diffusion
# Return : Si ajout de la diffusion en BDD :
#             l'id de la diffusion qui vient d'être ajouté (int)
#          Sinon :
#             False en cas d'échec
def saveArchivesDiffusion(date, mode, enseignant, titre, code):
    try:
        # Change en booleen le mode pour correspondre à la BDD
        if mode == "question":
            mode = 0
        elif mode == "sequence":
            mode = 1

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Insertion de la diffusion dans la table
        cursor.execute("INSERT INTO ArchivesDiffusions (date, mode, enseignant, titre, code) VALUES (?, ?, ?, ?, ?);",
                       (date, mode, enseignant, titre, code))
        conn.commit()

        # Récupère l'id de la dernière diffusion insérée (avec l'auto-increment)
        diffusion_id = cursor.lastrowid

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Renvoie l'id de la dernière diffusion insérée
        return diffusion_id

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion de la diffusion : ", error)
        return False


# Ajoute la question dans les archives des questions
# Param : - question : dictionnaire issu de la fonction getQuestion (dico)
#         - id_diffusion : id de la diffusion lier à la question (int)
# Return : Si ajout de la question :
#               True
#           Sinon :
#               False en cas d'échec
def saveArchivesQuestions(data_question, id_diffusion):
    if not data_question:
        return False

    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Insertion de l'archive de la question dans la table
        cursor.execute("INSERT INTO ArchivesQuestions (enonce, type, numerique, question, diffusion) VALUES (?, ?, ?, ?, ?);",
                       (data_question["enonce"], data_question["type"], data_question["numerique"], data_question["id"], id_diffusion))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion des questions de la diffusion : ", error)
        return False


# Récupère les données pour ajouter la réponse de l'étudiant dans les archives des réponses
# Param : - un dico qui contient la réponse de l'étudiant sous cette forme :
#                   {
#                       'id': 22100000,
#                       'question': 6,
#                       'answer': 20,
#                       'date':1678558000,
#                       'est_correcte' : 0
#                   }
#         - l'id de la diffusion lier à la réponse (int)
# Return : Si ajout de la réponse :
#               True
#           Sinon :
#               False en cas d'échec
def archivesReponses(reponse_etudiant, id_diffusion):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Requêtes pour récupérer l'id de la question des archives et son type
        id_question_archive = cursor.execute("SELECT id,type FROM ArchivesQuestions WHERE question = ? AND diffusion = ?",
                                             (reponse_etudiant["question"], id_diffusion))
        id_question_archive = id_question_archive.fetchone()

        # Insertion des données dans des variables pour une meilleure lisibilité
        id_question = id_question_archive[0]
        type_question = id_question_archive[1]

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Si on a une question numérique, on met la réponse de l'étudiant dans la base de données
        if type_question == 1:
            save = saveArchivesReponse(reponse_etudiant["date"], reponse_etudiant["est_correcte"], reponse_etudiant["answer"],
                                reponse_etudiant["id"], id_question)

        # Sinon, on a une question QCM, on met donc le nombre de réponses qu'a donné l'étudiant à cette question
        else:
            save = saveArchivesReponse(reponse_etudiant["date"], reponse_etudiant["est_correcte"],
                                len(reponse_etudiant["answer"]), reponse_etudiant["id"], id_question)

        return save

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion des reponses de la diffusion : ", error)
        return False


# Ajoute la réponse de l'étudiant dans les archives des réponses
# Param : - date : la date de la diffusion (int)
#         - est_correcte : entier qui permet de savoir si la réponse est juste (int)
#         - reponse : la réponse (pour une question numérique) ou le nombre de réponses (pour un QCM) de l'étudiant
#         - id_etudiant : l'id de l'etudiant (int)
#         - id_question : l'id de la question (int)
# Return : Si ajout de la réponse :
#               True
#           Sinon :
#               False en cas d'échec
def saveArchivesReponse(date, est_correcte, reponse, id_etudiant, id_question):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Insertion des données de la réponse dans la table d'archive des réponses
        cursor.execute("INSERT INTO ArchivesReponses (date, est_correcte, reponse, etudiant, question) VALUES (?, ?, ?, ?, ?);",
                       (date, est_correcte, reponse, id_etudiant, id_question))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion de la reponse de la diffusion : ", error)
        return False


# Permet de verifier si l'étudiant a eu la bonne réponse aux différentes questions
# Param : tableau_reponses_etudiants : un tableau contenant les réponses de tous les étudiants
#         [
#          {'id': 22100000, 'question': 6, 'answer': 20,'date':1678558000},
#          {'id': 22100000, 'question': 18, 'answer': [33],'date':1678558989}
#           ]
#           reponse_juste_question : tableau de question contenant les bonnes réponses de la question
#           [
#           {'id': 6, 'numerique': 206.0},
#           {'id': 18, 'reponse': [34]}
#           ]
# Return : le même tableau, mais en ajoutant si l'étudiant a eu correcte aux questions
#           [
#           {'id': 22100000, 'question': 6, 'answer': 20,'date':1678558000, 'est_correcte': 0},
#           {'id': 22100000, 'question': 18, 'answer': [33],'date':1678558989, 'est_correcte': 0}
#           ]
def addEstCorrecte(tableau_reponses_etudiants, reponse_juste_question):

    # Boucle qui parcourt toutes les questions
    for i in range(len(reponse_juste_question)):

        # Boucle qui parcourt toutes les réponses des étudiants
        for j in range(len(tableau_reponses_etudiants)):

            # Verifier si on n'a pas déjà ajouté "est correcte" à cette réponse et si on est sur la question que l'on vérifie
            if not ('est_correcte' in tableau_reponses_etudiants[j]) and reponse_juste_question[i]["id"] == tableau_reponses_etudiants[j]["question"]:
                # Si on est sur une question sous forme de QCM
                if "reponse" in reponse_juste_question[i]:

                    # Si les longueurs des réponses correspondent pour éviter un tour de boucle inutile
                    if len(tableau_reponses_etudiants[j]['answer']) != len(reponse_juste_question[i]["reponse"]):
                        tableau_reponses_etudiants[j]['est_correcte'] = 0
                    else:
                        k = 0
                        # Boucle pour savoir si l'étudiant a toutes les bonnes réponses au QCM
                        while k < len(reponse_juste_question[i]["reponse"]) and reponse_juste_question[i]["reponse"][k] in \
                                tableau_reponses_etudiants[j]['answer']:
                            k += 1

                        # On est allé à la fin de la boucle, on a donc la bonne réponse
                        if k == len(reponse_juste_question[i]["reponse"]):
                            tableau_reponses_etudiants[j]['est_correcte'] = 1
                        else:
                            tableau_reponses_etudiants[j]['est_correcte'] = 0
                # Sinon, on est sur une question avec une réponse numérique
                else:
                    # Comparaison pour voir si on a la bonne réponse ( /!\ ils doivent être du même type)
                    if tableau_reponses_etudiants[j]['answer'] == reponse_juste_question[i]["numerique"]:
                        tableau_reponses_etudiants[j]['est_correcte'] = 1
                    else:
                        tableau_reponses_etudiants[j]['est_correcte'] = 0
    return tableau_reponses_etudiants


# Supprime l'archive de la diffusion
# Param : id_diffusion : id de la diffusion a supprimé (int)
#         id_enseignant : id de l'enseignant qui possède l'archive (int)
def removeDiffusion(id_diffusion, id_enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Suppression de la séquence (update on cascade supprime les archives des questions et réponses liées)
        cursor.execute("DELETE FROM ArchivesDiffusions WHERE id = ? AND enseignant=?;", (id_diffusion, id_enseignant))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de la séquence :", error)
        return False
