import sqlite3

# Récupère toutes les étiquettes d'un enseignant
# Param : id de l'enseignant (int)
# Return : les étiquettes de l'enseignant (tab de dico)
#            [{"id":666, "nom":"Modèle de calcul", "couleur":"FF0000"}, {...}, ...]
def getLabels(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

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

            # Active les clés étrangères
            cur.execute("PRAGMA foreign_keys = ON")

            sql = "INSERT INTO Etiquettes ('nom','couleur','enseignant') VALUES(?,?,?);"
            value = (nomLabel, couleur, userID)
            cur.execute(sql, value)
            con.commit()
            last_row_id = cur.lastrowid

            cur.close()
            con.close()
            return last_row_id

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette : ", error)
            return False
    else:
        return False


# Modifie une étiquette
# Param : - id : id de l'étiquette (int)
#         - nom : nom de l'étiquette (string)
#         - couleur : couleur de l'étiquette (string)
def editLabel(id, nom, couleur):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Modifie l'étiquette dans la table
        cursor.execute("UPDATE Etiquettes SET nom = ?, couleur = ? WHERE id = ?;", (nom, couleur, id))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la modification de l'étiquette : ", error)
        return False


# Fonction qui récupère les données des étiquettes associées a une question
# et les renvoie sous forme de dico {"nom": ... , "couleur": ...}
def getLiensEtiquettes(questionId):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Active les clés étrangères
    cur.execute("PRAGMA foreign_keys = ON")

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


# Supprime une étiquette (que si elle n'est liée à aucune question)
# Param : l'id de l'étiquette (int)
# Return : - True si réussite
#          - False si échec ou si étiquette liée
def deleteLabel(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Récupère les liens de l'étiquette avec des éventuelles questions
        result = cursor.execute("SELECT * FROM liensEtiquettesQuestions WHERE etiquette = ?;", (id,))
        result = result.fetchone()

        check = False

        # Si l'étiquette n'est pas liée, suppression de l'étiquette dans la table et on renvoie True
        if result is None:
            check = True
            cursor.execute("DELETE FROM Etiquettes WHERE id = ?;", (id,))
            conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        return check

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de l'étiquette la table sqlite : ", error)
        return False
