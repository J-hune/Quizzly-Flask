# Quizzly-Flask

## Installation
Python 3.7 ou une version plus récente est requise.

Pour installer les dépendances nécessaires, exécutez la commande suivante :
```shell
pip install -r requirements.txt
```

## Utilisation
Pour lancer le serveur, exécutez la commande suivante :
```shell
python3 app.py
```

## Structure du dossier
- `app.py`: point d'entrée de l'application Flask.
- `blueprints`: contient les différents blueprints de l'application.
- `functions`: contient les fonctions réutilisables utilisées dans l'application.
- `events.py`: contient les événements de l'application (par exemple, les événements de socketio).
- `database.db`: fichier de base de données SQLite.
- `requirements.txt`: contient la liste des dépendances Python requises pour l'application.

## Configuration

Les variables d'environnement nécessaires pour l'application sont stockées dans le fichier `.env`.

Les variables d'environnement disponibles sont les suivantes :
- `FLASK_SECRET_KEY`: Clé secrète utilisée par Flask pour signer les cookies et autres données.
