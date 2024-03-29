import sqlite3
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash


# Ajoute l'enseignant en session et en base de donnée
# Param : - firstname : prénom de l'enseignant (string)
#         - surname : nom de l'enseignant (string)
#         - password : mot de passe de l'enseignant (string)
# Return : les infos de l'enseignant (dico) ou False si échec de la requête
#               {"id": 0,
#                "firstname": "Livio",
#                "surname": "Nortes-Bousquet",
#                "type": "Enseignant"}
def registerTeacher(firstname, surname, password):
    try:
        # On enlève les espaces
        firstname = firstname.strip()
        surname = surname.strip()

        # Génération du condensat du mot de passe avec l'algo sha256
        hashed_password = generate_password_hash(password, 'sha256')

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Ajout de l'enseignant en BDD
        cursor.execute("INSERT INTO Enseignants (nom, prenom, mdp) VALUES(?, ?, ?);", (surname, firstname, hashed_password))
        conn.commit()

        # Ajout de l'utilisateur en session
        session["user"] = {
            'id': cursor.lastrowid,
            'firstname': firstname,
            'surname': surname,
            'type': "Enseignant"
        }
        session.permanent = True

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return session["user"]

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion de l'enseignant :", error)
        return 0


# Renvoie les infos de l'enseignant s'il existe en BDD et l'ajoute en session si tel est le cas
# Param : - firstname : prénom de l'enseignant (string)
#         - surname : nom de l'enseignant (string)
#         - password : mot de passe de l'enseignant (string)
# Return : les infos de l'enseignant (dico) ou False si échec de la requête
#               {"id": "1",
#                "firstname": "Donovann",
#                "surname": "Zassot",
#                "type": "Enseignant"}
def teacherExists(firstname, surname, password):
    try:
        # On enlève les espaces
        firstname = firstname.strip()
        surname = surname.strip()

        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupérations de tous les enseignants qui ont ce couple nom prénom
        cursor.execute("SELECT * FROM Enseignants WHERE nom = ? AND prenom = ?;", (surname, firstname))
        result = cursor.fetchall()

        # Pour chaque enseignant
        for i in result:
            # Si le condensat correspond au mot de passe
            if check_password_hash(i[3], password):
                session["user"] = {
                    'id': i[0],
                    'firstname': i[2],
                    'surname': i[1],
                    'type': "Enseignant"
                }
                session.permanent = True
                return session["user"]
        conn.commit()  # ?????

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return False

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection de l'enseignant :", error)
        return False
