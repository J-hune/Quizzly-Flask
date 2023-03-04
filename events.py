import copy
import sqlite3

from flask import session, request
from flask_socketio import emit, join_room, close_room, rooms

from functions.broadcast import generateCode, deleteCode
from functions.questions import getQuestion

sequenceEnCours = {}  # Les données de ce tableau peuvent servir pour les stats (il manque la date).


# Les données seront stockées sous cette forme :
# {'2E2E2RR': ## Cle unique de la question/sequence
#       {'name': '2E2E2RR', ## Cle unique de la question/sequence
#        'enseignant': '5rPA12jQpLpxX3DdAAAH', ## Ici l'id de l'enseignant stocké à la création de la question
#        'stopReponses': False, ## Ici un boolean pour savoir si on peut encore rentrer des reponses
#        'questions': [6, 16]
#        'derQuestionTraitee': objet question
#        'reponsesEtudiant': [##Ici un tableau qui a toutes les reponses entrées par les étudiants (sert pour les stats)
#               {'reponse': 'Dounnouvahannne', 'idEtu': 532312},
#               {'reponse': 'EREN YEAAAAAAAAAGGERRRR', 'idEtu': 231342},
#               {'reponse': 'Dark Vador', 'idEtu': 344322},
#               {'reponse': 'Platon', 'idEtu': 125749}],
#        'reponses': [{'id': 1, 'question': 1, 'reponse': 'Ératosthène', 'reponseJuste': 1}]
#        Au-dessus un tableau qui contient la reponse juste pour les questions numériques
#        ou toutes les reponses d'un QCM (meme les fausses)
#        }
# }

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

            if room_id and room_id in sequenceEnCours:
                emit("renderSequenceEnd", to=room_id)
                close_room(room_id)
                deleteCode(room_id)
                del sequenceEnCours[room_id]


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
            roomId = generateCode()

            # Le client est mis dans la room
            join_room(roomId)
            session["user"]["room"] = roomId

            # On crée une room dans le tableau des questions en cours de
            # diffusion avec toutes les informations utiles aux echanges de reponses et questions
            sequenceEnCours[roomId] = {'name': roomId,
                                       'enseignant': request.sid,
                                       "questions": [int(t[0]) for t in res],
                                       "derQuestionTraitee": 0,
                                       "stopReponses": False,
                                       "reponsesEtudiant": [],
                                       "reponses": []
                                       }

            # On demande au client d'afficher la page d'attente
            emit("renderSequenceInit", roomId, to=roomId)


def nextQuestion():
    # Si l'utilisateur est un enseignant et a une séquence en session
    if 'user' in session and session["user"]["type"] == "Enseignant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:

            # On récupère la première question
            question = getQuestion(session["user"]["id"], sequenceEnCours[room_id]["questions"].pop(0))

            # On modifie derQuestionTraitee avec une copie profonde de question
            sequenceEnCours[room_id]["derQuestionTraitee"] = copy.deepcopy(question)

            # On réactive les réponses
            sequenceEnCours[room_id]["stopReponses"] = True

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
            emit("error", "La room de l'utilisateur n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")


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
            emit("error", "La room de l'utilisateur n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")


def askStopResponses():
    # Si l'utilisateur est un enseignant et a une séquence en session
    if 'user' in session and session["user"]["type"] == "Enseignant" and 'room' in session["user"]:
        room_id = session["user"]["room"]

        # Si la séquence existe
        if room_id in sequenceEnCours:
            sequenceEnCours[room_id]["stopReponses"] = True

        else:
            emit("error", "La room de l'utilisateur n'existe pas")
    else:
        emit("error", "La room de l'utilisateur n'a pas pu être trouvée")