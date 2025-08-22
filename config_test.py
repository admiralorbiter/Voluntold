# config_test.py
import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:
    SECRET_KEY = 'test_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SF_USERNAME = os.getenv('SF_USERNAME')
    SF_PASSWORD = os.getenv('SF_PASSWORD')
    SF_SECURITY_TOKEN = os.getenv('SF_SECURITY_TOKEN')
    DEBUG = True
    TESTING = True
    # Use a separate test database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.db'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
