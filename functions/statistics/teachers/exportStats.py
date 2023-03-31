import sqlite3

# Retourne un dictionnaire de dictionnaires contenant toutes les statistiques d'un enseignant
# Param : - enseignant : id de l'enseignant (int)
# Return : un dictionnaire
def exportStatistics(enseignant):
    list_diffusions = exportDiffusions(enseignant)
    list_questions = exportQuestions(enseignant)
    list_reponses = exportReponses(enseignant)

    # S'il y eu une erreur lors d'un des appels des fonctions, on retourne False
    if not list_questions or not list_questions or not list_reponses:
        return False
    else:
        return {
            "diffusions": list_diffusions,
            "questions": list_questions,
            "reponses": list_reponses
        }


# Retourne un dictionnaire contenant toutes les diffusions d'un enseignant (table ArchivesDiffusions)
# Param : - enseignant : id de l'enseignant (int)
# Return : un dictionnaire
def exportDiffusions(enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # On récupère toutes les archives des diffusions de l'enseignant (table ArchivesDiffusions)
        cursor.execute("SELECT id, date, mode, code, titre FROM ArchivesDiffusions WHERE enseignant = ?;",
                       (enseignant,))
        results = cursor.fetchall()

        # On initialise un dictionnaire vide avec des listes vides pour chaque clé
        result_dict = {col[0]: [] for col in cursor.description}

        # On parcourt chaque tuple dans la liste de résultats
        for row in results:
            # Parcourez chaque élément du tuple, en utilisant le nom de colonne comme clé
            for i, value in enumerate(row):
                col_name = cursor.description[i][0]

                # On vérifie si la colonne "mode" vaut 0 ou 1 et on remplace la valeur correspondante
                if col_name == "mode":
                    if value == 1:
                        value = "sequence"
                    elif value == 0:
                        value = "question"
                result_dict[col_name].append(value)

        return result_dict

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False


# Retourne un dictionnaire contenant toutes les questions des diffusions d'un enseignant (table ArchivesReponses)
# Param : - enseignant : id de l'enseignant (int)
# Return : un dictionnaire
def exportQuestions(enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # On récupère toutes les archives des diffusions de l'enseignant (table ArchivesDiffusions)
        cursor.execute("SELECT Questions.* FROM ArchivesQuestions AS Questions \
                            INNER JOIN ArchivesDiffusions AS Diffusions on Questions.diffusion = Diffusions.id \
                            WHERE Diffusions.enseignant = ?;", (enseignant,))
        results = cursor.fetchall()

        # On initialise un dictionnaire vide avec des listes vides pour chaque clé
        result_dict = {col[0]: [] for col in cursor.description}

        # On parcourt chaque tuple dans la liste de résultats
        for row in results:
            # Parcourez chaque élément du tuple, en utilisant le nom de colonne comme clé
            for i, value in enumerate(row):
                col_name = cursor.description[i][0]

                # On vérifie si la colonne "type" vaut 0, 1 ou 2 et on remplace la valeur correspondante
                if col_name == "type":
                    if value == 0:
                        value = "qcm"
                    elif value == 1:
                        value = "numerique"
                    elif value == 2:
                        value = "libre"
                result_dict[col_name].append(value)

        return result_dict

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False


# Retourne un dictionnaire contenant toutes les réponses des diffusions d'un enseignant (table ArchivesReponses)
# Param : - enseignant : id de l'enseignant (int)
# Return : un dictionnaire
def exportReponses(enseignant):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # On récupère toutes les archives des diffusions de l'enseignant (table ArchivesDiffusions)
        cursor.execute("SELECT Reponses.* FROM ArchivesReponses AS Reponses \
                    INNER JOIN ArchivesQuestions AS Questions on Reponses.question = Questions.id \
                    INNER JOIN ArchivesDiffusions AS Diffusions on Questions.diffusion = Diffusions.id \
                    WHERE Diffusions.enseignant = ?;", (enseignant,))
        results = cursor.fetchall()

        # On initialise un dictionnaire vide avec des listes vides pour chaque clé
        result_dict = {col[0]: [] for col in cursor.description}

        # On parcourt chaque tuple dans la liste de résultats
        for row in results:
            # Parcourez chaque élément du tuple, en utilisant le nom de colonne comme clé
            for i, value in enumerate(row):
                col_name = cursor.description[i][0]

                # On vérifie si la colonne "type" vaut 0, 1 ou 2 et on remplace la valeur correspondante
                if col_name == "date":
                    value = round(value)

                if col_name == "est_correcte":
                    if value == 1:
                        value = True
                    elif value == 0:
                        value = False
                result_dict[col_name].append(value)

        return result_dict

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélection des statistiques :", error)
        return False
