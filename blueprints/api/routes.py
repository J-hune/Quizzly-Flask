from flask import Blueprint, session

from blueprints.api.students.routes import students
from blueprints.api.labels.routes import label
from blueprints.api.login.routes import login
from blueprints.api.questions.routes import questions
from blueprints.api.users.routes import users
from blueprints.api.sequences.routes import sequences

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(label)
api.register_blueprint(login)
api.register_blueprint(questions)
api.register_blueprint(users)
api.register_blueprint(students)
api.register_blueprint(sequences)

@api.route('/')
def index():
    print(session.get("user"))
    return {}
