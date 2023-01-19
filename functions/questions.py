import sqlite3

import functions.fonctionLabels as fonctionLabels


# fonction qui permet de récupérer les questions et les réponses créées par un utilisateur
# sous cette forme :
# [
#   { "enonce": "Comment tou tou péle?",
#     "id": 1,
#     "etiquette": [{"couleur": "#000000", "nom": "algo"},...],
#     "reponses": [{"id": 1, "question": 1, "reponse": "Dounnouvahannne", "reponseJuste": 1},...],
#     "user": 1 }
# ]
def getQuestions(userId, label):

    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui ont une etiquette
    sql = """SELECT questions.enonce, questions.id, questions.user FROM questions 
             JOIN liensEtiquettesQuestions ON liensEtiquettesQuestions.questions = questions.id
             WHERE questions.user = ? AND liensEtiquettesQuestions.etiquettes = ?"""

    res = cur.execute(sql, (userId, label))
    res = res.fetchall()


    # Ranger les données sous forme de tableau de dictionnaire
    data = []
    for i in range(0, len(res)):
        # Dans le dictionnaire, on a les valeurs de la question et
        # un tableau de réponses qui contient toutes les réponses associées à la question
        dico = {
            "id": res[i][0],
            "enonce": res[i][1],
            "user": res[i][2],
            "etiquette": fonctionLabels.getLiensEtiquettes(res[i][0]),
            "reponses": getReponses(res[i][0])
        }
        data.append(dico)

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    # et seulement celle qui n'ont pas d'étiquette

    # Fermeture de la connection
    cur.close()
    con.close()

    return data


# fonction qui permet l'ajout d'une question (ses reponses, et ses etiquettes)
# faite par un utilisateur dans la table des questions
def addQuestions(enonce, user, liensEtiquettesQuestions, reponses):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Insertion de la nouvelle question dans la table des questions
        sql = "INSERT INTO questions (enonce, user) VALUES (?, ?);"
        data = (enonce, user)
        cur.execute(sql, data)
        con.commit()

        # Ensuite, on récupère l'id de la dernière question insérée
        questionsId = cur.lastrowid

        # Fermeture de la connection
        cur.close()
        con.close()

        # On ajoute tous les liens entre les étiquettes et les questions
        # en ayant comme prérequis que les étiquettes sont déjà créées et la question aussi
        for i in range(0, len(liensEtiquettesQuestions)):
            fonctionLabels.addLiensEtiquettesQuestions(liensEtiquettesQuestions[i], questionsId)

        # On ajoute toutes les réponses associées à la question
        for i in range(0, len(reponses)):
            addReponses(questionsId, reponses[i]["reponse"], reponses[i]["reponseJuste"])

        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False


# fonction qui renvoie un tableau de dico qui contient les réponses :
# [{"id": 1, "question": 1, "reponse": "Dounnouvahannne", "reponseJuste": 1},...]
def getReponses(questionId):
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les réponses associées à la question grâce à l'id de celle-ci
    res = cur.execute("SELECT * FROM reponses WHERE question=?", (questionId,))
    res = res.fetchall()

    # On les range dans un dictionnaire pour que ce soit plus simple d'utilisation
    data = []
    for i in range(0, len(res)):
        dico = {"id": res[i][0], "question": res[i][1], "reponse": res[i][2],
                "reponseJuste": res[i][3]}
        data.append(dico)

    # Fermeture de la connection
    cur.close()
    con.close()
    return data


# fonction qui permet l'ajout d'une réponse associée à une question, dans la table reponses de la BDD
def addReponses(question, reponse, reponseJuste):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table des reponses
        sql = "INSERT INTO reponses (question, reponse,reponseJuste) VALUES (?, ?, ?)";
        data = (question, reponse, reponseJuste)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False


# Supprime l'étiquette donnée en paramètre dans la base de donnée
def deleteQuestion(id, userId):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # À mettre quand on veut supprimer des lignes,
        # car les CASCADE ont besoin de cet attribut en True
        cur.execute("PRAGMA foreign_keys = ON")

        sql = 'DELETE FROM questions WHERE id = ? AND user=?'
        cur.execute(sql, (id, userId))

        res = cur.execute("SELECT * FROM questions WHERE id = ?", (id, ))
        res= res.fetchall()
        con.commit()

        cur.close()
        con.close()
        if len(res) is 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression !", error)
        return False
