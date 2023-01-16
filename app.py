from flask import Flask

from blueprints.api.routes import api

app = Flask(__name__)

app.register_blueprint(api)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
