import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-change-in-prod'
    DATABASE = os.environ.get('DATABASE') or 'sac_shop.db'
    DEBUG = True