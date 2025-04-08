from flask import Blueprint, render_template
from models.school_mapping import SchoolMapping
from models.upcoming_event import UpcomingEvent
from models.event_district_mapping import EventDistrictMapping
from sqlalchemy import distinct
from models import db

bp = Blueprint('district', __name__)

@bp.route('/districts')
def list_districts():
    """Show list of all districts with their linked event counts"""
    # Get unique districts from event district mappings
    districts = db.session.query(distinct(EventDistrictMapping.district)).order_by(EventDistrictMapping.district).all()
    districts = [d[0] for d in districts]  # Extract district names from tuples
    
    # For each district, get the count of all linked events
    district_data = []
    for district in districts:
        # Get total events count (both visible and non-visible)
        total_events = EventDistrictMapping.query.join(
            UpcomingEvent, 
            EventDistrictMapping.event_id == UpcomingEvent.id
        ).filter(
            EventDistrictMapping.district == district
        ).count()
        
        # Get visible events count
        visible_events = EventDistrictMapping.query.join(
            UpcomingEvent, 
            EventDistrictMapping.event_id == UpcomingEvent.id
        ).filter(
            EventDistrictMapping.district == district,
            UpcomingEvent.display_on_website == True
        ).count()
        
        district_data.append({
            'name': district,
            'event_count': total_events,
            'visible_event_count': visible_events
        })
    
    return render_template('districts/districts.html', districts=district_data)

@bp.route('/districts/<string:district_name>')
def district_events(district_name):
    """Show events for a specific district"""
    # Get all events linked to this district
    events = UpcomingEvent.query.join(
        EventDistrictMapping,
        UpcomingEvent.id == EventDistrictMapping.event_id
    ).filter(
        EventDistrictMapping.district == district_name
    ).order_by(UpcomingEvent.start_date).all()
    
    # Convert events to dictionary format
    event_list = []
    for event in events:
        event_dict = {
            'name': event.name,
            'date_and_time': event.date_and_time,
            'available_slots': event.available_slots,
            'filled_volunteer_jobs': event.filled_volunteer_jobs,
            'event_type': event.event_type,
            'registration_link': event.registration_link,
            'note': event.note,
            'display_on_website': event.display_on_website
        }
        event_list.append(event_dict)
    
    # Get schools in this district
    schools = SchoolMapping.query.filter_by(district=district_name).all()
    
    return render_template('districts/show.html', 
                         district_name=district_name,
                         events=event_list,
                         schools=schools)
