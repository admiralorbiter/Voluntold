from datetime import datetime, timezone
import re
from models import db
from sqlalchemy.orm import validates
from models.event_district_mapping import EventDistrictMapping

class UpcomingEvent(db.Model):
    """
    Represents an upcoming event synchronized from Salesforce.
    Handles the display of events on the website and tracks volunteer registration status.
    """
    
    __tablename__ = 'upcoming_events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salesforce_id = db.Column(db.String(18), unique=True, nullable=True)  # Made nullable for virtual events
    name = db.Column(db.String(255), nullable=False)
    available_slots = db.Column(db.Integer)
    filled_volunteer_jobs = db.Column(db.Integer)
    date_and_time = db.Column(db.String(100))  # Storing as string since format is "MM/DD/YYYY HH:MM AM/PM to HH:MM AM/PM"
    event_type = db.Column(db.String(50), index=True)
    registration_link = db.Column(db.Text)
    display_on_website = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    start_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(20), default='active')
    note = db.Column(db.Text)
    
    # Virtual event fields
    source = db.Column(db.String(20), default='salesforce', index=True)  # 'salesforce' or 'virtual'
    spreadsheet_id = db.Column(db.String(255), nullable=True)  # Google Sheet ID for virtual events
    presenter_name = db.Column(db.String(255), nullable=True)
    presenter_organization = db.Column(db.String(255), nullable=True)
    presenter_location = db.Column(db.String(100), nullable=True)  # Local (KS/MO) or Not local
    topic_theme = db.Column(db.String(255), nullable=True)
    teacher_name = db.Column(db.String(255), nullable=True)
    school_level = db.Column(db.String(50), nullable=True)  # Elementary, High, etc.

    # Replace the schools relationship with districts
    districts = db.relationship('EventDistrictMapping',
                              backref=db.backref('event'),
                              lazy='dynamic')

    def to_dict(self):
        """Convert event to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'Id': self.salesforce_id,
            'Name': self.name,
            'name': self.name,  # Add lowercase version for frontend compatibility
            'Available_Slots__c': self.available_slots,
            'available_slots': self.available_slots,  # Add lowercase version
            'Filled_Volunteer_Jobs__c': self.filled_volunteer_jobs,
            'filled_volunteer_jobs': self.filled_volunteer_jobs,  # Add lowercase version
            'Date_and_Time_for_Cal__c': self.date_and_time,
            'date_and_time': self.date_and_time,  # Add lowercase version
            'Session_Type__c': self.event_type,
            'event_type': self.event_type,  # Add lowercase version
            'Registration_Link__c': self.registration_link,
            'registration_link': self.registration_link,  # Add lowercase version
            'Display_on_Website__c': self.display_on_website,
            'display_on_website': self.display_on_website,  # Add lowercase version
            'Start_Date__c': self.start_date.isoformat() if self.start_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,  # Add lowercase version
            'note': self.note,
            'status': self.status,
            'source': self.source,
            'spreadsheet_id': self.spreadsheet_id,
            'presenter_name': self.presenter_name,
            'presenter_organization': self.presenter_organization,
            'presenter_location': self.presenter_location,
            'topic_theme': self.topic_theme,
            'teacher_name': self.teacher_name,
            'school_level': self.school_level
        }
        # Replace schools with districts in the dictionary
        data['districts'] = [mapping.district for mapping in self.districts]
        return data

    @validates('available_slots', 'filled_volunteer_jobs')
    def validate_slots(self, key, value):
        """Ensure slot counts are non-negative integers"""
        if value is not None:
            try:
                # Handle string or float inputs from Salesforce
                value = int(float(str(value)))
                if value < 0:
                    raise ValueError(f"{key} cannot be negative")
            except (ValueError, TypeError):
                raise ValueError(f"{key} must be a valid number")
        return value

    @validates('registration_link')
    def validate_url(self, key, value):
        """
        Validate and extract URL from registration link.
        Handles both raw URLs and HTML anchor tags.
        """
        if not value:
            return value
        
        # Skip validation for header rows or non-URL values
        if value in ['Session Link', 'Registration_Link__c'] or not value.startswith(('http://', 'https://')):
            # If it's not a URL, return None (will be handled by the import logic)
            return None
        
        # If it's an HTML anchor tag, extract the href
        if value.startswith('<a') and 'href=' in value:
            href_match = re.search(r'href=[\'"]?([^\'" >]+)', value)
            if href_match:
                value = href_match.group(1)
        
        # Validate the URL
        if not value.startswith(('http://', 'https://')):
            raise ValueError("Registration link must be a valid URL")
        
        return value

    @classmethod
    def upsert_from_salesforce(cls, sf_data):
        """
        Update or insert event data from Salesforce.
        
        Args:
            sf_data (list): List of dictionaries containing Salesforce event data
            
        Returns:
            tuple: (new_records_count, updated_records_count)
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
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
                    print(f"Warning: Could not parse date {record['Start_Date__c']} for session {record['Id']}")
            
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
                # Don't include display_on_website in the update
                for key, value in event_data.items():
                    setattr(existing, key, value)
                
                # If event becomes available again, reactivate it
                if existing.status == 'archived' and event_data['available_slots'] > 0:
                    existing.status = 'active'
                    print(f"Reactivating archived event: {existing.name}")
                
                # Explicitly preserve display_on_website
                updated_count += 1
            else:
                # Only set display_on_website for new records
                if record.get('Display_on_Website__c') == 'Yes':
                    event_data['display_on_website'] = True
                else:
                    event_data['display_on_website'] = False
                new_event = cls(**event_data)
                db.session.add(new_event)
                new_count += 1
        
        db.session.commit()
        return (new_count, updated_count)

    @classmethod
    def upsert_from_virtual_sheet(cls, sheet_data, spreadsheet_id):
        """
        Update or insert virtual event data from Google Sheets.
        
        Args:
            sheet_data (list): List of dictionaries containing virtual event data
            spreadsheet_id (str): Google Sheet ID for tracking
            
        Returns:
            tuple: (new_records_count, updated_records_count, skipped_records_count)
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        new_count = 0
        updated_count = 0
        skipped_count = 0
        
        for record in sheet_data:
            # Skip header rows
            if record.get('Session Link') in ['Session Link', 'Registration_Link__c']:
                skipped_count += 1
                continue
            
            # Skip rows without Session Link (not ready-to-go)
            if not record.get('Session Link') or not record['Session Link'].strip():
                skipped_count += 1
                continue
                
            # Skip canceled events
            if record.get('Status') == 'canceled':
                skipped_count += 1
                continue
            
            # Only import rows with no Status AND no Presenter (upcoming events needing volunteers)
            # Skip rows that already have presenters assigned
            status = record.get('Status', '').strip()
            presenter = record.get('Presenter', '').strip()
            
            if presenter:
                # Has presenter - already assigned, skip
                skipped_count += 1
                continue
            
            # Create a unique identifier for virtual events using registration link
            registration_link = record['Session Link'].strip()
            existing = cls.query.filter_by(
                registration_link=registration_link,
                source='virtual'
            ).first()
            
            # Parse date and time
            date_str = record.get('Date', '').strip()
            time_str = record.get('Time', '').strip()
            date_and_time = f"{date_str} {time_str}".strip()
            
            # Parse start_date for sorting
            start_date = None
            if date_str:
                try:
                    # Handle format like "9/3/2025"
                    start_date = datetime.strptime(date_str, '%m/%d/%Y')
                    start_date = start_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    print(f"Warning: Could not parse date {date_str} for virtual event {record.get('Session Title', 'Unknown')}")
            
            event_data = {
                'name': record['Session Title'].strip(),
                'source': 'virtual',
                'spreadsheet_id': spreadsheet_id,
                'date_and_time': date_and_time,
                'event_type': record.get('Session Type', '').strip(),
                'registration_link': registration_link,
                'display_on_website': True,  # Default to visible for virtual events
                'status': 'active',
                'start_date': start_date,
                'presenter_name': record.get('Presenter', '').strip() or None,
                'presenter_organization': record.get('Organization', '').strip() or None,
                'presenter_location': record.get('Presenter Location', '').strip() or None,
                'topic_theme': record.get('Topic/Theme', '').strip() or None,
                'teacher_name': record.get('Teacher Name', '').strip() or None,
                'school_level': record.get('School Level', '').strip() or None,
                'available_slots': 50,  # Default for virtual events
                'filled_volunteer_jobs': 0,  # Default for virtual events
                'note': None  # No note needed for virtual events
            }
            
            if existing:
                # Update existing virtual event
                for key, value in event_data.items():
                    setattr(existing, key, value)
                updated_count += 1
            else:
                # Create new virtual event
                new_event = cls(**event_data)
                db.session.add(new_event)
                new_count += 1
        
        db.session.commit()
        return (new_count, updated_count, skipped_count)

    @classmethod
    def needs_refresh(cls):
        """Check if the local data needs to be refreshed"""
        last_updated = db.session.query(db.func.max(cls.updated_at)).scalar()
        if not last_updated:
            return True
        # Refresh if data is older than 6 hours
        return (datetime.now(timezone.utc) - last_updated).total_seconds() > 21600  # 6 hours in seconds