import sqlite3


# teste si l'étudiant existe dans la base de donnée
def getEtu(studentId):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Selection des données dans la table
        cur.execute("SELECT nom, prenom FROM Etudiants WHERE id = ?;", (studentId,))
        res = cur.fetchall()

        # Fermeture de la connection
        cur.close()
        con.close()

        if len(res) == 0:
            return False
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


# ajoute les étudiants dans la base de donnée
# Reçois des données sous cette forme :
# [{"id" : 1332214, "nom":"DeLaTour", "prenom":"Jean"},
# {"id" : 1322324, "nom":"DeLaTour", "prenom":"Jeanne"},
# ]
def addStudent(ListeDeDictionnaire):
    nbStudentAdd = 0

    # Pour chaque étudiant
    for i in range(len(ListeDeDictionnaire)):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Insertion des données dans la table
            sql = "INSERT or IGNORE INTO Etudiants (id, nom, prenom, mdp) VALUES (?, ?, ?, ?);"
            data = (ListeDeDictionnaire[i]["id"],
                    ListeDeDictionnaire[i]["nom"],
                    ListeDeDictionnaire[i]["prenom"],
                    ListeDeDictionnaire[i]["id"])
            cur.execute(sql, data)
            con.commit()

            # Si le dernier element inséré, a le meme id que l'étudiant actuel on l'a réellement ajouté
            if cur.lastrowid == int(ListeDeDictionnaire[i]["id"]):
                nbStudentAdd += 1

            # Fermeture de la connection
            cur.close()
            con.close()
        except sqlite3.Error as error:
            print("Échec de l'insertion de la variable Python dans la table sqlite", error)
            return -1
    return nbStudentAdd


# Retourne tous les étudiants de la BDD sous cette forme :
# [
#   {
#      "id": 42,
#      "nom": "Smith",
#      "prenom": "John",
#      "avatar": "data:image/png;base64,iVBORw0KGgo..."
#    }, ...
# ]
def getStudents():
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    cur.execute("SELECT Etudiants.id, Etudiants.nom, Etudiants.prenom, Etudiants.avatar FROM Etudiants")
    res = cur.fetchall()

    data = []
    for i in range(len(res)):
        dico = {
            "id": res[i][0],
            "nom": res[i][1],
            "prenom": res[i][2],
            "avatar": res[i][3]
        }
        data.append(dico)

    # Fermeture de la connection
    cur.close()
    con.close()

    return data


def changePassword(NumEtudiant, password):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Mise à jour des données dans la table
        cur.execute("UPDATE Etudiants SET mdp = ? WHERE id = ?;", (password, NumEtudiant))
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


# Modifie l'avatar d'un étudiant
def editAvatar(NumEtudiant, avatar):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Mise à jour de la donnée dans la table
        cur.execute("UPDATE Etudiants SET avatar = ? WHERE id = ?;", (avatar, NumEtudiant))
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True

    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False


# removeStudent renvoie :
#  0 si bon
#  1 si mauvaise requete
#  2 si l'étudiant n'est pas trouvé
def removeStudent(studentId):
    # Si l'étudiant existe
    if getEtu(studentId):
        try:
            # Connection à la table
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            # Suppression des données dans la table
            cur.execute("DELETE FROM Etudiants WHERE id = ?;", (studentId,))
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


def removeAllStudent():
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Suppression de toutes les données dans la table
        cur.execute("DELETE FROM Etudiants;")
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de la suppression de l'élément dans la table sqlite", error)
        return False
