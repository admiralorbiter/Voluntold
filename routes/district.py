from flask import Blueprint, render_template
from models.school_mapping import SchoolMapping
from models.upcoming_event import UpcomingEvent
from models.event_district_mapping import EventDistrictMapping
from sqlalchemy import distinct
from models import db

bp = Blueprint('district', __name__)

@bp.route('/districts')
def list_districts():
    """Show list of all districts"""
    # Get unique districts from school mappings
    districts = db.session.query(distinct(SchoolMapping.district)).order_by(SchoolMapping.district).all()
    districts = [d[0] for d in districts]  # Extract district names from tuples
    
    # For each district, get the count of active events
    district_data = []
    for district in districts:
        event_count = EventDistrictMapping.query.join(
            UpcomingEvent, 
            EventDistrictMapping.event_id == UpcomingEvent.id
        ).filter(
            EventDistrictMapping.district == district,
            UpcomingEvent.display_on_website == True
        ).count()
        
        district_data.append({
            'name': district,
            'event_count': event_count
        })
    
    return render_template('districts/districts.html', districts=district_data)

@bp.route('/districts/<string:district_name>')
def district_events(district_name):
    """Show events for a specific district"""
    # Get all events associated with this district that are displayed on website
    events = UpcomingEvent.query.join(
        EventDistrictMapping,
        UpcomingEvent.id == EventDistrictMapping.event_id
    ).filter(
        EventDistrictMapping.district == district_name,
        UpcomingEvent.display_on_website == True
    ).order_by(UpcomingEvent.start_date).all()
    
    return render_template('districts/show.html', 
                         district_name=district_name,
                         events=events)
