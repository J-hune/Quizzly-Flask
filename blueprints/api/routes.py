from flask import Blueprint, session

from blueprints.api.evaluations.routes import evaluations
from blueprints.api.students.routes import students
from blueprints.api.labels.routes import label
from blueprints.api.login.routes import login
from blueprints.api.questions.routes import questions
from blueprints.api.sequences.routes import sequences
from blueprints.api.statistics.routes import statistics

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(label)
api.register_blueprint(login)
api.register_blueprint(questions)
api.register_blueprint(students)
api.register_blueprint(sequences)
api.register_blueprint(statistics)
api.register_blueprint(evaluations)

@api.route('/')
def index():
    print(session.get("user"))
    return {}
