import sqlite3


# fonction qui permet de récupérer les questions et les réponses créées par un utilisateur
def getQuestions(userId):

    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les questions faites par le prof grâce à l'id de celle-ci
    res = cur.execute("SELECT * FROM questions WHERE user=?", (userId, ))
    res = res.fetchall()

    # Fermeture de la connection
    cur.close()
    con.close()

    # Ranger les données sous forme de tableau de dictionnaire
    data = []
    for i in range(0, len(res)):
        # Dans le dictionnaire, on a les valeurs de la question et
        # un tableau de réponses qui contient toutes les réponses associées à la question
        dico = {"id": res[i][0], "etiquette":res[i][1], "enonce": res[i][2], "user": res[i][3], "reponses": getReponses(res[i][0])}
        data.append(dico)

    return data


# fonction qui permet l'ajout d'une question faite par un utilisateur dans la table des questions
def addQuestions(enonce, user):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Insertion des données dans la table des questions
        sql = """INSERT INTO questions
                (enonce, user) 
                VALUES (?, ?);"""
        data = (enonce, user)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False


# fonction qui renvoie un tableau qui contient les réponses
def getReponses(questionId):
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Requêtes pour récupérer toutes les réponses associées à la question grâce à l'id de celle-ci
    res = cur.execute("SELECT * FROM reponses WHERE question=?", (questionId, ))
    res = res.fetchall()

    # Fermeture de la connection
    cur.close()
    con.close()
    return res


# fonction qui permet l'ajout d'une réponse associée à une question, dans la table reponses de la BDD
def addReponses(question, reponse):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table des reponses
        sql = """INSERT INTO reponses
                (question, reponse) 
                VALUES (?, ?);"""
        data = (question, reponse)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False
