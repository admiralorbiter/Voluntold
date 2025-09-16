from datetime import datetime, timezone
from models import db

class EventSchoolMapping(db.Model):
    __tablename__ = 'event_school_mappings'
    
    """Provides a model for mapping events to PrepKC's associated schools"""

    event_id = db.Column(db.Integer, db.ForeignKey('upcoming_events.id'), primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school_mappings.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) 