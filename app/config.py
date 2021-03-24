import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'Harmony'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_DEV']


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_PROD']


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
