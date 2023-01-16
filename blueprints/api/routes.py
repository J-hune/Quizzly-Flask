from flask import Blueprint
import app

from blueprints.api.labels.routes import label
from blueprints.api.login.routes import login
from blueprints.api.questions.routes import questions
from blueprints.api.users.routes import users

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(label)
api.register_blueprint(login)
api.register_blueprint(questions)
api.register_blueprint(users)
