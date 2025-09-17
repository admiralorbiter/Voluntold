import os
import sys
from dotenv import load_dotenv

# Add the project root directory to the Python path
# Adjust this path based on your project structure
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables from .env file
# Make sure to create a .env file with your actual credentials

# Also try to load from .env file as fallback
load_dotenv(os.path.join(project_root, '.env'))

# Environment variables are now set and ready

try:
    # Import the Flask app instance and the sync function
    # Adjust the import path based on your project structure
    # Assuming your Flask app is created in 'app.py' or '__init__.py'
    from app import app # Or from your_package import app
    from routes.upcoming_events import sync_upcoming_events

    print("Starting scheduled sync...")

    # Create an application context to access db, config, etc.
    with app.app_context():
        result = sync_upcoming_events()

        if result.get('success'):
            print("Sync completed successfully.")
            print(f"  New: {result.get('new_count', 0)}")
            print(f"  Updated: {result.get('updated_count', 0)}")
            print(f"  Deleted: {result.get('deleted_count', 0)}")
            print(f"  Archived: {result.get('archived_count', 0)}")
        else:
            print(f"Sync failed: {result.get('error', 'Unknown error')}")

except ImportError as e:
    print(f"Error importing application components: {e}")
    print("Please ensure the script is run from the correct directory and")
    print("that the import paths for 'app' and 'sync_upcoming_events' are correct.")
except Exception as e:
    print(f"An unexpected error occurred during sync: {e}")
