#!/usr/bin/env python3
# sync_salesforce.py

from datetime import datetime, timedelta, timezone
import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app (needed for database)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///your_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define models (need to define both before establishing relationship)
class EventSchoolMapping(db.Model):
    __tablename__ = 'event_school_mappings'
    
    event_id = db.Column(db.Integer, db.ForeignKey('upcoming_events.id'), primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school_mappings.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class SchoolMapping(db.Model):
    __tablename__ = 'school_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(255), nullable=False)
    parent_salesforce_id = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'district': self.district,
            'parent_salesforce_id': self.parent_salesforce_id
        }

class UpcomingEvent(db.Model):
    __tablename__ = 'upcoming_events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salesforce_id = db.Column(db.String(18), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    available_slots = db.Column(db.Integer)
    filled_volunteer_jobs = db.Column(db.Integer)
    date_and_time = db.Column(db.String(100))
    event_type = db.Column(db.String(50), index=True)
    registration_link = db.Column(db.Text)
    display_on_website = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    start_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(20), default='active')
    note = db.Column(db.Text)

    # Define the relationship with SchoolMapping
    schools = db.relationship('SchoolMapping',
                            secondary='event_school_mappings',
                            backref=db.backref('events', lazy='dynamic'))

    def to_dict(self):
        data = {
            'id': self.id,
            'Id': self.salesforce_id,
            'Name': self.name,
            'Available_Slots__c': self.available_slots,
            'Filled_Volunteer_Jobs__c': self.filled_volunteer_jobs,
            'Date_and_Time_for_Cal__c': self.date_and_time,
            'Session_Type__c': self.event_type,
            'Registration_Link__c': self.registration_link,
            'Display_on_Website__c': self.display_on_website,
            'Start_Date__c': self.start_date.isoformat() if self.start_date else None,
            'note': self.note
        }
        data['schools'] = [school.to_dict() for school in self.schools]
        return data

    @classmethod
    def upsert_from_salesforce(cls, sf_data):
        new_count = 0
        updated_count = 0
        
        for record in sf_data:
            existing = cls.query.filter_by(salesforce_id=record['Id']).first()
            
            # Make start_date timezone-aware
            start_date = None
            if record['Start_Date__c']:
                try:
                    start_date = datetime.strptime(record['Start_Date__c'], '%Y-%m-%d')
                    start_date = start_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    logger.warning(f"Could not parse date {record['Start_Date__c']} for session {record['Id']}")
            
            event_data = {
                'salesforce_id': record['Id'],
                'name': record['Name'],
                'available_slots': int(record['Available_Slots__c'] or 0),
                'filled_volunteer_jobs': int(record['Filled_Volunteer_Jobs__c'] or 0),
                'date_and_time': record['Date_and_Time_for_Cal__c'],
                'event_type': record['Session_Type__c'],
                'registration_link': record['Registration_Link__c'],
                'start_date': start_date
            }
            
            if existing:
                for key, value in event_data.items():
                    setattr(existing, key, value)
                updated_count += 1
            else:
                event_data['display_on_website'] = record.get('Display_on_Website__c') == 'Yes'
                new_event = cls(**event_data)
                db.session.add(new_event)
                new_count += 1
        
        db.session.commit()
        return new_count, updated_count

def sync_upcoming_events():
    """Sync upcoming events from Salesforce"""
    try:
        logger.info("Starting sync process...")
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Delete old/filled events
        deleted_count = UpcomingEvent.query.filter(
            or_(
                UpcomingEvent.start_date < yesterday,
                UpcomingEvent.available_slots <= 0
            )
        ).delete()
        db.session.commit()
        logger.info(f"Deleted {deleted_count} past/filled events")

        # Connect to Salesforce
        logger.info("Connecting to Salesforce...")
        # Check credentials before attempting connection
        sf_username = os.getenv('SF_USERNAME')
        sf_password = os.getenv('SF_PASSWORD') # Be careful logging passwords
        sf_token = os.getenv('SF_SECURITY_TOKEN') # Be careful logging tokens

        # Log clearly what the script sees
        logger.info(f"SCRIPT_ENV: SF_USERNAME is set: {sf_username is not None}")
        # Avoid logging the actual password/token if possible, just confirm presence
        logger.info(f"SCRIPT_ENV: SF_PASSWORD is set: {sf_password is not None}") 
        logger.info(f"SCRIPT_ENV: SF_SECURITY_TOKEN is set: {sf_token is not None}")
        
        # You could log the username itself for confirmation
        logger.info(f"SCRIPT_ENV: Attempting login with username: {sf_username}")

        if not all([sf_username, sf_password, sf_token]):
            logger.error("SCRIPT_ENV: Salesforce credentials missing in environment for sync_script.py process.")
            return False # Stop the sync

        try:
            sf = Salesforce(
                username=sf_username,
                password=sf_password,
                security_token=sf_token,
                domain='login'
            )
        except SalesforceAuthenticationFailed as sf_auth_err:
             logger.error(f"SCRIPT_ENV: Salesforce Authentication Failed: {sf_auth_err}")
             # Log the username again to confirm it wasn't None
             logger.error(f"SCRIPT_ENV: Failed using username: {sf_username}")
             return False
        except Exception as e:
             logger.error(f"SCRIPT_ENV: Non-auth Salesforce connection error: {e}")
             return False

        # Query Salesforce
        logger.info("Executing Salesforce query...")
        query = """
            SELECT Id, Name, Available_slots__c, Filled_Volunteer_Jobs__c, 
                Date_and_Time_for_Cal__c, Session_Type__c, Registration_Link__c, 
                Display_on_Website__c, Start_Date__c 
            FROM Session__c 
            WHERE Start_Date__c > TODAY 
            AND Available_slots__c > 0
            ORDER BY Start_Date__c ASC
        """
        result = sf.query(query)
        events = result.get('records', [])
        logger.info(f"Retrieved {len(events)} events from Salesforce")

        # Get all salesforce IDs from the query results
        salesforce_ids = {event['Id'] for event in events}
        
        # Delete events that are no longer in Salesforce results
        additional_deleted = UpcomingEvent.query.filter(
            ~UpcomingEvent.salesforce_id.in_(salesforce_ids)
        ).delete()
        db.session.commit()
        logger.info(f"Deleted {additional_deleted} events that are no longer in Salesforce")

        # Update database
        logger.info("Updating database...")
        new_count, updated_count = UpcomingEvent.upsert_from_salesforce(events)
        
        logger.info(f"Sync completed: {new_count} new events, {updated_count} updated events, {deleted_count + additional_deleted} total deleted")
        return True

    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        # Run sync once and exit
        sync_upcoming_events()
