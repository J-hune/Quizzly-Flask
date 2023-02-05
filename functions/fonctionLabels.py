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


# Retourne tous les labels de l'enseignant
def getLabels(userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    sql = ("\n"
           "    SELECT Etiquettes.nom, Etiquettes.couleur FROM Etiquettes\n"
           "        WHERE enseignant = ?")

    res = cur.execute(sql, (userId,))
    res = res.fetchall()
    cur.close()
    con.close()

    return res


# Supprime l'étiquette donnée en paramètre dans la base de donnée
# Non utilisé dans notre cas
def supprLabel(nomLabel):
    if searchLabel(nomLabel):
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            sql = 'DELETE FROM Etiquettes WHERE nom = ?'
            cur.execute(sql, (nomLabel,))
            con.commit()
            print("L'étiquette a été supprimée !")

            cur.close()
            con.close()
            return True


        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la suppression !", error)
            return False
    else:
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


# Ajoute une étiquette avec une couleur choisie dans la base de donnée
def addLabel(nomLabel, couleur, userID):
    if not searchLabel(nomLabel):
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            sql = "INSERT INTO Etiquettes ('nom','couleur','enseignant') VALUES(?,?,?)"
            value = (nomLabel, couleur, userID)
            cur.execute(sql, value)
            con.commit()

            cur.close()
            con.close()
            return True

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette !", error)
            return False
    else:
        return False


# Requêtes pour ajouter un nouveau lien entre une question et une étiquette
# pré-requis on a la question et l'étiquette dans la BDD
def addLiensEtiquettesQuestions(etiquette, question, userID):
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
        print("Une erreur est survenue lors de la création du lien entre l'étiquette et la question !", error)
        return False


# Fonction qui récupère les données des étiquettes associées a une question
# et les renvoie sous forme de dico {"nom": ... , "couleur": ...}
def getLiensEtiquettes(questionId, userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    res = cur.execute("""SELECT nom, couleur FROM Etiquettes
                    JOIN liensEtiquettesQuestions ON Etiquettes.id = liensEtiquettesQuestions.etiquette 
                    WHERE liensEtiquettesQuestions.question=? AND Etiquettes.enseignant=?""", (questionId, userId))
    res = res.fetchall()
    data = []
    for i in range(0, len(res)):
        dico = {"nom": res[i][0], "couleur": res[i][1]}
        data.append(dico)

    cur.close()
    con.close()
    return data
