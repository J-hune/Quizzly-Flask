import sqlite3


# Supprime l'étiquette donnée en paramètre dans la base de donnée
def supprLabel(nomLabel):
    if searchLabel(nomLabel):
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            sql = 'DELETE FROM etiquettes WHERE nom = ?'
            value = nomLabel
            cur.execute(sql, (value,))
            con.commit()
            print("L'étiquette a été supprimée!")

            cur.close()
            con.close()
            return True


        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la suppression !", error)
            return False
    else:
        return False


# Vérifie si l'étiquette donnée en paramètre est dans la base de donnée
def searchLabel(nomLabel):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        sql = 'SELECT * FROM etiquettes WHERE nom= ?'
        value = nomLabel
        cur.execute(sql, (value,))
        con.commit()
        print("Cette étiquette existe déjà !")

        cur.close()
        con.close()
        return True


    except sqlite3.Error as error:
        print("Une erreur est survenue ou l'étiquette n'existe pas !", error)
        return False


# Ajoute une étiquette avec une couleur choisie dans la base de donnée
def addLabel(nomLabel, couleur):
    if not searchLabel(nomLabel):
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            sql = 'INSERT INTO etiquettes VALUES(?,?)'
            value = (nomLabel, couleur)
            cur.execute(sql, value)
            con.commit()
            print("Etiquette créée !")

            cur.close()
            con.close()
            return True

        except sqlite3.Error as error:
            print("Une erreur est survenue lors de la création de l'étiquette!", error)
            return False
    else:
        return False
