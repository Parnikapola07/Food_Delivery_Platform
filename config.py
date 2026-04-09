import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zomato_clone_super_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///food_delivery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
