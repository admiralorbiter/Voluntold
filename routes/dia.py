from flask import Blueprint, jsonify, render_template
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from config import Config
from models import db
from models.upcoming_event import UpcomingEvent
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