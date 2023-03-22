import sqlite3

from functions.broadcast import generateCode
from functions.fonctionLabels import getLiensEtiquettes


# Récupère l'id de l'enseignant ayant créé l'étiquette (permet aussi de vérifier que la séquence existe)
# Param : id de l'étiquette (int)
# Return : l'id de l'enseignant (int) ou False si l'étiquette n'est pas trouvée
def getEnseignant(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Selection des données dans la table
        result = cursor.execute("SELECT enseignant FROM Sequences WHERE id = ?;", (id,))
        result = result.fetchone()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        if result:
            return result[0]
        return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'id :", error)
        return False


# Ajoute une séquence dans la BDD
# Param : - enseignant : id du créateur de la séquence (int)
#         - titre : nom de la séquence (string)
#         - tab_question : un tableau avec les id des questions de la séquence (tab[int])
def addSequence(enseignant, titre, tab_questions):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Insertion de la séquence
        cursor.execute("INSERT INTO Sequences (titre, enseignant) VALUES (?, ?);", (titre, enseignant))
        conn.commit()

        # Récupère la valeur du dernier auto-increment
        id_sequence = cursor.lastrowid

        # Ajoute le lien entre la question et la séquence pour chaque question
        for i in range(len(tab_questions)):
            cursor.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?, ?);",
                           (id_sequence, tab_questions[i]))
            conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'ajout de la séquence :", error)
        return False


# Modifie une séquence
# Param : - id : id de la séquence à modifier (int)
#         - titre : nom de la séquence (string)
#         - tab_question : un tableau avec les id des questions de la séquence (tab[int])
# Return : - 0 si réussite
#          - 1 si échec de la requête
#          - 2 si la séquence n'est pas trouvée
def editSequence(id, titre, tab_questions):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Modification du titre de la séquence
        cursor.execute("UPDATE Sequences SET titre = ? WHERE id = ?;", (titre, id))
        # Suppression des liens entre les questions et la séquence
        cursor.execute("DELETE FROM liensSequencesQuestions WHERE idSequence = ?;", (id,))
        conn.commit()

        # Pour chaque question
        for i in range(len(tab_questions)):
            # Ajout des liens entre les questions et la séquence
            cursor.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?, ?);",
                        (id, tab_questions[i]))
            conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la modification de la séquence :", error)
        return False


# Supprime une séquence
# Param : l'id de la séquence (int)
# Return : - 0 si réussite
#          - 1 si échec de la requête
#          - 2 si la sequence n'est pas trouvée
def removeSequence(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Suppression de la séquence (update on cascade supprime les liens)
        cursor.execute("DELETE FROM Sequences WHERE id = ?;", (id,))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de la séquence :", error)
        return False


# Récupère une séquence
# Param : l'id de la séquence (int)
# Return : les informations de la séquence (dico)
#            {"id":1,
#             "titre":"Les Array list en java",
#             "questions":[6, 18]
#            }
def getSequence(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Sélection de la séquence et de ses liens avec les questions
        result = cursor.execute("SELECT id, titre, idQuestion FROM Sequences \
                                    JOIN liensSequencesQuestions ON Sequences.id=liensSequencesQuestions.idSequence \
                                    WHERE id=?;", (id,))
        result = result.fetchall()

        # Fermeture de la connection
        cursor.close()
        conn.close()

        # Si la séquence n'existe pas
        if not result:
            return False

        # Ordonne les données dans un dico
        data = {
            "id": result[0][0],
            "titre": result[0][1],
            "questions": []
        }

        # Pour chaque lien, met l'id de la question dans le tableau
        for i in range(len(result)):
            # On ajoute les id de chaque question
            data["questions"].append(result[i][2])
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de la séquence :", error)
        return False


# Récupère toutes les séquences d'un enseignant
# Param : l'id de l'enseignant (int)
# Return : les informations de la séquence (dico) ou False si échec de la requête
#            [{"id":1,
#             "titre":"Les Array list en java",
#             "questions":[6, 18]}
#             "listeEtiquettes":["{"nom":"Java", "couleur":"c47f31"}, {...}]
#             }, {...}, ...]
def getAllSequences(id_enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Sélection des séquences de l'enseignant et de leurs liens avec les questions
        result = cursor.execute("SELECT id, titre FROM Sequences WHERE enseignant=?;", (id_enseignant,))
        result = result.fetchall()

        # Pour chaque séquence
        data = []
        for k in range(len(result)):
            sequence = {
                "id": result[k][0],
                "titre": result[k][1],
                "questions": [],
                "listeEtiquettes": []
            }

            etiquette_added = []  # Contient les noms des étiquettes déjà ajoutées, pour enlever les doublons

            # Sélection des id des questions liées à la sequence
            result_question = cursor.execute("SELECT idQuestion FROM liensSequencesQuestions WHERE idSequence=?;",
                                             (sequence["id"],))
            result_question = result_question.fetchall()

            # Pour chaque question
            for i in range(len(result_question)):
                sequence["questions"].append(result_question[i][0])  # On ajoute l'id de la question
                result_etiquette = getLiensEtiquettes(result_question[i][0])  # Récupère les étiquettes de la question

                # Pour chaque étiquette
                for j in range(len(result_etiquette)):
                    # On ajoute l'étiquette si elle n'y est pas encore
                    if not (result_etiquette[j]["nom"] in etiquette_added):
                        etiquette_added.append(result_etiquette[j]["nom"])
                        sequence["listeEtiquettes"].append(result_etiquette[j])

            data.append(sequence)  # On ajoute notre beau dico au tableau

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des séquences :", error)
        return 0
