from flask import Blueprint, jsonify, render_template
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from config import Config
from models import db
from models.upcoming_event import UpcomingEvent
from models.event_district_mapping import EventDistrictMapping
from datetime import datetime
import logging

dia_events_bp = Blueprint('dia_events', __name__)

@dia_events_bp.route('/dia_events')
def dia_events():
    # Get initial DIA events from database
    events = [
        event.to_dict() 
        for event in UpcomingEvent.query.filter(
            UpcomingEvent.event_type.like('%DIA%')
        ).all()
    ]
    return render_template('dia_events.html', initial_events=events)


@dia_events_bp.route('/dia_events_api')
def dia_events_api():
    try:
        # Get events from local database
        events = UpcomingEvent.query.filter(
            UpcomingEvent.event_type.ilike('%DIA%'),
            UpcomingEvent.start_date > datetime.utcnow(),
            UpcomingEvent.available_slots > 0
        ).order_by(UpcomingEvent.start_date.asc()).all()

        return jsonify([event.to_dict() for event in events])

    except Exception as e:
        logging.error(f"Error in dia_events_api: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

# DIA Events by District API (accessible via /events/api/dia/districts/<district_name>/events)
@dia_events_bp.route('/api/dia/districts/<string:district_name>/events')
def dia_events_by_district(district_name):
    """API endpoint to get DIA events for a specific district"""
    try:
        # Get DIA events for the specific district
        events = UpcomingEvent.query.join(
            EventDistrictMapping,
            UpcomingEvent.id == EventDistrictMapping.event_id
        ).filter(
            EventDistrictMapping.district == district_name,
            UpcomingEvent.event_type.ilike('%DIA%'),
            UpcomingEvent.start_date > datetime.utcnow(),
            UpcomingEvent.available_slots > 0
        ).order_by(UpcomingEvent.start_date.asc()).all()
        
        return jsonify([event.to_dict() for event in events])
        
    except Exception as e:
        logging.error(f"Error in dia_events_by_district: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

# All DIA Events with District Information (accessible via /events/api/dia/events)
@dia_events_bp.route('/api/dia/events')
def all_dia_events_with_districts():
    """API endpoint to get all DIA events with their district associations"""
    try:
        # Get all DIA events with their district mappings
        events = UpcomingEvent.query.filter(
            UpcomingEvent.event_type.ilike('%DIA%'),
            UpcomingEvent.start_date > datetime.utcnow(),
            UpcomingEvent.available_slots > 0
        ).order_by(UpcomingEvent.start_date.asc()).all()
        
        # Convert to dict and include district information
        event_list = []
        for event in events:
            event_dict = event.to_dict()
            # Get district associations for this event
            districts = [mapping.district for mapping in event.districts]
            event_dict['districts'] = districts
            event_list.append(event_dict)
        
        return jsonify(event_list)
        
    except Exception as e:
        logging.error(f"Error in all_dia_events_with_districts: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500