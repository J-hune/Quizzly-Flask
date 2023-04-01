import sqlite3


# Renvoie les 3 dernières diffusions auxquelles un étudiant a participé
# (sauf les diffusions avec que des questions ouvertes)
# Param : id de l'étudiant
# Return : les trois dernières diffusions de l'étudiant (tab de dico)
#               [{"code":"A2dt8g6B",
#                 "titre":"Mathématiques",
#                 "enseignant":"Michel Staelens",
#                 "participants":25,
#                 "pourcentage":"82,7",             (--> pourcentage de réussite de l'étudiant)
#                 "date":07032023
#                 }, ...]
def getLastSequences(id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Active les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        # Récupère l'id des 3 dernières séquences participé, le nom/prénom du prof et le pourcentage de bonne réponse
        #                                                                           nbRéponse     nbBonneRéponse
        result = cursor.execute("SELECT AD.id, AD.code, AD.titre, E.prenom, E.nom, COUNT(AR.id), SUM(AR.est_correcte), AD.date \
                                            FROM ArchivesDiffusions AD \
                                            JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                            JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                            JOIN Enseignants E ON AD.enseignant = E.id \
                                            WHERE AR.etudiant = ? AND AD.mode = 1 AND AQ.type != 2 \
                                            GROUP BY AD.id, AR.etudiant \
                                            ORDER BY AD.date DESC LIMIT 3;", (id,))
        result = result.fetchall()

        # Ordonne les données dans un tableau pour chaque séquence
        tab = []
        for i in range(len(result)):
            # Récupère le nombre de participants à la diffusion
            nb_participant = cursor.execute("SELECT COUNT(DISTINCT AR.etudiant) \
                                            FROM ArchivesDiffusions AD \
                                            JOIN ArchivesQuestions AQ ON AD.id = AQ.diffusion \
                                            JOIN ArchivesReponses AR ON AQ.id = AR.question \
                                            WHERE AD.id = ?;", (result[i][0],))
            nb_participant = nb_participant.fetchone()

            # Range les données dans un dico
            data = {"code": result[i][1],
                    "titre": result[i][2],
                    "enseignant": result[i][3] + " " + result[i][4],
                    "participants": nb_participant[0],
                    "pourcentage": ((result[i][6] / result[i][5]) * 100),
                    "date": result[i][7]
                    }
            tab.append(data)

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return tab

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des dernières séquences :", error)
        return 0
