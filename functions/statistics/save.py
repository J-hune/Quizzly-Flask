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
#          {'id': 22100000, 'question': 6, 'answer': 20,'date':1678558000, 'est_correcte': 0},
#          {'id': 22100000, 'question': 18, 'answer': [33],'date':1678558989, 'est_correcte': 0}
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

    # Insère les données des questions dans la table d'archive des questions
    for i in range(len(tableau_questions)):
        saveArchivesQuestions(tableau_questions[i], diffusion_id)

    # Récupère les infos et réponses des étudiants qui ont participé à la diffusion
    tableau_reponses_etudiants = sequence["reponsesEtudiant"]

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
# Param : - id_question : id de la question à ajouter (int)
#         - id_diffusion : id de la diffusion lier à la question (int)
# Return : Si ajout de la question :
#               True
#           Sinon :
#               False en cas d'échec
def saveArchivesQuestions(id_question, id_diffusion):

    # Appel a une fonction pour récupérer toutes les données de la question
    data_question = getQuestion(id_question)
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