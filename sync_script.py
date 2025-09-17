import os
import sys
from dotenv import load_dotenv

# Add the project root directory to the Python path
# Adjust this path based on your project structure
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables directly (same as WSGI file)
os.environ['SF_USERNAME=your_salesforce_username@domain.com
os.environ['SF_PASSWORD=your_salesforce_password
os.environ['SF_SECURITY_TOKEN=your_salesforce_security_token
os.environ['SYNC_AUTH_TOKEN=your_sync_auth_token
os.environ['SYNC_USERNAME=your_sync_username
os.environ['SYNC_PASSWORD=your_sync_password
os.environ['ENCRYPTION_KEY=your_base64_encryption_key

# Also try to load from .env file as fallback
load_dotenv(os.path.join(project_root, '.env'))

# Debug: Check if environment variables are loaded
print("=== Environment Variable Debug ===")
print(f"SF_USERNAME: {'SET' if os.getenv('SF_USERNAME') else 'NOT SET'}")
print(f"SF_PASSWORD: {'SET' if os.getenv('SF_PASSWORD') else 'NOT SET'}")
print(f"SF_SECURITY_TOKEN: {'SET' if os.getenv('SF_SECURITY_TOKEN') else 'NOT SET'}")
if os.getenv('SF_USERNAME'):
    print(f"SF_USERNAME value: {os.getenv('SF_USERNAME')}")
if os.getenv('SF_SECURITY_TOKEN'):
    print(f"SF_SECURITY_TOKEN length: {len(os.getenv('SF_SECURITY_TOKEN'))}")
print("=================================")

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
