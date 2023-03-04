import sqlite3

from functions.broadcast import generateCode
from functions.fonctionLabels import getLiensEtiquettes


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


def getSequence(sequenceId):
    # Si la séquence existe
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        result = {}
        # Suppression des données dans la table (update on cascade supprime les liens)
        resultRequetes = cur.execute("""SELECT id, titre, idQuestion FROM Sequences
                            JOIN liensSequencesQuestions ON Sequences.id=liensSequencesQuestions.idSequence
                             WHERE id=?""", (sequenceId, ))

        resultRequetes = resultRequetes.fetchall()
        con.commit()
        # Fermeture de la connection
        cur.close()
        con.close()

        if resultRequetes:
            # On récupère l'id
            result["id"] = resultRequetes[0][0]
            # On récupère que le titre
            result["titre"] = resultRequetes[0][1]
            # On crée un tableau pour les questions
            result["questions"] = []
            for i in range(len(resultRequetes)):
                # On ajoute les id de chaque question
                result["questions"].append(resultRequetes[i][2])
            return result
        else:
            return False
    except sqlite3.Error as error:
        print("Échec de la selection de l'élément dans la table sqlite", error)
        return False


def getAllSequences(idEnseignant):
    # Si la séquence existe
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Suppression des données dans la table (update on cascade supprime les liens)
        resultRequetes = cur.execute("""SELECT id, titre FROM Sequences WHERE enseignant=?""", (idEnseignant,))

        resultRequetes = resultRequetes.fetchall()

        if resultRequetes:
            result = []
            for k in range(len(resultRequetes)):
                dicoResult = {}

                # On récupère l'id
                dicoResult["id"] = resultRequetes[k][0]
                # On récupère que le titre
                dicoResult["titre"] = resultRequetes[k][1]

                # Tableau qui contient les etiquettes
                listeEtiquettes = []
                # Tableau qui contient les noms des etiquettes deja ajouté pour pas de doublon
                listeEtiquettesNomAjouté = []

                # Requetes SQL pour récupérer les id des questions de la sequence
                resultRequetesQuestion = cur.execute("""SELECT idQuestion FROM liensSequencesQuestions WHERE idSequence=?""", (dicoResult["id"],))
                resultRequetesQuestion = resultRequetesQuestion.fetchall()
                # On crée un tableau pour les questions
                dicoResult["questions"] = []
                for i in range(len(resultRequetesQuestion)):
                    # On ajoute les id de chaque question
                    dicoResult["questions"].append(resultRequetesQuestion[i][0])

                    # Appel a la fonction pour récupérer toutes les étiquettes associés a la question
                    listeEtiquettesQuestions = getLiensEtiquettes(resultRequetesQuestion[i][0], idEnseignant)
                    for j in range(len(listeEtiquettesQuestions)):
                        # On ajoute les étiquettes que si on ne les a pas
                        if not (listeEtiquettesQuestions[j]["nom"] in listeEtiquettesNomAjouté):
                            listeEtiquettesNomAjouté.append(listeEtiquettesQuestions[j]["nom"])
                            listeEtiquettes.append(listeEtiquettesQuestions[j])
                dicoResult["listeEtiquettes"] = listeEtiquettes
                # On ajoute notre beau dico au tableau
                result.append(dicoResult)
            con.commit()
            # Fermeture de la connection
            cur.close()
            con.close()
            return result
        else:

            con.commit()
            # Fermeture de la connection
            cur.close()
            con.close()
            return False
    except sqlite3.Error as error:
        print("Échec de la selection de l'élément dans la table sqlite", error)
        return False
