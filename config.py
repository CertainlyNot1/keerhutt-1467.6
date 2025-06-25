import os
class Config:
    secret_key='perekryt_ligmi'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kood.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False