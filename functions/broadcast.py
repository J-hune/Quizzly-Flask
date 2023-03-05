import sqlite3
import string
import random


# Vérifie si le code existe déjà dans la BDD
def codeAlreadyExists(cursor, code):
    cursor.execute("SELECT id FROM Codes WHERE id=?;", (code,))
    result = cursor.fetchone()
    return result is not None


# Génère un code de 8 caractères alphanumérique qui n'est pas encore utilisé
def generateCode():
    try:
        # Connection à la table
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
        print("Échec de l'insertion de l'élément dans la table sqlite : ", error)
        return False

    # Supprime un code de la BDD


# Libère le code
def deleteCode(code):
    try:
        # Connection à la table
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
        print("Échec de la suppression de l'élément dans la table sqlite : ", error)
        return False
