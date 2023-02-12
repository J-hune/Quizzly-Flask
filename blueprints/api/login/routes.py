from flask import Blueprint
from blueprints.api.login.teachers.routes import teachers
from blueprints.api.login.students.routes import students

login = Blueprint('login', __name__, url_prefix='/login')

login.register_blueprint(teachers)
login.register_blueprint(students)