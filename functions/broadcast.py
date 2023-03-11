import sqlite3
import string
import random


# Vérifie si le code existe déjà dans la BDD
# Param : - cursor : le cursor de la BDD
#         - code : le code alphanumérique généré (string)
# Return : True si code existe déjà sinon False
def codeAlreadyExists(cursor, code):
    try:
        cursor.execute("SELECT id FROM Codes WHERE id=?;", (code,))
        result = cursor.fetchone()
        return result is not None

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection du code :", error)
        return False


# Génère un code de 8 caractères alphanumérique qui n'est pas encore utilisé
# Return : le code alphanumérique (string)
def generateCode():
    try:
        # Connection à la BDD
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Génère un code aléatoire de 8 caractères alphanumériques
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Tant que le code existe déjà dans la BDD, en générer un nouveau
        while codeAlreadyExists(cursor, code):
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Insère le code dans la base de données
        cursor.execute("INSERT INTO Codes (id) VALUES (?);", (code,))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return code

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de l'insertion du code :", error)
        return False


# Libère le code (le supprime de la BDD)
# Param : le code à libérer (string)
def deleteCode(code):
    try:
        # Connection à la BDD
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Supprime le code de la BDD
        cursor.execute("DELETE FROM Codes WHERE id=?;", (code,))
        conn.commit()

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return True

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la suppression du code :", error)
        return False
