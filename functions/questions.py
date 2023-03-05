import sqlite3
import functions.fonctionLabels as fonctionLabels


# Récupère toutes les questions associées aux étiquettes (et leurs réponses) créées par un enseignant
# Params : - userId : l'id de l'enseignant
#          - label : un tableau d'étiquettes (string)
# Return : tableau de dico sous cette forme
#           [
#             {
#               "id": 1,
#               "type": 0,
#               "enonce": "Combien vaut pi ?",
#               "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#               "numerique": "3.14",
#               "reponses": [{"id": 1, "question": 1, "reponse": "Trois quatorze", "reponseJuste": 1},...],
#             }, ...
#           ]
def getQuestions(enseignant, etiquettes):
    try :
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Si aucune étiquette n'est précisée, on récupère toutes les questions de l'enseignant
        if etiquettes is None:
            sql = "SELECT id, enonce, enseignant, type, numerique FROM Questions WHERE enseignant = ?;"
            parameters = (enseignant,)
        # Sinon, on récupère les questions de l'enseignant selon les étiquettes choisies
        else:
            sql = "SELECT Q.id, Q.enonce, Q.type, Q.numerique \
                            FROM Questions Q \
                            JOIN liensEtiquettesQuestions liens ON liens.question = Q.id \
                            JOIN Etiquettes E ON E.id= liens.etiquette \
                            WHERE Q.enseignant = ? AND E.nom = ?;" ###PROBLEME SI DEUX MEME NOMS
            parameters = (enseignant, etiquettes)

        result = cursor.execute(sql, parameters)
        result = result.fetchall()

        # Range les données dans un tableau de dictionnaires
        data = []
        for i in range(0, len(result)):
            dico = {
                "id": result[i][0],
                "enonce": result[i][1],
                "etiquettes": fonctionLabels.getLiensEtiquettes(result[i][0]),
                "reponses": getReponses(result[i][0]),
                "type": result[i][2],
                "numerique": result[i][3]
            }
            data.append(dico)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélecton des questions : ", error)
        return False


# Retourne une question
# Param : l'id de la question
# Return : un dico sous la forme suivante
#               {
#                 "id": 1,
#                 "type": 0,
#                 "enonce": "Qui a calculé la circonférence de la terre en -200 av JC ?",
#                 "enseignant": 1
#                 "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#                 "numerique": ""
#                 "reponses": [{"id": 1, "question": 1, "reponse": "Ératosthène", "reponseJuste": 1},...],
#               }
def getQuestion(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère la question
        result = cursor.execute("SELECT Questions.id, Questions.enonce, Questions.enseignant, Questions.type, Questions.numerique \
                                    FROM Questions WHERE id = ?;", (id,))
        result = result.fetchone()

        if not result:
            return False

        # Ordonne les données dans un dico
        data = {
            "id": result[0],
            "type": result[3],
            "enonce": result[1],
            "enseignant": result[2],
            "etiquettes": fonctionLabels.getLiensEtiquettes(result[0]),
            "reponses": getReponses(result[0]),
            "numerique": result[4]
        }

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélecton de la question : ", error)
        return False


# Ajoute les liens entre les étiquettes et la question
# Pré-requis : la question et les étiquettes sont déjà créées
# Param : - conn et cursor : BDD
#         - id : id de la question (int)
#         - etiquettes : les étiquettes à lier (tab de dico)
#                           [ {"couleur": "000000", "nom": "musique"},
#                             {"couleur": "FFFFFF", "nom": "ondes"}, ...
#                           ]
#         - enseignant : id du créateur de la question
def addLinksQuestionLabels(conn, cursor, id, etiquettes, enseignant):
    try:
        for i in range(len(etiquettes)):
            result = cursor.execute("SELECT id FROM Etiquettes WHERE nom=? AND enseignant=?;", (etiquettes[i]["nom"], enseignant)) #si deux étiquettes ont le même nom : probleme (id au lieu de "nom")
            result = result.fetchone()
            cursor.execute("INSERT INTO liensEtiquettesQuestions (question, etiquette) VALUES(?,?);", (id, result[0]))
            conn.commit()
            return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la création du lien entre l'étiquette et la question : ", error)
        return False


# Ajoute les réponses de la question
# Param : - conn et cursor : BDD
#         - id : id de la question (int)
#         - reponses : les réponses à insérer (tab de dico)
#                           [ {"reponse": "piano", "reponseJuste": True},
#                             {"reponse": "guitare", "reponseJuste": False}, ...
#                           ]
def addReponses(conn, cursor, id, reponses):
    try:
        for i in range(len(reponses)):
            if len(reponses[i]["reponse"]) != 0:
                if (reponses[i]["reponseJuste"]):
                    reponseJuste = 1
                else:
                    reponseJuste = 0

                # Insertion des données dans la table
                cursor.execute("INSERT INTO Reponses (reponse, reponseJuste, question) VALUES (?, ?, ?);", (reponses[i]["reponse"], reponseJuste, id))
                conn.commit()

        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion des réponses : ", error)
        return False


# Ajoute une question à la BDD avec ses réponses et ses étiquettes
# Param : - questionType : type de la question (1 pour numérique, 0 pour choix)
#         - enonce : énonce de la question (string)
#         - enseignant : créateur de la question
#         - etiquettes : les étiquettes à lier (tab de dico)
#                             [ {"couleur": "000000", "nom": "C#"},
#                               {"couleur": "FFFFFF", "nom": "C++"}, ...
#                             ]
#         - reponses : les réponses à insérer (tab de dico)
#                             [ {"reponse": "Steam", "reponseJuste": True},
#                               {"reponse": "EpicGames", "reponseJuste": False}, ...
#                             ]
#         - numérique : la réponse numérique (float)
def addQuestion(questionType, enonce, enseignant, etiquettes, reponses, numerique):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Insertion de la question dans la table
        cursor.execute("INSERT INTO Questions (type, enonce, enseignant, numerique) VALUES (?, ?, ?, ?);", (questionType, enonce, enseignant, numerique))
        conn.commit()

        # Récupère l'id de la dernière question insérée (avec l'auto-increment)
        questionsId = cursor.lastrowid

        # Ajoute les liens entre les étiquettes et les questions et ajoute les réponses
        addLinksQuestionLabels(conn, cursor, questionsId, etiquettes, enseignant)
        if reponses is not None:
            addReponses(conn, cursor, questionsId, reponses)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion de la question : ", error)
        return False


# Renvoie les réponses d'une question
# Param : l'id de la question
# Return : un tableau de dico avec les réponses
#           [{"id": 1, "reponse": "La réponse D", "reponseJuste": 1, "question": 1},...]
def getReponses(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Requêtes pour récupérer toutes les réponses associées à la question grâce à l'id de celle-ci
        result = cursor.execute("SELECT * FROM Reponses WHERE question=?;", (id,))
        result = result.fetchall()

        # Range les données dans un tableau de dictionnaires
        data = []
        for i in range(0, len(result)):
            dico = {
                "id": result[i][0],
                "reponse": result[i][1],
                "reponseJuste": bool(result[i][2]),
                "question": result[i][3]
            }
            data.append(dico)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des réponses : ", error)
        return False


# Supprime une question
# Param : id de la question
def deleteQuestion(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Supprime la question (et tout ce qui est lié à elle avec delete on cascade)
        cursor.execute("DELETE FROM Questions WHERE id = ?;", (id,))

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True
    
    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de la question : ", error)
        return False


# Modifie une question : supprime ses réponses et ses liens d'étiquettes, modifie la question, et ajoutes les réponses et liens
# Param : - id : id de la question (int)
#         - questionType : type de la question (1 pour numérique, 0 pour choix)
#         - enonce : énonce de la question (string)
#         - etiquettes : les étiquettes à lier (tab de dico)
#                             [ {"couleur": "000000", "nom": "C#"},
#                               {"couleur": "FFFFFF", "nom": "C++"}, ...
#                             ]
#         - reponses : les réponses à insérer (tab de dico)
#                             [ {"reponse": "Steam", "reponseJuste": True},
#                               {"reponse": "EpicGames", "reponseJuste": False}, ...
#                             ]
#         - numérique : la réponse numérique (float)
def editQuestion(id, questionType, enonce, etiquettes, reponses, numerique):
    try:
        # Connection à la table
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Suppression des réponses et des liens entre étiquette et question
        cursor.execute("DELETE FROM Reponses WHERE question = ?;", (id,))
        conn.commit()
        cursor.execute("DELETE FROM liensEtiquettesQuestions WHERE question = ?;", (id,))
        conn.commit()

        # Mise à jour de la question
        cursor.execute("UPDATE Questions \
                        SET type = ?, enonce = ?, numerique = ? \
                        WHERE id = ?;", (questionType, enonce, numerique, id))
        conn.commit()

        ###TEMPORAIRE /!\
        result = cursor.execute("SELECT enseignant FROM Questions WHERE id=?;", (id,)) ###CECI N'EST PAS OPTI
        idprof = result.fetchone()
        ###TEMPORAIRE /!\

        # Ajout des liens entre les étiquettes et les questions et ajoute les réponses
        addLinksQuestionLabels(conn, cursor, id, etiquettes, idprof[0])
        addReponses(conn, cursor, id, reponses)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la modification de la question : ", error)
        return False

# fonction qui permet l'ajout d'une réponse associée à une question, dans la table reponses de la BDD /!\ FONCTION PASSEE A MODIFIE /!\
def addReponse(reponse, reponseJuste, question):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table des reponses
        sql = "INSERT INTO Reponses (reponse, reponseJuste, question) VALUES (?, ?, ?, ?)"
        data = (reponse, reponseJuste, question)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite : ", error)
        return False