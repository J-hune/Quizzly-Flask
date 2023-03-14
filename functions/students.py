import sqlite3
from werkzeug.security import generate_password_hash


# Ajoute les étudiants en paramètre dans la BDD
# Param : tableau d'étudiant sous cette forme
#           [{"id" : 1332214, "nom":"DeLaTour", "prenom":"Jean"},
#            {"id" : 1322324, "nom":"DeLaTour", "prenom":"Jeanne"}, ...
#           ]
# Return : le nombre d'étudiants ajoutés dans la BDD (int)
def addStudent(students):
    nb_student_added = 0

    # Pour chaque étudiant
    for i in range(len(students)):
        try:
            # Connection à la BDD
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Chiffrage du mot de passe
            hashed_password = generate_password_hash(students[i]["id"], 'sha256')

            # Insertion de l'étudiant
            cursor.execute("INSERT or IGNORE INTO Etudiants (id, nom, prenom, mdp) VALUES (?, ?, ?, ?);",
                           (students[i]["id"],
                            students[i]["nom"],
                            students[i]["prenom"],
                            hashed_password))
            conn.commit()

            # Si le dernier élément inséré a le même id que l'étudiant actuel, l'étudiant a réellement été ajouté,
            # sinon l'étudiant était donc déjà dans la BDD
            if cursor.lastrowid == int(students[i]["id"]):
                nb_student_added += 1

            # Fermeture de la connection
            cursor.close()
            conn.close()

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de l'ajout des étudiants :", error)
            return -1

    return nb_student_added


# Retourne les informations sur l'étudiant en paramètre
# Param : numéro de l'étudiant
# Return : un dico sous la forme suivante
#           {
#               "prenom": "Ada",
#               "nom": "Lovelace",
#               "avatar": ""data:image/png;base64,iVBORw0KGgo..."
#           }
def getStudent(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Selection des données dans la table
        cursor.execute("SELECT nom, prenom, avatar FROM Etudiants WHERE id = ?;", (id,))
        result = cursor.fetchone()

        # Si l'étudiant n'est pas trouvé
        if not result:
            return False

        dico = {
            "nom": result[0],
            "prenom": result[1],
            "avatar": result[2]
        }

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return dico

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'étudiant :", error)
        return False


# Retourne tous les étudiants de la BDD
# Return : tableau de dico d'étudiant sous la forme suivante
#           [
#             {
#               "id": 42,
#               "prenom": "John",
#               "nom": "Smith",
#               "avatar": "data:image/png;base64,iVBORw0KGgo..."
#              }, ...
#           ]
def getAllStudents():
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère l'id, le nom, le prénom et l'avatar de chaque étudiant dans la BDD
        cursor.execute("SELECT Etudiants.id, Etudiants.nom, Etudiants.prenom, Etudiants.avatar FROM Etudiants;")
        result = cursor.fetchall()

        # Ordonne les données dans un tableau de dico
        data = []
        for i in range(len(result)):
            dico = {
                "id": result[i][0],
                "nom": result[i][1],
                "prenom": result[i][2],
                "avatar": result[i][3]
            }
            data.append(dico)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des étudiants :", error)
        return False


# Modifie le mot de passe d'un étudiant
# Param : - id : id de l'étudiant (int)
#         - password : nouveau mot de passe de l'étudiant (string)
def changePassword(id, password):
    try:
        # On chiffre le mot de passe
        hashed_password = generate_password_hash(password, 'sha256')

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Mise à jour des données dans la table
        cursor.execute("UPDATE Etudiants SET mdp = ? WHERE id = ?;", (hashed_password, id))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la modification du mot de passe :", error)
        return False


# Modifie l'avatar de l'étudiant en paramètre
# Param : - id : id de l'étudiant (int)
#         - avatar : nouvel avatar de l'étudiant (string)
def editAvatar(id, avatar):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Mise à jour de la donnée dans la table
        cursor.execute("UPDATE Etudiants SET avatar = ? WHERE id = ?;", (avatar, id))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la modification de l'avatar :", error)
        return False


# Retourne l'avatar de l'étudiant en paramètre
# Param : id de l'étudiant (int)
def getAvatar(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Mise à jour de la donnée dans la table
        result = cursor.execute("SELECT avatar FROM Etudiants WHERE id = ?;", (id,))
        result = result.fetchone()
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        if result:
            return result[0]
        return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'avatar :", error)
        return False


# Supprime l'étudiant en paramètre de la BDD
# Param : id de l'étudiant (int)
# Return : 0 si réussite
#          1 si échec de la requête
#          2 si l'étudiant n'est pas trouvé
def removeStudent(id):
    # Vérifie si l'étudiant existe
    if getStudent(id):
        try:
            # Connection à la BDD
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Active les clés étrangères
            cursor.execute("PRAGMA foreign_keys = ON")

            # Suppression des données dans la table
            cursor.execute("DELETE FROM Etudiants WHERE id = ?;", (id,))
            conn.commit()

            # Fermeture de la connection
            cursor.close()
            conn.close()
            return 0

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la suppresion de l'étudiant :", error)
            return 1
    else:
        return 2


# Supprime tous les étudiants de la BDD
def removeAllStudents():
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Activation des clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Suppression de toutes les données dans la table
        cursor.execute("DELETE FROM Etudiants;")
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression de tous les étudiants :", error)
        return False


# Renvoie les infos de l'étudiant s'il existe en BDD et l'ajoute en session si tel est le cas
# Param : - student_id : le numéro étudiant de l'étudiant (string)
#         - password : mot de passe de l'étudiant (string)
# Return : les infos de l'étudiant (dico) ou False
#               {
#                "id": "1",
#                "firstname": "Donovann",
#                "surname": "Zassot",
#                "type": "Enseignant"
#               }
def studentExists(student_id, password):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupère tous les étudiants qui ont ce couple nom/prénom
        cursor.execute("SELECT * FROM Etudiants WHERE id = ?;", (student_id,))
        result = cursor.fetchone()

        # Si le condensat correspond au mot de passe
        if check_password_hash(result[3], password):
            session["user"] = {
                'id': result[0],
                'firstname': result[2],
                'surname': result[1],
                'type': "Etudiant"
            }
            # session.permanent = True ????? (au-dessus c'est pas commenté, pourquoi ?)
            return {**session["user"], "avatar": result[4]}

        # Fermeture de la connection
        conn.commit()
        conn.close()
        return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'étudiant :", error)
        return False
