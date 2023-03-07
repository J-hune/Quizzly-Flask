import sqlite3


# Retourne tous les labels que l'enseignant utilise
def getLabelsUsed(userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    sql = ("SELECT DISTINCT e.nom, e.couleur FROM Etiquettes e\n" +
           " JOIN liensEtiquettesQuestions leq ON e.id = leq.etiquette\n"
           " JOIN Questions q ON leq.question = q.id\n"
           " WHERE q.enseignant = ?"
           )

    res = cur.execute(sql, (userId,))
    res = res.fetchall()
    cur.close()
    con.close()

    return res


# Récupère toutes les étiquettes d'un enseignant
# Param : id de l'enseignant
# Return : les étiquettes de l'enseignant (tab de dico)
#            [{"id":666, "nom":"Modèle de calcul", "couleur":"FF0000"}, {...}, ...]
def getLabels(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère les étiquettes dans la table
        result = cursor.execute("SELECT Etiquettes.id, Etiquettes.nom, Etiquettes.couleur FROM Etiquettes WHERE enseignant = ?;", (id,))
        result = result.fetchall()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Range les données dans un tableau de dictionnaires
        data = []
        for i in range(len(result)):
            dico = {
                "id": result[i][0],
                "nom": result[i][1],
                "couleur": result[i][2]
            }
            data.append(dico)

        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des étiquettes : ", error)
        return False


# Vérifie si l'étiquette donnée en paramètre est dans la base de donnée et la renvoie si elle existe
def searchLabel(nomLabel):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        sql = 'SELECT * FROM Etiquettes WHERE nom= ?'
        value = nomLabel
        # Récupères les données
        res = cur.execute(sql, (value,))
        res = res.fetchall()
        con.commit()

        cur.close()
        con.close()

        # Envoyés les données que si on les a
        if len(res) != 0:
            print("Cette étiquette existe déjà !")
            return res
        else:
            return False

    except sqlite3.Error as error:
        print("Une erreur est survenue ou l'étiquette n'existe pas !", error)
        return False


# Ajoute une étiquette
# Param : - nom : nom de l'étiquette (string)
#         - couleur : couleur de l'étiquette ex : #000000 (string)
#         - userID : créateur de l'étiquette (int)
def addLabel(nomLabel, couleur, userID):
    if not searchLabel(nomLabel):
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            sql = "INSERT INTO Etiquettes ('nom','couleur','enseignant') VALUES(?,?,?);"
            value = (nomLabel, couleur, userID)
            cur.execute(sql, value)
            con.commit()

            cur.close()
            con.close()
            return True

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette : ", error)
            return False
    else:
        return False


# Ajoute les liens entre la question et les étiquettes
# pré-requis on a la question et l'étiquette dans la BDD
# Fonction migrée vers question.py en addLinksQuestionLabels /!\ À GARDER POUR LE MOMENT /!\
"""def addLiensEtiquettesQuestions(etiquette, question, userID):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        sql = 'SELECT id FROM Etiquettes WHERE nom=? AND enseignant=?'
        value = (etiquette, userID)
        res = cur.execute(sql, value)
        res = res.fetchall()
        if len(res) != 0 or len(res[0]) != 0:

            sql = 'INSERT INTO liensEtiquettesQuestions VALUES(?,?)'
            value = (question, res[0][0])
            cur.execute(sql, value)
            con.commit()
            cur.close()
            con.close()
            return True
        else:
            cur.close()
            con.close()
            return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la création du lien entre l'étiquette et la question : ", error)
        return False"""


# Fonction qui récupère les données des étiquettes associées a une question
# et les renvoie sous forme de dico {"nom": ... , "couleur": ...}
def getLiensEtiquettes(questionId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    res = cur.execute("""SELECT nom, couleur FROM Etiquettes
                    JOIN liensEtiquettesQuestions ON Etiquettes.id = liensEtiquettesQuestions.etiquette 
                    WHERE liensEtiquettesQuestions.question=?;""", (questionId,))
    res = res.fetchall()
    data = []
    for i in range(0, len(res)):
        dico = {"nom": res[i][0], "couleur": res[i][1]}
        data.append(dico)

    cur.close()
    con.close()
    return data


# @Unused
# Supprime une étiquette
# Param : l'id de l'étiquette
def deleteLabel(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Insertion des données dans la table
        cursor.execute("DELETE FROM Etiquettes WHERE id = ?;", (id,))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de l'étiquette la table sqlite : ", error)
        return False
