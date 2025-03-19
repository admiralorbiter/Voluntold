# app.py

from flask import Flask
from flask_login import LoginManager
from forms import LoginForm
from models.user import User
from routes import init_routes
from config import DevelopmentConfig, ProductionConfig
from dotenv import load_dotenv
import os
from models import db
from flask_apscheduler import APScheduler
from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

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

    # Configure APScheduler logger to use our scheduler handler
    apscheduler_logger = logging.getLogger('apscheduler')
    apscheduler_logger.setLevel(logging.WARNING)  # Only log warnings and errors
    apscheduler_logger.addHandler(scheduler_handler)
    apscheduler_logger.propagate = False

setup_logging()

# Initialize scheduler
scheduler = APScheduler()

# Load configuration based on the environment
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Add scheduler config
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'UTC'

# Initialize extensions
db.init_app(app)
scheduler.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Create the database tables
with app.app_context():
    db.create_all()

# Schedule the sync job
@scheduler.task('interval', id='sync_all_data', hours=6)
def scheduled_sync():
    with app.app_context():
        from routes.upcoming_events import sync_recent_salesforce_data
        current_time = datetime.now(timezone.utc)
        scheduler_logger = logging.getLogger('scheduler')
        
        scheduler_logger.info(f"Starting scheduled sync at {current_time}")
        
        try:
            result = sync_recent_salesforce_data()
            
            if result['success']:
                scheduler_logger.info(
                    f"Sync completed successfully at {datetime.now(timezone.utc)}\n"
                    f"Successes: {result['success_count']}\n"
                    f"Details:\n{chr(10).join(result['details'])}"
                )
            else:
                scheduler_logger.error(
                    f"Sync completed with errors at {datetime.now(timezone.utc)}\n"
                    f"Errors: {result['error_count']}\n"
                    f"Successes: {result['success_count']}\n"
                    f"Details:\n{chr(10).join(result['details'])}"
                )
                
        except Exception as e:
            scheduler_logger.error(f"Sync failed with exception: {str(e)}", exc_info=True)

# Start the scheduler
scheduler.start()
logging.getLogger('scheduler').info("APScheduler started successfully")

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