# app.py

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from forms import LoginForm
from models.user import User
from routes import init_routes
from config import DevelopmentConfig, ProductionConfig
from dotenv import load_dotenv
import os
from models import db
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)

# Set up logging
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up file handler for scheduler logs only
    scheduler_handler = RotatingFileHandler(
        'logs/scheduler.log',
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    scheduler_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] SCHEDULER: %(message)s'
    ))

    # Create a specific logger for scheduler
    scheduler_logger = logging.getLogger('scheduler')
    scheduler_logger.setLevel(logging.INFO)
    scheduler_logger.addHandler(scheduler_handler)
    
    # Prevent scheduler logs from propagating to root logger
    scheduler_logger.propagate = False

setup_logging()

# Load configuration based on the environment
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Create the database tables
with app.app_context():
    db.create_all()

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Initialize routes
init_routes(app)

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    app.run(debug=True)