from flask import session
from flask_socketio import emit


def connect():
    user = session.get("user")
    if user:
        if user["type"] == "Enseignant":
            print("Connexion d'un nouvel enseignant au socket: " + user["firstname"] + " " + user["surname"])
        elif user["type"] == "Etudiant":
            print("Connexion d'un nouvel étudiant au socket: " + user["firstname"] + " " + user["surname"])


def disconnect():
    print('Un client vient de se déconnecter du socket')
