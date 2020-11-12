import os

class onfig:
    SECRET_KEY=os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
#    SQLALCHEMY_BINDS={'accounts' : 'HEROKU_POSTGRESQL_BLUE_URL'}
    SQLALCHEMY_TRACK_MODIFICATIONS=False
