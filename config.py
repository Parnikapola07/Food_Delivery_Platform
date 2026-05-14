import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zomato_clone_super_secret_key'

    db_url = os.environ.get('DATABASE_URL')

    if db_url and db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///food_delivery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False