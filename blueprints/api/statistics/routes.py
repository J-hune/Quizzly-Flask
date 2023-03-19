from flask import Blueprint
from blueprints.api.statistics.teachers.routes import teachers
#from blueprints.api.statistics.students.routes import students

statistics = Blueprint('statistics', __name__, url_prefix='/statistics')

statistics.register_blueprint(teachers)
#statistics.register_blueprint(students)
