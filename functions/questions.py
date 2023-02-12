import sqlite3

import functions.fonctionLabels as fonctionLabels


# fonction qui permet de récupérer les questions et les réponses créées par un enseignant
# sous cette forme :
# [
#   {
# #     "id": 1,
# #     "type": 0,
# #     "enonce": "Qui a calculé la circonférence de la terre en -200 av JC ?",
# #     "enseignant": 1
# #     "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
# #     "reponses": [{"id": 1, "question": 1, "reponse": "Ératosthène", "reponseJuste": 1},...],
# #   }
# ]
def getQuestions(userId, label):

    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui ont une etiquette

    if label is not None:
        sql = """SELECT Q.id, Q.enonce, Q.enseignant, Q.type FROM Questions Q
             JOIN liensEtiquettesQuestions liens ON liens.question = Q.id JOIN Etiquettes E ON E.id= liens.etiquette
             WHERE Q.enseignant = ? AND E.nom = ?"""
        parameters = (userId, label)

    else:
        sql = "SELECT id, enonce, enseignant, type FROM Questions WHERE enseignant = ?"
        parameters = (userId, )

    res = cur.execute(sql, parameters)
    res = res.fetchall()


    # Ranger les données sous forme de tableau de dictionnaire
    data = []
    for i in range(0, len(res)):
        # Dans le dictionnaire, on a les valeurs de la question et
        # un tableau de réponses qui contient toutes les réponses associées à la question
        dico = {
            "id": res[i][0],
            "enonce": res[i][1],
            "enseignant": res[i][2],
            "etiquettes": fonctionLabels.getLiensEtiquettes(res[i][0], userId),
            "reponses": getReponses(res[i][0], res[3])
        }
        data.append(dico)

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui n'ont pas d'étiquette

    # Fermeture de la connection
    cur.close()
    con.close()

    return data


# fonction qui retourne la question désignée par son id (avec ses réponses)
# sous la forme suivante :
#   {
#     "id": 1,
#     "type": 0,
#     "enonce": "Qui a calculé la circonférence de la terre en -200 av JC ?",
#     "enseignant": 1
#     "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#     "reponses": [{"id": 1, "question": 1, "reponse": "Ératosthène", "reponseJuste": 1},...],
#   }
def getQuestion(userId, id):
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui ont une etiquette
    sql = """SELECT Questions.id, Questions.enonce, Questions.enseignant, Questions.type FROM Questions 
             WHERE Questions.enseignant = ? AND id = ?"""

    res = cur.execute(sql, (userId, id))
    res = res.fetchone()

    if not res:
        return False

    # Dans le dictionnaire, on a les valeurs de la question et
    # un tableau de réponses qui contient toutes les réponses associées à la question
    dic = {
        "id": res[0],
        "type": res[3],
        "enonce": res[1],
        "enseignant": res[2],
        "etiquettes": fonctionLabels.getLiensEtiquettes(res[0], userId),
        "reponses": getReponses(res[0], res[3])
    }

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui n'ont pas d'étiquette

    # Fermeture de la connection
    cur.close()
    con.close()

    return dic


# fonction qui permet l'ajout d'une question (ses reponses, et ses etiquettes)
# faite par un enseignant dans la table des questions
def addQuestions(questionType, enonce, enseignant, etiquettes, reponses):

    if len(reponses)==0 or len(reponses[0])==0:
        return False
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Insertion de la nouvelle question dans la table des questions
        sql = "INSERT INTO Questions (type, enonce, enseignant) VALUES (?, ?, ?);"
        data = (questionType, enonce, enseignant)
        cur.execute(sql, data)
        con.commit()

        # Ensuite, on récupère l'id de la dernière question insérée
        questionsId = cur.lastrowid

        # Fermeture de la connection
        cur.close()
        con.close()

        # On ajoute tous les liens entre les étiquettes et les questions
        # en ayant comme prérequis que les étiquettes sont déjà créées et la question aussi
        for i in range(0, len(etiquettes)):
            fonctionLabels.addLiensEtiquettesQuestions(etiquettes[i]["nom"], questionsId, enseignant)

        # On ajoute toutes les réponses associées à la question
        for i in range(0, len(reponses)):
            if len(reponses[i]["reponse"]) != 0:
                if(reponses[i]["reponseJuste"]):
                    reponseJuste = 1
                else:
                    reponseJuste = 0
                addReponses(reponses[i]["reponseType"], reponses[i]["reponse"], reponseJuste, questionsId)

        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False


# fonction qui renvoie un tableau de dico qui contient les réponses :
# [{"id": 1, "reponse": "Dounnouvahannne", "reponseJuste": 1, "question": 1},...]
def getReponses(questionId, questionType):
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les réponses associées à la question grâce à l'id de celle-ci
    res = cur.execute("SELECT * FROM Reponses WHERE question=? AND type=?", (questionId, questionType))
    res = res.fetchall()

    # On les range dans un dictionnaire pour que ce soit plus simple d'utilisation
    data = []
    for i in range(0, len(res)):
        dico = {
            "id": res[i][0],
            "reponse": res[i][2],
            "reponseJuste": bool(res[i][3]),
            "question": res[i][4],
        }
        data.append(dico)

    # Fermeture de la connection
    cur.close()
    con.close()
    return data


# fonction qui permet l'ajout d'une réponse associée à une question, dans la table reponses de la BDD
def addReponses(reponseType, reponse, reponseJuste, question):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table des reponses
        sql = "INSERT INTO Reponses (type, reponse, reponseJuste, question) VALUES (?, ?, ?, ?)"
        data = (reponseType, reponse, reponseJuste, question)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False


# Supprime la question donnée en paramètre dans la base de donnée
def deleteQuestion(id, userId):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # À mettre quand on veut supprimer des lignes,
        # car les CASCADE ont besoin de cet attribut en True
        cur.execute("PRAGMA foreign_keys = ON")

        sql = 'DELETE FROM Questions WHERE id = ? AND enseignant=?'
        cur.execute(sql, (id, userId))

        res = cur.execute("SELECT * FROM Questions WHERE id = ?", (id,))
        res = res.fetchall()
        con.commit()

        cur.close()
        con.close()
        if len(res) == 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression !", error)
        return False


# Edit une question, c'est-à-dire supprime la question et la remet dans la base de données
# ATTENTION à l'id qui change
def editQuestion(id, questionType, enonce, enseignant, etiquettes, reponses):
    # Verifie si l'id correspond à une question faite par l'enseignant
    if not deleteQuestion(id, enseignant):
        return False

    return addQuestions(questionType, enonce, enseignant, etiquettes, reponses)
