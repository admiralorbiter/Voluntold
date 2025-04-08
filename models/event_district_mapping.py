from datetime import datetime, timezone
from models import db

class EventDistrictMapping(db.Model):
    __tablename__ = 'event_district_mappings'
    
    event_id = db.Column(db.Integer, db.ForeignKey('upcoming_events.id'), primary_key=True)
    district = db.Column(db.String(255), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) 