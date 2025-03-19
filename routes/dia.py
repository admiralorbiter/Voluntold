from flask import Blueprint, render_template
from models import db
from models.upcoming_event import UpcomingEvent

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
