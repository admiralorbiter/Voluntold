from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from models.upcoming_event import UpcomingEvent
from models.school_mapping import SchoolMapping
from models.event_district_mapping import EventDistrictMapping
from models import db
from sqlalchemy import distinct

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Show active events by default
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(status='active').order_by(UpcomingEvent.start_date).all()]
    return render_template('dashboard.html', initial_events=events)

@dashboard_bp.route('/api/districts/search')
def search_districts():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get unique districts from school mappings that match the query
    districts = SchoolMapping.query.with_entities(
        distinct(SchoolMapping.district)
    ).filter(
        SchoolMapping.district.ilike(f'%{query}%')
    ).all()
    
    # Extract district names from the result tuples
    district_names = [district[0] for district in districts]
    
    return jsonify(sorted(district_names))

@dashboard_bp.route('/events/api/events/<string:event_id>/districts', methods=['POST'])
@login_required
def add_district_to_event(event_id):
    try:
        data = request.get_json()
        district = data.get('district')
        
        if not district:
            return jsonify({'success': False, 'error': 'District is required'}), 400
            
        # Find event by salesforce_id instead of id
        event = UpcomingEvent.query.filter_by(salesforce_id=event_id).first_or_404()
        
        # Check if mapping already exists
        existing = EventDistrictMapping.query.filter_by(
            event_id=event.id,  # Use the internal ID
            district=district
        ).first()
        
        if not existing:
            # Create new mapping
            mapping = EventDistrictMapping(event_id=event.id, district=district)
            db.session.add(mapping)
            db.session.commit()
        
        # Get all districts for this event
        districts = [m.district for m in EventDistrictMapping.query.filter_by(event_id=event.id).all()]
        
        return jsonify({
            'success': True,
            'districts': sorted(districts)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/events/api/events/<string:event_id>/districts/<string:district>', methods=['DELETE'])
@login_required
def remove_district_from_event(event_id, district):
    try:
        # Find event by salesforce_id
        event = UpcomingEvent.query.filter_by(salesforce_id=event_id).first_or_404()
        
        # Find and delete the mapping
        mapping = EventDistrictMapping.query.filter_by(
            event_id=event.id,  # Use the internal ID
            district=district
        ).first()
        
        if mapping:
            db.session.delete(mapping)
            db.session.commit()
        
        # Get remaining districts for this event
        districts = [m.district for m in EventDistrictMapping.query.filter_by(event_id=event.id).all()]
        
        return jsonify({
            'success': True,
            'districts': sorted(districts)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/archive')
@login_required
def dashboard_archive():
    # Show archived events
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(status='archived').order_by(UpcomingEvent.start_date).all()]
    return render_template('dashboard.html', initial_events=events, view_type='archive')

@dashboard_bp.route('/api/events/archive')
@login_required
def get_archived_events():
    # API endpoint to get archived events
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(status='archived').order_by(UpcomingEvent.start_date).all()]
    return jsonify(events)

@dashboard_bp.route('/virtual-events')
@login_required
def virtual_events_dashboard():
    # Show virtual events
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(source='virtual').order_by(UpcomingEvent.start_date).all()]
    return render_template('virtual_events_dashboard.html', initial_events=events)