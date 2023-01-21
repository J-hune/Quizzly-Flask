import sqlite3


# Retourne tous les labels que l'utilisateur utilise
def getLabelsUsed(userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    sql = ("\n"
           "    SELECT etiquettes.nom, etiquettes.couleur FROM etiquettes\n"
           "        JOIN liensEtiquettesQuestions ON liensEtiquettesQuestions.etiquettes = etiquettes.nom\n"
           "        JOIN questions ON questions.id = liensEtiquettesQuestions.questions\n"
           "        WHERE questions.user = ?\n "
           "        GROUP BY etiquettes.nom, etiquettes.user, etiquettes.couleur")

    res = cur.execute(sql, (userId,))
    res = res.fetchall()
    cur.close()
    con.close()

    return res


# Retourne tous les labels de l'utilisateur
def getLabels(userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    sql = ("\n"
           "    SELECT etiquettes.nom, etiquettes.couleur FROM etiquettes\n"
           "        WHERE user = ?")

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

            sql = 'DELETE FROM etiquettes WHERE nom = ?'
            cur.execute(sql, (nomLabel,))
            con.commit()
            print("L'étiquette a été supprimée!")

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

        sql = 'SELECT * FROM etiquettes WHERE nom= ?'
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

            sql = 'INSERT INTO etiquettes VALUES(?,?,?)'
            value = (nomLabel, couleur, userID)
            cur.execute(sql, value)
            con.commit()
            print("Etiquette créée !")

            cur.close()
            con.close()
            return True

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette!", error)
            return False
    else:
        return False


# Requêtes pour ajouter un nouveau lien entre une question et une étiquette
# pré-requis on a la question et l'étiquette dans la BDD
def addLiensEtiquettesQuestions(etiquette, question, userID):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        sql = 'INSERT INTO liensEtiquettesQuestions VALUES(?,?,?)'
        value = (etiquette, question, userID)
        cur.execute(sql, value)
        con.commit()

        cur.close()
        con.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la création du lien entre l'étiquette et la question!", error)
        return False


# Fonction qui récupère les données des étiquettes associées a une question
# et les renvoie sous forme de dico {"nom": ... , "couleur": ...}
def getLiensEtiquettes(questionId, userId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    res = cur.execute("""SELECT nom, couleur FROM etiquettes
                    JOIN liensEtiquettesQuestions ON etiquettes.nom = liensEtiquettesQuestions.etiquettes 
                    WHERE liensEtiquettesQuestions.questions=? AND etiquettes.user=?""", (questionId, userId))
    res = res.fetchall()
    data = []
    for i in range(0, len(res)):
        dico = {"nom": res[i][0], "couleur": res[i][1]}
        data.append(dico)

    cur.close()
    con.close()
    return data
