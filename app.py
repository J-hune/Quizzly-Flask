from flask import Flask
import sqlite3
from blueprints.api.routes import api
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = "4f75177439a4bb0b5494d3ce5fd4727fe7b0d61d17ffd81d6420e40c9dc7d9da"

app.register_blueprint(api)

app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
)

con = sqlite3.connect('database.db')
cur = con.cursor()

if __name__ == '__main__':
    app.run()
