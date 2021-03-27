from flask import Flask
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)

api = Api(app)


@app.route('/')
def hello():
    return "Hello World!"

############################################################

from harmony.resources.auth import SignUp, Login

api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')

