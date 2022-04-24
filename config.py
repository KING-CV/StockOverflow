import os

class AppConfig(object):
    SQLALCHEMY_ECHO = False
    DEBUG = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.getenv('COCKROACH')

    @property
    def SECRET_KEY(self):
        return os.getenv('FLASK_SECRET')