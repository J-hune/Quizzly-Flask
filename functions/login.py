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
        'type': "Enseignant" if userType == "Enseignants" else "Etudiant"
    }
    session.permanent = True

    connection.close()


# Vérifie si l'enseignant existe et retourne un objet ou un booleen selon le cas
# Si oui, l'enseignant est ajouté en session
def teacherExists(firstname, surname, password):
    firstname = firstname.strip()
    surname = surname.strip()
    password = password

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Récupérations de tous les utilisateurs qui ont ce couple nom prénom
    dataToSelect = (surname, firstname)
    sql = "SELECT * FROM Enseignants WHERE nom = ? AND prenom = ?"
    cursor.execute(sql, dataToSelect)

    # Pour chaque utilisateur
    rows = cursor.fetchall()
    for i in rows:
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
    connection.commit()

    connection.close()
    return False


# Vérifie si l'enseignant existe et retourne un objet ou un booleen selon le cas
# Si oui, l'enseignant est ajouté en session
def studentExists(studentID, password):
    studentID = studentID
    password = password

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Récupérations de tous les utilisateurs qui ont ce couple nom prénom
    sql = "SELECT * FROM Etudiants WHERE id = ?"
    cursor.execute(sql, (studentID,))

    # Pour chaque utilisateur
    rows = cursor.fetchall()
    for i in rows:
        # Si le condensat correspond au mot de passe
        if check_password_hash(i[3], password):
            session["user"] = {
                'id': i[0],
                'firstname': i[2],
                'surname': i[1],
                'type': "Etudiant"
            }
            session.permanent = True
            return session["user"]
    connection.commit()

    connection.close()
    return False
