from flask import Flask
import sqlite3
from blueprints.api.routes import api

app = Flask(__name__)

app.register_blueprint(api)

con = sqlite3.connect('database.sql')
cur = con.cursor()

if __name__ == '__main__':
    app.run()
