import sqlite3


# Fonction qui renvoie un tableau contenant tous les utilisateurs du site
def getUsers():
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Selection de tous les utilisateurs
    res = cur.execute("SELECT * FROM users")
    res = res.fetchall()

    # Fermeture de la connection
    cur.close()
    con.close()
    return res


# Fonction qui renvoie un tableau contenant un utilisateur du site selon son id
def getUser(userId):
    # Connection à la table
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Selection de l'utilisateur selon son id
    res = cur.execute("SELECT * FROM users WHERE id=?", (userId,))
    res = res.fetchall()

    # Fermeture de la connection
    cur.close()
    con.close()
    return res


# Fonction qui permet d'ajouter un nouvel utilisateur sur le site
def addUser(nom, prenom, password):
    try:
        # Connection à la table
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Insertion des données dans la table
        sql = """INSERT INTO users
                (nom, prenom, password) 
                VALUES (?, ?, ?);"""
        data = (nom, prenom, password)
        cur.execute(sql, data)
        con.commit()

        # Fermeture de la connection
        cur.close()
        con.close()
        return True
    except sqlite3.Error as error:
        print("Échec de l'insertion de la variable Python dans la table sqlite", error)
        return False
