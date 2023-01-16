from flask import Flask
import mysql.connector
from blueprints.api.routes import api
import os

app = Flask(__name__)

app.register_blueprint(api)

sql = mysql.connector.connect(
    pool_size=3,
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)

if __name__ == '__main__':
    app.run()
