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
    # Si la séquence existe
    if getEnseignant(id):
        try:
            # Connection à la BDD
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Active les clés étrangères
            cursor.execute("PRAGMA foreign_keys = ON")

            # Modification du titre de la séquence
            cursor.execute("UPDATE Sequences SET titre = ? WHERE id = ?;", (titre, id))

            # Suppression des données dans la table
            cursor.execute("DELETE FROM liensSequencesQuestions WHERE idSequence = ?;", (id,))
            conn.commit()

            # pour chaque question
            for i in range(len(tab_questions)):
                # insertion des données dans la table
                cursor.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?, ?);",
                            (id, tab_questions[i]))
                conn.commit()

            # Fermeture de la connection
            cursor.close()
            conn.close()
            return 0

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la modification de la séquence :", error)
            return 1
    else:
        return 2


# Supprime une séquence
# Param : l'id de la séquence (int)
# Return : - 0 si réussite
#          - 1 si échec de la requête
#          - 2 si la sequence n'est pas trouvée
def removeSequence(id):
    # Si la séquence existe
    if getEnseignant(id):
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
            return 0

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la suppression de la séquence :", error)
            return 1
    else:
        return 2


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
# Return : les informations de la séquence (dico)
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

        # Sélection des séquences de l'enseignant et de leurs liens avec les questions
        result = cursor.execute("SELECT id, titre FROM Sequences WHERE enseignant=?;", (id_enseignant,))
        result = result.fetchall()

        if result:
            sequences = []
            for k in range(len(result)):
                dico_result = {
                    "id": result[k][0],
                    "titre": result[k][1],
                    "questions": []
                }

                # Tableau qui contient les etiquettes
                liste_etiquette = []
                # Tableau qui contient les noms des etiquettes deja ajouté pour pas de doublon
                liste_etiquette_nom_ajoute = []

                # Requetes SQL pour récupérer les id des questions de la sequence
                result_request_question = cursor.execute(
                    "SELECT idQuestion FROM liensSequencesQuestions WHERE idSequence=?;", (dico_result["id"],))
                result_request_question = result_request_question.fetchall()
                # On crée un tableau pour les questions
                dico_result["questions"] = []
                for i in range(len(result_request_question)):
                    # On ajoute les id de chaque question
                    dico_result["questions"].append(result_request_question[i][0])

                    # Appel a la fonction pour récupérer toutes les étiquettes associées à la question
                    liste_etiquette_question = getLiensEtiquettes(result_request_question[i][0])
                    for j in range(len(liste_etiquette_question)):
                        # On ajoute les étiquettes que si on ne les a pas
                        if not (liste_etiquette_question[j]["nom"] in liste_etiquette_nom_ajoute):
                            liste_etiquette_nom_ajoute.append(liste_etiquette_question[j]["nom"])
                            liste_etiquette.append(liste_etiquette_question[j])
                dico_result["listeEtiquettes"] = liste_etiquette
                # On ajoute notre beau dico au tableau
                sequences.append(dico_result)
            conn.commit()
            # Fermeture de la connection
            cursor.close()
            conn.close()
            return sequences
        else:

            # Fermeture de la connection
            cursor.close()
            conn.close()
            return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des séquences :", error)
        return False


# Renvoie les 3 dernières diffusions auxquelles un étudiant a participé
# Param : id de l'étudiant
# Return : les trois dernières diffusions de l'étudiant (tab de dico)
#               [{"id":7,                           (--> id de la séquence qui a été diffusé)
#                 "enseignant":"Michel Staelens",
#                 "participants":25,
#                 "pourcentage":"82,7",             (--> pourcentage de réussite de l'étudiant)
#                 "date":07032023
#                 }, ...]
def getLastSequences(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Récupère l'id des 3 dernières séquences participé, le nom/prénom du prof et le pourcentage de bonne réponse
        #                                                                   nbRéponse     nbBonneRéponse
        result = cursor.execute("SELECT AD.id, AD.mode, E.prenom, E.nom, COUNT(AR.id), SUM(AR.est_correcte), AD.date \
                                            FROM ArchivesDiffusions AD \
                                            JOIN ArchivesReponses AR ON AD.id = AR.diffusion \
                                            JOIN Enseignants E ON AD.enseignant = E.id \
                                            JOIN Sequences S ON AD.mode = S.id \
                                            WHERE AR.etudiant = ? \
                                            GROUP BY AD.id \
                                            ORDER BY AD.date DESC LIMIT 3;", (id,))
        result = result.fetchall()

        # Ordonne les données dans un tableau pour chaque séquence
        tab = []
        for i in range(len(result)):
            # Récupère le nombre de participants à la diffusion
            nb_participant = cursor.execute("SELECT COUNT(DISTINCT AR.etudiant) \
                                            FROM ArchivesDiffusions AD \
                                            JOIN ArchivesReponses AR ON AD.id = AR.diffusion \
                                            WHERE AD.id = ? \
                                            GROUP BY AD.id;", (result[i][0],))
            nb_participant = nb_participant.fetchone()

            # Fermeture de la connection
            cursor.close()
            conn.close()

            # Range les données dans un dico
            data = {"id": result[i][1],
                    "enseignant": result[i][2] + " " + result[i][3],
                    "participants": nb_participant[0],
                    "pourcentage": ((result[i][5] / result[i][4]) * 100),
                    "date": result[i][6]
                    }
            tab.append(data)

        return tab

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des dernières séquences :", error)
        return 0
