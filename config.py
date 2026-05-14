import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zomato_clone_super_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://food_delivery_reuc_user:7nPpC0qzChgi7ohG9BtlgwJD0Go2fxUC@dpg-d82qfn0g4nts73b8sveg-a.oregon-postgres.render.com/food_delivery_reuc')
    SQLALCHEMY_TRACK_MODIFICATIONS = False