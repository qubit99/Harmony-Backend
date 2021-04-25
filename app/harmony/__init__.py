from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
CORS(app)
app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)

api = Api(app)


@app.route('/')
def hello():
    return "Hello World!"

############################################################

from harmony.resources.auth import SignUp, Login
from harmony.resources.apiv1 import UserSettings

api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UserSettings, '/settings')

