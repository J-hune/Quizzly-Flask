import sqlite3


# Récupère une étiquette avec le nom (permet aussi de vérifier si cette étiquette existe)
# Param : - nom de l'étiquette (string)
#         - id de l'enseignant (int)
# Return : les infos de l'étiquette (tuple)
def searchLabelWithName(nom, id_enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère l'étiquette
        result = cursor.execute("SELECT * FROM Etiquettes WHERE nom = ? AND enseignant = ?;", (nom, id_enseignant))
        result = result.fetchone()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Si l'étiquette est trouvée, on envoie les données
        if not result:
            return False
        else:
            return result

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'étiquette :", error)
        return False


# Récupère une étiquette avec son id (permet aussi de vérifier si cette étiquette existe)
# Param : id de l'étiquette (int)
# Return : les infos de l'étiquette (tuple)
def searchLabelWithId(id_etiquette, id_enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère l'étiquette
        result = cursor.execute("SELECT * FROM Etiquettes WHERE id = ? AND enseignant = ?;", (id_etiquette, id_enseignant))
        result = result.fetchone()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Si l'étiquette est trouvée, on envoie les données
        if not result:
            return False
        else:
            return result

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'étiquette : ", error)
        return False


# Ajoute une étiquette
# Param : - nom : nom de l'étiquette (string)
#         - couleur : couleur de l'étiquette en hexa (string)
#         - id_enseignant : id du créateur de l'étiquette (int)
# Return : l'id de l'étiquette ajoutée (int) ou False si une étiquette avec le même nom existe déjà ou si erreur
def addLabel(nom, couleur, id_enseignant):
    if not searchLabelWithName(nom, id_enseignant):
        try:
            # Connection à la BDD
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Insère l'étiquette
            cursor.execute("INSERT INTO Etiquettes ('nom','couleur','enseignant') VALUES(?, ?, ?);",
                           (nom, couleur, id_enseignant))
            conn.commit()

            # Récupère l'id de l'étiquette ajoutée
            id = cursor.lastrowid

            # Fermeture de la connection
            cursor.close()
            conn.close()
            return id

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette :", error)
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
        print("Une erreur est survenue lors de la modification de l'étiquette :", error)
        return False


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
        print("Une erreur est survenue lors de la suppression de l'étiquette :", error)
        return False


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
        result = cursor.execute(
            "SELECT Etiquettes.id, Etiquettes.nom, Etiquettes.couleur FROM Etiquettes WHERE enseignant = ?;", (id,))
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
        print("Une erreur est survenue lors de la sélection des étiquettes :", error)
        return False


# Récupère les étiquettes liées à une question
# Param : id de la question (int)
# Return : les étiquettes de la question (tab de dico)
#           [{"nom": "PHP" , "couleur": "FFFFFF},
#            {"nom": "JavaScript , "couleur": "000000"}, ...]
def getLiensEtiquettes(id_question):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Récupère les étiquettes de la question
        result = cursor.execute("SELECT nom, couleur, id FROM Etiquettes \
                                JOIN liensEtiquettesQuestions ON Etiquettes.id = liensEtiquettesQuestions.etiquette \
                                WHERE liensEtiquettesQuestions.question=?;", (id_question,))
        result = result.fetchall()

        # Ordonne les données dans un tableau de dico
        data = []
        for i in range(len(result)):
            dico = {"nom": result[i][0],
                    "couleur": result[i][1],
                    "id":result[i][2]}
            data.append(dico)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des liens entre la question et les étiquettes :", error)
        return False
