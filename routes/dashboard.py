from flask import Blueprint, render_template
from flask_login import login_required
from models.upcoming_event import UpcomingEvent

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    events = [event.to_dict() for event in UpcomingEvent.query.all()]
    return render_template('dashboard.html', initial_events=events)