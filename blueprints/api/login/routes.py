from flask import Blueprint
from blueprints.api.login.enseignants.routes import enseignants
from blueprints.api.login.etudiants.routes import etudiants

login = Blueprint('login', __name__, url_prefix='/login')

login.register_blueprint(enseignants)
login.register_blueprint(etudiants)