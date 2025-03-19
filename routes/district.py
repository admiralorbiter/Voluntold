from flask import Blueprint, render_template
from models.school_mapping import SchoolMapping
from models.upcoming_event import UpcomingEvent
from sqlalchemy import distinct
from models import db

bp = Blueprint('district', __name__)

@bp.route('/districts')
def list_districts():
    """Show list of all districts"""
    # Get unique districts from school mappings
    districts = db.session.query(distinct(SchoolMapping.district)).order_by(SchoolMapping.district).all()
    districts = [d[0] for d in districts]  # Extract district names from tuples
    
    return render_template('districts/districts.html', districts=districts)

@bp.route('/districts/<string:district_name>')
def district_events(district_name):
    """Show events for a specific district"""
    # Get all schools in the district
    schools = SchoolMapping.query.filter_by(district=district_name).all()
    
    # Get all events associated with these schools
    events = []
    for school in schools:
        events.extend(school.events.filter_by(display_on_website=True).all())
    
    # Remove duplicates and sort by date
    events = list(set(events))
    events.sort(key=lambda x: x.start_date)
    
    return render_template('districts/show.html', 
                         district_name=district_name, 
                         schools=schools,
                         events=events)
