# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin

db = SQLAlchemy()

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salesforce_id = db.Column(db.String(18), unique=True, nullable=False)  # Salesforce IDs are 18 chars
    name = db.Column(db.String(255), nullable=False)
    available_slots = db.Column(db.Integer)
    filled_volunteer_jobs = db.Column(db.Integer)
    date_and_time = db.Column(db.String(100))  # Storing as string since format is "MM/DD/YYYY HH:MM AM/PM to HH:MM AM/PM"
    session_type = db.Column(db.String(50))
    registration_link = db.Column(db.Text)
    display_on_website = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert session to dictionary for JSON serialization"""
        return {
            'Id': self.salesforce_id,  # Match Salesforce API format
            'Name': self.name,
            'Available_Slots__c': self.available_slots,
            'Filled_Volunteer_Jobs__c': self.filled_volunteer_jobs,
            'Date_and_Time_for_Cal__c': self.date_and_time,
            'Session_Type__c': self.session_type,
            'Registration_Link__c': self.registration_link,
            'Display_on_Website__c': self.display_on_website
        }

    @classmethod
    def upsert_from_salesforce(cls, sf_data):
        """
        Update or insert session data from Salesforce.
        Returns tuple of (new_records_count, updated_records_count)
        """
        new_count = 0
        updated_count = 0
        
        for record in sf_data:
            existing = cls.query.filter_by(salesforce_id=record['Id']).first()
            
            session_data = {
                'salesforce_id': record['Id'],
                'name': record['Name'],
                'available_slots': int(record['Available_Slots__c'] or 0),
                'filled_volunteer_jobs': int(record['Filled_Volunteer_Jobs__c'] or 0),
                'date_and_time': record['Date_and_Time_for_Cal__c'],
                'session_type': record['Session_Type__c'],
                'registration_link': record['Registration_Link__c'],
                'display_on_website': bool(record['Display_on_Website__c'])
            }
            
            if existing:
                # Update existing record
                for key, value in session_data.items():
                    setattr(existing, key, value)
                updated_count += 1
            else:
                # Create new record
                new_session = cls(**session_data)
                db.session.add(new_session)
                new_count += 1
        
        db.session.commit()
        return (new_count, updated_count)
