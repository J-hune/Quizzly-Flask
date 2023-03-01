import sqlite3


def getEnseignant(idSequence):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Selection des données dans la table
        result = cur.execute("SELECT enseignant FROM Sequences WHERE id = ?;", (idSequence,))

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


def addSequence(enseignantId, TabIdQuestions):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # insertion des données dans la table
        cur.execute("INSERT INTO Sequences (enseignant) VALUES (?);", (enseignantId, ))

        # Récupère la clé primaire de cette sequence
        SequencesId=cur.lastrowid

        # Pour chaque question
        for i in range(len(TabIdQuestions)):

            # insertion des données dans la table
            cur.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?,?);", (SequencesId, TabIdQuestions[i]))
            con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


def editSequence(SequenceId, TabIdQuestions):

    # Si la sequence existe
    if getEnseignant(SequenceId):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Suppression des données dans la table
            cur.execute("DELETE FROM liensSequencesQuestions WHERE idSequence = ?;", (SequenceId,))
            con.commit()

            # pour chaque question
            for i in range(len(TabIdQuestions)):
                # insertion des données dans la table
                cur.execute("INSERT or IGNORE INTO liensSequencesQuestions (idSequence, idQuestion) VALUES (?,?);",
                            (SequenceId, TabIdQuestions[i]))
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
    #  0 si bon
    #  1 si mauvaise request
    #  2 si la sequence n'est pas trouvé


def removeSequence(SequenceId):

    # Si la sequence existe
    if getEnseignant(SequenceId):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Suppression des données dans la table
            cur.execute("DELETE FROM liensSequencesQuestions WHERE idSequence = ?;", (SequenceId,))
            con.commit()
            cur.execute("DELETE FROM Sequences WHERE id = ?;", (SequenceId,))
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
    #  0 si bon
    #  1 si mauvaise request
    #  2 si la sequence n'est pas trouvé