import copy
import sqlite3

from flask import session, request
from flask_socketio import emit, join_room, leave_room, close_room

from functions.broadcast import generateCode, deleteCode
from functions.questions import getQuestion

sequenceEnCours = {}  # Les données de ce tableau peuvent servir pour les stats (il manque la date).


# Les données d'une séquence sont sous cette forme :

#  'GAHisbh5': {
#      'name': 'GAHisbh5',
#      'enseignant':
#      'GEBXTRQbmhZOTXqrAAAF',
#      'etudiants': [{'id': 22100000, 'nom': 'donov zst'}],
#      'questions': [],
#      'derQuestionTraitee': objet de type question,
#      'stopReponses': False,
#      'reponsesEtudiant': [
#          {'id': 22100000, 'question': 6, 'answer': 20},
#          {'id': 22100000, 'question': 18, 'answer': [33]}
#      ]
#  }

# Quand un nouvel utilisateur se connecte au socket
def connect():
    user = session.get("user")
    if user:
        if user["type"] == "Enseignant":
            print("Connexion d'un nouvel enseignant au socket: {0} {1}".format(user["firstname"], user["surname"]))
        elif user["type"] == "Etudiant":
            print("Connexion d'un nouvel étudiant au socket: {0} {1}".format(user["firstname"], user["surname"]))
        else:
            emit("error", "Le type de l'utilisateur est invalide")


# Quand un utilisateur se déconnecte du socket
def disconnect():
    print('Un client vient de se déconnecter du socket')

    # Suppression du code et fermeture de la séquence
    if 'user' in session and session["user"]["type"] == "Enseignant":

        # On cherche si l'enseignant a une séquence en cours
        if 'room' in session["user"]:
            room_id = session["user"]["room"]
            del session["user"]["room"]

            # Si l'enseignant a une séquence en cours
            if room_id and room_id in sequenceEnCours:
                emit("renderSequenceEnd", to=room_id)
                close_room(room_id)
                deleteCode(room_id)
                del sequenceEnCours[room_id]

    elif 'user' in session and session["user"]["type"] == "Etudiant":
        # On cherche si l'étudiant est dans une séquence en cours
        if 'room' in session["user"]:
            room_id = session["user"]["room"]
            del session["user"]["room"]
            leave_room(room_id)

            if room_id in sequenceEnCours:
                # on supprime l'étudiant de la liste
                sequenceEnCours[room_id]["etudiants"] = [
                    etudiant for etudiant in sequenceEnCours[room_id]["etudiants"] if
                    etudiant["id"] != session["user"]["id"]
                ]

                emit("renderStudentList", sequenceEnCours[room_id]["etudiants"], to=room_id)

            else:
                emit("error", "La room #" + room_id + " n'existe pas")


# Quand un enseignant lance une séquence
def createRoom(sequence_id):
    if 'user' in session and session["user"]["type"] == "Enseignant":

        # On récupère les questions liées à la séquence
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        # Selection des données dans la table
        cur.execute("SELECT idQuestion FROM liensSequencesQuestions WHERE idSequence = ?;", (sequence_id,))
        res = cur.fetchall()

        # Fermeture de la connection
        cur.close()
        con.close()

        # Si la séquence n'existe pas
        if not res:
            emit("error", "La séquence ayant l'id #{0} n'a pas été trouvée".format(sequence_id))

        else:
            # Génération de l'id de la room :
            room_id = generateCode()

            # Le client est mis dans la room
            join_room(room_id)
            session["user"]["room"] = room_id

            # On crée une room dans le tableau des questions en cours de
            # diffusion avec toutes les informations utiles aux echanges de reponses et questions
            sequenceEnCours[room_id] = {
                'name': room_id,
                'enseignant': request.sid,
                'etudiants': [],
                "questions": [int(t[0]) for t in res],
                "derQuestionTraitee": None,
                "stopReponses": False,
                "reponsesEtudiant": []
            }

            # On demande au client d'afficher la page d'attente
            emit("renderSequenceInit", room_id, to=room_id)


# Quand un enseignant passe à la question suivante
def nextQuestion():
    # Si l'utilisateur est un enseignant et a une séquence en session
    if 'user' in session and session["user"]["type"] == "Enseignant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:

            # On récupère la première question
            question = getQuestion(sequenceEnCours[room_id]["questions"].pop(0))

            # On modifie derQuestionTraitee avec une copie profonde de question
            sequenceEnCours[room_id]["derQuestionTraitee"] = copy.deepcopy(question)

            # On réactive les réponses
            sequenceEnCours[room_id]["stopReponses"] = False

            # On supprime la valeur du numérique (pour éviter la triche)
            question.pop("numerique")

            # Boucle pour supprimer la clé "reponseJuste" de chaque réponse (pour éviter la triche)
            for reponse in question["reponses"]:
                reponse.pop("reponseJuste", None)

            emit("renderQuestion", {
                "question": question,
                "last": len(sequenceEnCours[room_id]["questions"]) < 1
            }, to=room_id)

        else:
            del session["user"]["room"]
            emit("error", "La room #" + room_id + " n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")


# Quand un enseignant demande l'affichage de la correction
def askCorrection():
    # Si l'utilisateur est un enseignant et a une séquence en session
    if 'user' in session and session["user"]["type"] == "Enseignant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:
            question = sequenceEnCours[room_id]["derQuestionTraitee"]

            # Si la question est de type "QCM"
            if question['type'] == 0:
                reponses_justes = [r['id'] for r in question['reponses'] if r['reponseJuste']]
                emit("renderCorrection", reponses_justes, to=room_id)
            elif question['type'] == 1:
                numerique = question['numerique']
                emit("renderCorrection", numerique, to=room_id)

        else:
            emit("error", "La room #" + room_id + " n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")


# Quand un enseignant interdit les nouvelles réponses
def askStopResponses():
    # Si l'utilisateur est un enseignant et a une séquence en session
    if 'user' in session and session["user"]["type"] == "Enseignant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:
            sequenceEnCours[room_id]["stopReponses"] = True
            emit("renderSubmitButton", not sequenceEnCours[room_id]["stopReponses"], to=room_id)

        else:
            emit("error", "La room #" + room_id + " n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")


# Quand un étudiant rejoint une séquence
def joinRoom(room_id):
    if 'user' in session and session["user"]["type"] == "Etudiant":

        # Si la séquence existe
        if room_id in sequenceEnCours:
            session["user"]["room"] = room_id
            join_room(room_id)

            # On ajoute l'étudiant dans la liste des étudiants connectés
            sequenceEnCours[room_id]["etudiants"].append({
                "id": session["user"]["id"],
                "nom": session["user"]["firstname"] + " " + session["user"]["surname"]
            })

            # On modifie les données du professeur
            emit("renderStudentList", sequenceEnCours[room_id]["etudiants"], to=room_id)

            # On envoie la question si l'etudiant arrive en cours de séquence
            if sequenceEnCours[room_id]["derQuestionTraitee"]:
                question = copy.deepcopy(sequenceEnCours[room_id]["derQuestionTraitee"])

                # On supprime la valeur du numérique (pour éviter la triche)
                question.pop("numerique")

                # Boucle pour supprimer la clé "reponseJuste" de chaque réponse (pour éviter la triche)
                for reponse in question["reponses"]:
                    reponse.pop("reponseJuste", None)

                emit("renderQuestion", {
                    "question": question,
                    "last": len(sequenceEnCours[room_id]["questions"]) < 1
                }, to=request.sid)

                emit("renderSubmitButton", not sequenceEnCours[room_id]["stopReponses"], to=request.sid)

        else:
            emit("error", "La room #" + room_id + " n'existe pas")


# Quand un utilisateur soumet une réponse
def submitAnswer(answer):
    # Si l'utilisateur est un étudiant et qu'il une séquence en session
    if 'user' in session and session["user"]["type"] == "Etudiant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:

            # Si l'utilisateur a déjà répondu → Erreur
            if any(
                    answer["id"] == session["user"]["id"] and
                    answer["question"] == sequenceEnCours[room_id]["derQuestionTraitee"]["id"]
                    for answer in sequenceEnCours[room_id].get("reponsesEtudiant", [])
            ):
                emit("error", "Vous avez déjà répondu à la question")
            else:
                # On ajoute la réponse de l'étudiant
                sequenceEnCours[room_id]["reponsesEtudiant"].append({
                    "id": session["user"]["id"],
                    "question": sequenceEnCours[room_id]["derQuestionTraitee"]["id"],
                    "answer": answer
                })
                emit("renderSubmitButton", False, to=request.sid)

                # Si c'est un QCM
                if sequenceEnCours[room_id]["derQuestionTraitee"]["type"] == 0:

                    # Pour chaque valeur, on émet un event
                    for answerId in answer:
                        emit("renderNewResponse", answerId, to=room_id)

                else:
                    emit("renderNewResponse", answer, to=room_id)

        else:
            emit("error", "La room #" + room_id + " n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")
