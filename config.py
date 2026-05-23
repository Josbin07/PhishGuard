import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY       = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///phishguard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_BASE_URL     = os.getenv('APP_BASE_URL', 'http://localhost:5000')
    MAIL_SERVER      = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT        = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS     = True
    MAIL_USERNAME    = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD    = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
