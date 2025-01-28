import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # PostgreSQL connection URI
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost/tagtrack'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
