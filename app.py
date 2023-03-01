from flask import Flask, session, request
from blueprints.api.routes import api
from flask_cors import CORS

from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = "4f75177439a4bb0b5494d3ce5fd4727fe7b0d61d17ffd81d6420e40c9dc7d9da"

app.register_blueprint(api)

app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

sequenceEnCours = {} # Les données de ce tableau peuvent servir pour les stats (il manque la date).
# Les données seront stockées sous cette forme :
# {'2E2E2RR': ## Cle unique de la question/sequence
#       {'name': '2E2E2RR', ## Cle unique de la question/sequence
#        'enseignant': '5rPA12jQpLpxX3DdAAAH', ## Ici l'id de l'enseignant stocké à la création de la question
#        'stopReponses': False, ## Ici un boolean pour savoir si on peut encore rentrer des reponses
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


sio = SocketIO(app)


# data = { "question" : {
#     "id": 1,
#     "type": 0,
#     "enonce": "Qui a calculé la circonférence de la terre en -200 av JC ?",
#     "enseignant": 1
#     "etiquettes": [{"couleur": "#000000", "nom": "histoire"},...],
#     "reponses": [{"id": 1, "question": 1, "reponse": "Ératosthène", "reponseJuste": 1},...],
#   },
#   "room" : "2E2E2RR"
#   }
@sio.on('RenderQuestion')
def RenderQuestion(data):
    global sequenceEnCours
    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            room = data['room']
            # On rejoint la room (on la creer en meme temps)
            join_room(room)

            # On garde le numero de la room en session
            # (possible de l'utiliser à la place des data['room'] dans les autres fonctions)
            session["room"] = room

            # On crée une room dans le tableau des questions en cours de
            # diffusion avec toutes les informations utiles aux echanges de reponses et questions
            sequenceEnCours[room] = {'name': room,
                                     'enseignant': request.sid,
                                     "stopReponses": False,
                                     "reponsesEtudiant": [],
                                     "reponses": data["question"]["reponses"]}

            # Emission de la question
            emit('RenderQuestion', data["question"], to=room)
        # Ce n'est pas un enseignant
        else:
            # On est un étudiant et on essaye de se connecter avec un code à un questionnaire (s'il existe)
            if data['room'] in sequenceEnCours:
                room = data['room']
                # On rejoint la room
                join_room(room)

                # On garde le numero de la room en session
                # (possible de l'utiliser à la place des data['room'] dans les autres fonctions)
                session["room"] = room

                # Emission de la question
                emit('RenderQuestion', data["question"], to=room)

                # Emission d'un message avec les informations concernant l'étudiant
                # qui se connecte à l'enseignant qui a lancé le questionnaire
                emit('NouveauEleve', session['user'],
                     to=sequenceEnCours[room]['enseignant'])
            else:
                emit('Error', ({
                                   "status": 404,
                                   "reason": "La question/sequence n'existe pas"
                               }, 404))
    # Pas en session
    else:
        emit('Error', ({
                           "status": 400,
                           "reason": "Session non disponible"
                       }, 400))
    print("session", session)


# data = { "response" : {"id": 1, "reponse": "Dounnouvahannne", "reponseJuste": 1, "question": 1},
# "room": 2E2E2RR
# }
@sio.on('RenderResponse')
def RenderResponse(data):

    if 'user' in session:
        # Si la room existe dans notre tableau global et que l'on n'a pas arrêté l'envoie des réponses
        if data['room'] in sequenceEnCours and (not sequenceEnCours[data['room']]["stopReponses"]):
            room = data['room']

            # On ajoute au bon endroit la réponse de l'étudiant avec son ID (numéro étudiant)
            sequenceEnCours[room]["reponsesEtudiant"].append({"reponse": data["response"]["reponse"], "idEtu": session["user"]["id"]})

            # Emission d'un message avec la reponse de l'étudiant
            # à l'enseignant qui a lancé le questionnaire
            emit('RenderResponse', data["response"], to=sequenceEnCours[room]['enseignant'])
        else:
            emit('Error', ({
                               "status": 404,
                               "reason": "La question/sequence n'existe pas"
                           }, 404))
    # Pas en session
    else:
        emit('Error', ({
                           "status": 400,
                           "reason": "Session non disponible"
                       }, 400))


@sio.on('RenderResponses')
def RenderResponses(data):
    if 'user' in session:
        # Si la room existe dans notre tableau global
        if data['room'] in sequenceEnCours:
            room = data['room']

            # On envoie à tout le monde les réponses qui on était donné
            # (sans tri, les réponses peuvent être en double, triple...)
            emit('RenderResponses', sequenceEnCours[room]["reponsesEtudiant"], to=room)
        else:
            emit('Error', ({
                               "status": 404,
                               "reason": "La question/sequence n'existe pas"
                           }, 404))
    else:
        emit('Error', ({
                           "status": 400,
                           "reason": "Session non disponible"
                       }, 400))


# data = {
# "room": 2E2E2RR
# }
@sio.on('StopResponses')
def StopResponses(data):
    global sequenceEnCours

    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Si la room existe
            if data['room'] in sequenceEnCours:
                # On stop l'entrée des réponses
                sequenceEnCours[data['room']]["stopReponses"] = True
                # On dit à toute la room que l'on a stoppé l'entrée des réponses
                emit('StopResponses', True, to=data['room'])
            else:
                emit('Error', ({
                                   "status": 404,
                                   "reason": "La question/sequence n'existe pas"
                               }, 404))
        else:
            emit('Error', ({
                               "status": 403,
                               "reason": "Forbidden"
                           }, 403))
    else:
        emit('Error', ({
                           "status": 400,
                           "reason": "Session non disponible"
                       }, 400))


@sio.on('RenderCorrection')
def RenderCorrection(data):
    global sequenceEnCours

    if 'user' in session:
        # Si c'est un enseignant
        if session["user"]["type"] == "Enseignant":
            # Si la room existe
            if data['room'] in sequenceEnCours:
                # On crée un tableau qui va prendre que les bonnes réponses du tableau de réponse par défaut
                # la seule réponse pour une question numérique et les bonnes réponses pour une question QCM
                correction= []
                for i in range(len(sequenceEnCours[data['room']]["reponses"])):
                    if sequenceEnCours[data['room']]["reponses"][i]["reponseJuste"] == 1:
                        correction.append(sequenceEnCours[data['room']]["reponses"][i])
                # On envoie le tableau de bonne(s) réponse(s)
                emit('RenderCorrection', correction, to=data['room'])
            else:
                emit('Error', ({
                                   "status": 404,
                                   "reason": "La question/sequence n'existe pas"
                               }, 404))
        else:
            emit('Error', ({
                               "status": 403,
                               "reason": "Forbidden"
                           }, 403))
    else:
        emit('Error', ({
                           "status": 400,
                           "reason": "Session non disponible"
                       }, 400))


if __name__ == '__main__':
    sio.run(app, allow_unsafe_werkzeug=True, debug=True)

