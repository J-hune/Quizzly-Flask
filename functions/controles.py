import sqlite3
from copy import deepcopy
from math import factorial
from random import shuffle


# Fonction qui retourne toutes les combinaisons (ou jusqu'à la limite) du tableau de tableaux entrer en paramètre
# Param : tableaux : tableaux de tableaux avec des valeurs : [[...],[...],...]
#         limite : la limite du tableau pour ne pas avoir un trop gros tableau
# Renvoie un tableau avec les combinaisons souhaité
def combinaisons_tableaux(tableaux, limite = 500000):
    resultats = [[]]
    i = 0

    # Boucles qui font toutes les combinaisons des valeurs entre les tablaux
    for t in tableaux:
        i += 1
        nouvelles_combinaisons = []
        for r in resultats:
            i += 1
            for e in t:
                i += 1
                nouvelles_combinaisons.append(r + [e])

            # Si on est à la dernière boucle (on est en train de faire la combinaison avec le dernier tableau)
            # et que l'on atteint la limite, on renvoie nos données (pour éviter de faire un tableau trop grand
            # si on veut que les premières valeurs
            if len(nouvelles_combinaisons[0]) == len(tableaux) and len(nouvelles_combinaisons) > limite:
                return nouvelles_combinaisons

        resultats = nouvelles_combinaisons
    return resultats

# Param : intervalle : [{"max":nombre de question de l'étiquette, "value":[2,5]L'intervalle},{...},...]
#         nb_question : nombre de questions que l'on veut par sujet
#         nb_sujet : nombre de sujets que l'on désire au total
# Renvoie : Si nb_combinaison_total >= nb_sujet
#               un tableau de tableau
#                   avec en indice 0 :
#                               un tableau de tableau qui contient toutes les configurations qui résout
#                               nb question de la configuration == nb question que l'on veut
#                   avec en indice 1 :
#                               un tableau des combinaisons possibles avec la configuration i
#                   avec en indice 2 :
#                               un tableau du nombre de questions maximum associé à chaque étiquette
#       Sinon :
#       renvoie un tuple avec un code erreur et un chiffre :
#                       si on demande trop de question et le chiffre correspond au nombre max de question
#                       1 on demande trop de sujet et le chiffre correspond au nombre max de sujet
def systemeARes(intervalle, nb_question, nb_sujet):
    tableau_intervalle = []  # Tableau "étaler" des intervalles de [1,5] donne [1,2,3,4,5]
    result = []  # Tableau qui contient les bonnes combinaisons qui correspond au bon nb de question et nb de sujet
    result_combi = []  # Tableau qui contient le nombre de solutions de chaque sujet
    intervalle_max_value = []  # Tableau avec le nombre max de question de chaque étiquette
    nombre_question_minimum = 0
    # Boucle pour "étaler les intervalles" : de [1,5] donne [1,2,3,4,5]
    # et les insère dans tableau_intervalle
    for i in range(len(intervalle)):
        tableau_intervalle.append([])
        intervalle_max_value.append(intervalle[i]["max"])
        for j in range(intervalle[i]["value"][0], intervalle[i]["value"][1]+1):
            tableau_intervalle[i].append(j)
        nombre_question_minimum += intervalle[i]["value"][0]

    # Appel a combinaison_tableaux pour avoir toutes les combinaisons de sujets possibles
    tableau_combinaison = combinaisons_tableaux(tableau_intervalle)
    # Boucle pour parcourir ce tableau
    nb_combinaison_total = 0
    nb_question_combinaison = 0
    for i in range(len(tableau_combinaison)):
        nb_question_combinaison = 0
        nb_combinaison = 1


        # Boucle qui parcourt chaque valeur d'une combinaison
        for j in range(len(tableau_combinaison[i])):
            nb_question_combinaison += tableau_combinaison[i][j]
            nb_combinaison *= factorial(intervalle[j]["max"])/(factorial(tableau_combinaison[i][j])*factorial(intervalle[j]["max"]-tableau_combinaison[i][j]))

        # Si la combinaison a le bon nombre de questions et que l'on peut faire égale ou plus que le
        # nb_sujet en faisant toutes les combinaisons de question avec cette combinaison de sujet

        if nb_question_combinaison == nb_question:
            result.append(tableau_combinaison[i])
            result_combi.append(nb_combinaison)
            nb_combinaison_total += nb_combinaison
    if nb_combinaison_total >= nb_sujet:
        return [result, result_combi, intervalle_max_value]
    else:
        return 0, nb_combinaison_total, [nombre_question_minimum, nb_question_combinaison]


# Definition :
#           Configuration : pour désigner une configuration d'un sujet par exemple
#                           3 questions de python, 2 questions de php est une configuration
#                           2 questions de python et 3 questions de php en est une autre
# Fonction qui choisi le nombre de solutions que l'on veut avec les différentes configurations des questions
# Param : result_systeme : un tableau de tableau qui contient en [0] une configuration qui a le bon nombre de questions
#                          et qui peut faire le nb_sujet et le nb de combinaiqon de chaque configuration [[...][...]]
#                           (tableau renvoyer par systemeARes)
#         nb_sujet : nombre de sujets souhaité
# Renvoie : un tableau contenant result_systeme réduit au nombre de sujets
#           et les choix que l'on veut pour chaque configuration
def choixDesSolutionsDansLeSysteme(result_systeme, nb_sujet):
    # Si notre nombre de configurations différentes de sujet est égale au nb_sujet
    # on prend que 1 solution de chaque configuration
    if len(result_systeme[0]) == nb_sujet:
        return [result_systeme, [1 for i in range(len(result_systeme[0]))]]

    # Sinon, on va étaler nos choix de configuration sur tout le tableau
    else:
        longueur_tab_choix = len(result_systeme[0])
        # On crée un tableau qui a pour taille le nombre de sujets, remplit de 0
        tab_choix = [0 for i in range(longueur_tab_choix)]

        nb_sujet_choisi = 0  # Variable pour compter le nombre de sujets que l'on a déjà choisi
        j = 0  # Indice qui varie dans tout le tableau pour étaler le choix des configurations

        # Boucle pour étaler les choix
        while nb_sujet_choisi<nb_sujet:
            # Si on n'a pas atteint le nombre de possibilités de cette configuration
            if tab_choix[j] != result_systeme[1][j]:
                tab_choix[j] += 1
                nb_sujet_choisi += 1

            # Pour ne jamais dépasser la taille du tableau de choix
            j = (j+1) % longueur_tab_choix

        # On réduit les tableaux au nombre de sujets pour éviter d'avoir les possibilités pas sélectionner pour la suite
        tab_choix = tab_choix[:nb_sujet]
        result_systeme[0] = result_systeme[0][:nb_sujet]
        result_systeme[1] = result_systeme[1][:nb_sujet]
        return [result_systeme, tab_choix]


# Fonction qui retourne toutes les combinaisons pour un etiquette ou s'arrête à la combinaison : nb_sujet
# (stop à la 10eme combinaison si nb_sujet = 10)
# Param : p : un entier (le p de p parmi n)
#         n : un entier (le n de p parmi n)
#         nb_sujet : le nb de sujet différent que l'on veut
def combinaisons_v1(p, n, nb_sujet):
    liste_combinaisons = []  # initialisation de la liste des combinaisons à générer
    indices = list(range(p))  # initialisation de la liste avec les indices de départ [0,1,...,p-1]

    liste_combinaisons.append(tuple(indices))  # conversion de la liste des indices en tuple puis ajout à la liste
                                               # des combinaisons
    nb_iteration = 1  # permet de limiter les combinaisons au nb_sujet
    if p == n:
        return liste_combinaisons

    i = p - 1  # on commence à incrémenter le dernier indice de la liste

    # tant qu'il reste encore des indices à incrémenter ou que l'on n'a pas les combinaisons que l'on souhaite
    while i != -1 and nb_iteration < nb_sujet:
        indices[i] += 1  # on incrémente l'indice

        for j in range(i + 1, p):  # on recale les indices des éléments suivants par rapport à ndices[i]
            indices[j] = indices[j - 1] + 1
        if indices[i] == (n - p + i):  # si cet indice a atteint sa valeur maxi
            i -= 1  # on repère l'indice précédent
        else:  # sinon
            i = p - 1  # on repère le dernier indice

        liste_combinaisons.append(tuple(indices))  # ajout de la combinaison à la liste
        nb_iteration += 1
    return liste_combinaisons


# Génère les contrôles que l'on veut
# Param : intervallesMax : un tableau remplit du nombre de questions pour chaque étiquette
#           choixPossible : tableau renvoyé par choixDesSolutionsDansLeSysteme
# Renvoie : un tableau de tableau dans chaque tableau il y a des tuples
#                       et chaque tuple sont des indices
#                       et les indices sert à désigner une question dans un tableau d'étiquette
# Exemple : [[(0,), (0, 1, 2, 3, 4, 5, 6)], [(1,), (0, 1, 2, 3, 4, 5, 6)],[(0, 1), (0, 1, 2, 3, 4, 5)]]
# le sujet 0, a 1 question de l'étiquette 0 (0,)
#            et 7 questions de l'étiquette 1 (0, 1, 2, 3, 4, 5, 6)
# le sujet 1, a 1 question de l'étiquette 0 (1,)
#            et 7 questions de l'étiquette 1 (0, 1, 2, 3, 4, 5, 6)
# le sujet 2, a 2 questions de l'étiquette 0 (0, 1)
#            et 6 questions de l'étiquette 1 (0, 1, 2, 3, 4, 5)
def generateEvaluationWithoutIDQuestion(intervallesMax, choixPossible):
    controles = []
    tableau_configurations = choixPossible[0][0]  # Tableau qui contient les différentes configurations de sujet
    tableau_choix_configuration = choixPossible[1]  # Tableau qui contient le nombre de choix pour chaque configuration

    # On parcourt toutes les configurations de sujet
    # (qui sont limités au nombre de sujets grâce à l'algo choixDesSolutionsDansLeSysteme )
    for i in range(len(tableau_configurations)):
        tableau_combinaison = [] # Tableau qui va prendre les combinaisons de questions différentes pour une configuration i donné
        # Boucle qui parcourt toutes les configurations
        for j in range(len(tableau_configurations[i])):
            # appel à combinaison pour avoir toutes les combinaisons que l'on souhaite pour une étiquette "j"
            combinaison = combinaisons_v1(tableau_configurations[i][j], intervallesMax[j], tableau_choix_configuration[i])
            # Et ajout de cette combinaison dans notre tableau qui prend toutes les combinaisons de question pour chaque étiquette
            tableau_combinaison.append(combinaison)
        # On fait un produit cartésien pour avoir le bon nombre de questions associé à chaque étiquette
        # en limitant le tableau au nombre de sujets que l'on veut avec cette configuration
        tableau_combinaison = combinaisons_tableaux(tableau_combinaison, tableau_choix_configuration[i])[:tableau_choix_configuration[i]]

        # On ajoute tous ces sujets à notre tableau final
        for k in range(len(tableau_combinaison)):
            controles.append(tableau_combinaison[k])
    return controles

# Param : controles : tableau de controles renvoyer par genererDesControles
#         id_question : tableau avec toutes les ids des questions de la base de données concerné par cette génération
#         Attention les questions doivent être associé par étiquette
#         et les étiquettes dans le même ordre que dans le reste des tableaux
#           exemple : [[12,34,53][13,52,54,33]...]
def associeControleIdQuestion(controles, id_questions):
    sujet_final = []
    for i in range(len(controles)):
        sujet_final.append([])
        for j in range(len(controles[i])):
            for k in range(len(controles[i][j])):
                sujet_final[i].append(id_questions[j][controles[i][j][k]])
    return sujet_final


# Param : enseignant: id de l'enseignant
#         etiquette_id : l'id d'une étiquette
# Renvoie : un tableau contenant tout les id des questions associé à la question
def getQuestionsID(enseignant, etiquette_id):
    try:
        # Connection à la BDD
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()


        sql = "SELECT liens.question \
                FROM liensEtiquettesQuestions liens \
                JOIN Etiquettes E ON E.id= liens.etiquette \
                WHERE E.enseignant = ? AND E.id = ?;"
        parameters = (enseignant, etiquette_id)

        result = cursor.execute(sql, parameters)
        result = result.fetchall()

        # Range les données dans un tableau de dictionnaires
        data = []
        for i in range(0, len(result)):
            data.append(result[i][0])

        # Fermeture de la connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as error:
        print("Une erreur est survenue lors de la sélecton des questions :", error)
        return False


# Param : intervalle = [{"min": 1, "max": 5, "value": [3, 5]}, {"min": 1, "max": 4, "value": [3, 4]}, {"min": 1, "max": 4, "value": [2, 4]}]
#     nb_sujet = 1
#     nb_question = 9
#     id_questions : tableau avec les id des questions = [[1, 2, 3, 4, 5], [2, 4, 8, 6], [6, 7, 8, 9]]
def enleveLesDoublons(id_questions, intervalle, nb_question, nb_sujet):
    copie_intervalle = deepcopy(intervalle)


    # Boucles pour créer un dico qui contient en clé : l'étiquette
    #                                         et en valeur : les questions qui sont dans une autre étiquette
    question_doublon = {}
    for i in range(len(id_questions)):
        for j in range(len(id_questions[i])):
            for k in range(len(id_questions)):
                if k != i and id_questions[i][j] in id_questions[k]:
                    if k in question_doublon:
                        if id_questions[i][j] not in question_doublon[k]:
                            question_doublon[k].append(id_questions[i][j])
                    else:
                        question_doublon[k] = [id_questions[i][j]]

    # On récupère les indices des étiquettes qui ont des doublons
    keys = list(question_doublon.keys())
    question_doublon = list(question_doublon.values())

    # Boucle pour retirer au maximum les doublons des questions
    # si une étiquette a atteint son minimum elle privatise les questions qui restent, même si elles sont
    # prises par d'autres étiquettes
    # et si une question peut être associé a plusieurs étiquettes sans pour autant changer les intervalles alors on
    # la garde pour plus tard. Pour pouvoir l'ajouter a l'étiquette qui correspond au mieux a la solution
    j = 0
    while j < len(keys):
        i = 0
        while i < len(question_doublon[j]):
            if keys and intervalle[keys[j]]["max"] - 1 < intervalle[keys[j]]["value"][1]:

                if keys and intervalle[keys[j]]["value"][1] - 1 < intervalle[keys[j]]["value"][0] and \
                        question_doublon[j][i] in id_questions[keys[j]]:
                    l = 0
                    v = i
                    while keys and l < intervalle[keys[j]]["value"][0]:
                        a_garder = -1
                        if len(question_doublon[j]) > v:
                            a_garder = question_doublon[j][v]
                        for k in range(len(keys)):
                            if a_garder in question_doublon[k]:
                                question_doublon[k].remove(a_garder)
                                if k != j:
                                    if a_garder in id_questions[keys[k]]:
                                        intervalle[keys[k]]["max"] -= 1
                                        if intervalle[keys[k]]["value"][1] > intervalle[keys[k]]["max"]:
                                            intervalle[keys[k]]["value"][1] -= 1
                                            if intervalle[keys[k]]["value"][0] > intervalle[keys[k]]["value"][1]:
                                                return 1, "Erreur due a un conflit d'etiquette verifier si plusieurs de vos étiquettes n'ont pas besoin de la même question"
                                        id_questions[keys[k]].remove(a_garder)

                        l += 1

                        if len(question_doublon[j]) == 0:
                            v = 0
                        else:
                            v = (v + 1) % len(question_doublon[j])
                else:

                    if question_doublon[j][i] in id_questions[keys[j]]:
                        a_garder = question_doublon[j][i]
                        for k in range(len(keys)):
                            if a_garder in question_doublon[k]:
                                question_doublon[k].remove(a_garder)
                                if k != j:
                                    if a_garder in id_questions[keys[k]]:
                                        intervalle[keys[k]]["max"] -= 1
                                        if intervalle[keys[k]]["value"][1] > intervalle[keys[k]]["max"]:
                                            intervalle[keys[k]]["value"][1] -= 1
                                            if intervalle[keys[k]]["value"][0] > intervalle[keys[k]]["value"][1]:
                                                return 1, "Erreur due a un conflit d'etiquette verifier si plusieurs de vos étiquettes n'ont pas besoin de la même question"
                                        id_questions[keys[k]].remove(a_garder)

                        i -= 1
            elif keys:
                if question_doublon[j][i] in id_questions[keys[j]]:
                    intervalle[keys[j]]["max"] -= 1
                    id_questions[keys[j]].remove(question_doublon[j][i])
            i += 1
        j += 1

    # Enchainement de boucle pour tirer un tableau de tuple sous cette forme [(id_etiquette,id_question), ...]
    # Pour pouvoir jouer avec les combinaisons si on ajoute une question à une étiquette ou une autre
    dico = {}
    for i in range(len(question_doublon)):
        for j in range(len(question_doublon[i])):
            if question_doublon[i][j] in dico:
                if i not in dico[question_doublon[i][j]]:
                    dico[question_doublon[i][j]].append(i)
            else:
                dico[question_doublon[i][j]] = [i]
    items = list(dico.items())
    valeur = []
    for i in range(len(items)):
        valeur.append([])
        for j in range(len(items[i][1])):
            valeur[i].append((items[i][1][j], items[i][0]))

    suite_du_petit_test = combinaisons_tableaux(valeur)

    # Boucle qui s'arètent une fois quelle a trouvé une bonne combinaison en ayant
    # placé les questions en doubles dans une bonne étiquette
    # Ou qui parcourt jusqu'avoir placé la ou elle pouvait la question avec ces multiples étiquettes
    # et renvoie l'impossibilité de réaliser la demande si c'est impossible et pourquoi
    result_solution = None
    for i in range(len(suite_du_petit_test)):
        for j in range(len(suite_du_petit_test[i])):
            id_questions[suite_du_petit_test[i][j][0]].append(suite_du_petit_test[i][j][1])
            intervalle[suite_du_petit_test[i][j][0]]["max"] += 1
            if intervalle[suite_du_petit_test[i][j][0]]["value"][1] < \
                    copie_intervalle[suite_du_petit_test[i][j][0]]["value"][1]:
                intervalle[suite_du_petit_test[i][j][0]]["value"][1] += 1

        # Test la solution avec les questions en doubles qui varie
        result_solution = [0, 0, [2147483647, 0]]
        test_solution = systemeARes(intervalle, nb_question, nb_sujet)
        if type(test_solution) != tuple:
            return test_solution
        else:
            result_solution[1] = max(result_solution[1],test_solution[1])
            result_solution[2][0] = min(result_solution[2][0], test_solution[2][0])
            result_solution[2][1] = max(result_solution[2][1], test_solution[2][1])

        # Retire l'ancienne solution pour recommencer avec la question multiples étiquettes qui change d'étiquette
        for j in range(len(suite_du_petit_test[i])):
            id_questions[suite_du_petit_test[i][j][0]].remove(suite_du_petit_test[i][j][1])
            intervalle[suite_du_petit_test[i][j][0]]["max"] -= 1
            if intervalle[suite_du_petit_test[i][j][0]]["value"][1] > \
                    copie_intervalle[suite_du_petit_test[i][j][0]]["value"][1]:
                intervalle[suite_du_petit_test[i][j][0]]["value"][1] -= 1
    return 0, "Impossible de trouver une solution", result_solution


def generateEvaluation(enseignant, evaluation):
    id_questions = []
    intervalle = []
    for i in range(len(evaluation["labels"])):
        id_questions.append(getQuestionsID(enseignant, evaluation["labels"][i]["id"]))
        intervalle.append(evaluation["labels"][i]["range"])
    result = enleveLesDoublons(id_questions,intervalle, evaluation["questionSize"], evaluation["size"])
    if type(result) == tuple:
        if len(result) == 2:
            return result
        elif len(result) == 3:
            return result
    choixDesSolution = choixDesSolutionsDansLeSysteme(result, evaluation["size"])
    controles = generateEvaluationWithoutIDQuestion(choixDesSolution[0][2], choixDesSolution)

    # si les questions sont regroupées par étiquettes
    if evaluation["groupQuestions"]:

        # Dans les 2 cas, on mélange les questions entre elles
        for i in range(len(controles)):
            for j in range(len(controles[i])):
                controles[i][j] = list(controles[i][j])
                shuffle(controles[i][j])
        sujet_final = associeControleIdQuestion(controles, id_questions)  # On associe les index du tableau aux id des questions

        # Si on ne conserve pas l'ordre des étiquettes
        if not evaluation["keepLabelsOrder"]:
            # On mélange l'ordre des étiquettes
            for i in range(len(sujet_final)):
                shuffle(sujet_final[i])
    # les questions ne sont pas regroupées par étiquettes
    else:
        sujet_final = associeControleIdQuestion(controles, id_questions)  # On associe les index du tableau aux id des questions
        # On mélange les questions entre elles
        for i in range(len(sujet_final)):
            shuffle(sujet_final[i])
    shuffle(sujet_final)  # On mélange les sujets entre eux
    return sujet_final
