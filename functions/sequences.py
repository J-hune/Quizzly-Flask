import sqlite3

from functions.broadcast import generateCode


def getEnseignant(sequenceId):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Selection des données dans la table
        result = cur.execute("SELECT enseignant FROM Sequences WHERE id = ?;", (sequenceId,))
        result = result.fetchone()

        # Fermeture de la connection
        cur.close()
        con.close()
        if result:
            return result[0]
        return False
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


def addSequence(enseignant, titre, tabIdQuestions):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table
        cur.execute("INSERT INTO Sequences (titre, enseignant) VALUES (?, ?);",
                    (titre, enseignant,))

        # Récupère la valeur du dernier auto-increment
        lastId = cur.lastrowid

        # Pour chaque question
        for i in range(len(tabIdQuestions)):
            # insertion des données dans la table
            cur.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?, ?);",
                        (lastId, tabIdQuestions[i]))
            con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


def editSequence(sequenceId, titre, tabIdQuestions):
    # Si la séquence existe
    if getEnseignant(sequenceId):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Modification du titre de la séquence
            cur.execute("UPDATE Sequences SET titre = ? WHERE id = ?", (titre, sequenceId))

            # Suppression des données dans la table
            cur.execute("DELETE FROM liensSequencesQuestions WHERE idSequence = ?;", (sequenceId,))
            con.commit()

            # pour chaque question
            for i in range(len(tabIdQuestions)):
                # insertion des données dans la table
                cur.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?,?);",
                            (sequenceId, tabIdQuestions[i]))
                con.commit()

            # Fermeture de la connection
            cur.close()
            con.close()
            return 0
        except sqlite3.Error as error:
            print("Échec de la modification de l'élément dans la table sqlite", error)
            return 1
    else:
        return 2

    # 0 si réussite
    # 1 si échec de la requête
    # 2 si la sequence n'est pas trouvée


def removeSequence(sequenceId):
    # Si la séquence existe
    if getEnseignant(sequenceId):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Suppression des données dans la table (update on cascade supprime les liens)
            cur.execute("DELETE FROM Sequences WHERE id = ?;", (sequenceId,))
            con.commit()

            # Fermeture de la connection
            cur.close()
            con.close()
            return 0
        except sqlite3.Error as error:
            print("Échec de la suppression de l'élément dans la table sqlite", error)
            return 1
    else:
        return 2

    # 0 si réussite
    # 1 si échec de la requête
    # 2 si la sequence n'est pas trouvée
