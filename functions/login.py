import sqlite3
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

# Ajoute l'utilisateur en session et en base de donnée
def registerUser(firstname, surname, password, userType):
    firstname = firstname.strip()
    surname = surname.strip()
    password = password.strip()

    # Génération du condensat du mot de passe avec l'algo sha256
    hashedPassword = generate_password_hash(password, 'sha256')

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Ajout de l'utilisateur en bdd
    dataToInsert = (surname, firstname, hashedPassword)
    sql = "INSERT INTO " + userType + "(nom, prenom, mdp) VALUES(?,?,?)"
    cursor.execute(sql, dataToInsert)
    connection.commit()

    # Ajout de l'utilisateur en session
    session["user"] = {
        'id': cursor.lastrowid,
        'firstname': firstname,
        'surname': surname,
        'type': userType
    }
    session.permanent = True

    connection.close()


# Vérifie si l'utilisateur existe et retourne un booleen selon le cas
# Si oui, l'utilisateur est ajouté en session
def userExists(firstname, surname, password, userType):
    firstname = firstname.strip()
    surname = surname.strip()
    password = password.strip()

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Récupérations de tous les utilisateurs qui ont ce couple nom prénom
    dataToInsert = (surname, firstname)
    sql = "SELECT * FROM " + userType + " WHERE nom = ? AND prenom = ?"
    cursor.execute(sql, dataToInsert)

    # Pour chaque utilisateur
    rows = cursor.fetchall()
    for i in rows:
        # Si le condensat correspond au mot de passe
        if check_password_hash(i[3], password):
            session["user"] = {
                'id': i[0],
                'firstname': i[2],
                'surname': i[1],
                'type': userType
            }
            session.permanent = True
            return True
    connection.commit()

    connection.close()
    return False