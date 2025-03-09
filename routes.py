# routes.py

from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from forms import LoginForm
from models import User, db, UpcomingEvent


# Create a blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index')) 

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# Create a blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Get initial events from database and convert to dict
    events = [event.to_dict() for event in UpcomingEvent.query.all()]
    return render_template('dashboard.html', initial_events=events)

# Create a blueprint for upcoming events
upcoming_events_bp = Blueprint('upcoming_events', __name__)

@upcoming_events_bp.route('/sync_upcoming_events', methods=['POST'])
@login_required
def sync_upcoming_events_endpoint():
    """HTTP endpoint for manual sync trigger"""
    result = sync_upcoming_events()
    return jsonify(result)

def sync_upcoming_events():
    """Sync upcoming events from Salesforce"""
    try:
        today = datetime.now().date()
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Add logging for deletion
        print("Starting sync process...")
        
        deleted_count = UpcomingEvent.query.filter(
            or_(
                UpcomingEvent.start_date < yesterday,
                UpcomingEvent.available_slots <= 0
            )
        ).delete()
        db.session.commit()
        print(f"Deleted {deleted_count} past/filled events")

        # Salesforce connection
        print("Connecting to Salesforce...")
        sf = Salesforce(
            username=Config.SF_USERNAME,
            password=Config.SF_PASSWORD,
            security_token=Config.SF_SECURITY_TOKEN,
            domain='login'
        )

        # Query execution
        print("Executing Salesforce query...")
        query = """
            SELECT Id, Name, Available_slots__c, Filled_Volunteer_Jobs__c, 
                Date_and_Time_for_Cal__c, Session_Type__c, Registration_Link__c, 
                Display_on_Website__c, Start_Date__c 
                FROM Session__c 
                WHERE Start_Date__c > TODAY 
                AND Available_slots__c > 0
                ORDER BY Start_Date__c ASC
        """
        result = sf.query(query)
        events = result.get('records', [])
        print(f"Retrieved {len(events)} events from Salesforce")
        
        # Print first event for debugging
        if events:
            print("Sample event data:", events[0])

        # Update database
        print("Updating database...")
        new_count, updated_count = UpcomingEvent.upsert_from_salesforce(events)
        
        return {
            'success': True,
            'new_count': new_count,
            'updated_count': updated_count,
            'deleted_count': deleted_count
        }
    except Exception as e:
        print(f"Scheduler sync error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@upcoming_events_bp.route('/volunteer_signup')
def volunteer_signup():
    # Get initial events from database where display_on_website is True, ordered by date
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(display_on_website=True).order_by(UpcomingEvent.start_date).all()]
    return render_template('signup.html', initial_events=events)

@upcoming_events_bp.route('/volunteer_signup_api')
def volunteer_signup_api():
    # Get initial events from database where display_on_website is True, ordered by date
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(display_on_website=True).order_by(UpcomingEvent.start_date).all()]

    # Return JSON response directly
    return jsonify(events)

@upcoming_events_bp.route('/toggle-event-visibility', methods=['POST'])
@login_required
def toggle_event_visibility():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        visible = data.get('visible')
        
        print(f"Toggling event {event_id} to visibility: {visible}")  # Debug log
        
        event = UpcomingEvent.query.filter_by(salesforce_id=event_id).first()
        if not event:
            print(f"Event not found with ID: {event_id}")  # Debug log
            return jsonify({
                'success': False,
                'message': 'Event not found'
            }), 404
        
        # Print before state
        print(f"Before update - Event {event_id} visibility: {event.display_on_website}")
        
        event.display_on_website = visible
        db.session.commit()
        
        # Verify the update
        db.session.refresh(event)
        print(f"After update - Event {event_id} visibility: {event.display_on_website}")
        
        return jsonify({
            'success': True,
            'message': f'Event visibility {"enabled" if visible else "disabled"}',
            'current_state': event.display_on_website
        })
        
    except Exception as e:
        print(f"Error in toggle_event_visibility: {str(e)}")  # Debug log
        db.session.rollback()  # Roll back on error
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@upcoming_events_bp.route('/upcoming_event_management')
@login_required
def upcoming_event_management():
    # Get initial events from database and convert to dict
    events = [event.to_dict() for event in UpcomingEvent.query.all()]
    return render_template('events/upcoming_event_management.html', initial_events=events)

@upcoming_events_bp.route('/dia_events_api')
def dia_events_api():
    try:
        # Connect to Salesforce
        sf = Salesforce(
            username=Config.SF_USERNAME,
            password=Config.SF_PASSWORD,
            security_token=Config.SF_SECURITY_TOKEN,
            domain='login'
        )

        # Query for DIA events
        query = """
            SELECT Id, Name, Available_slots__c, Filled_Volunteer_Jobs__c, 
                Date_and_Time_for_Cal__c, Session_Type__c, Registration_Link__c, 
                Display_on_Website__c, Start_Date__c 
            FROM Session__c 
            WHERE Start_Date__c > TODAY 
            AND Session_Type__c = 'DIA - Classroom Speaker'
            AND Available_slots__c > 0
            ORDER BY Start_Date__c ASC
        """
        result = sf.query(query)
        events = result.get('records', [])

        # Return JSON response directly
        return jsonify(events)

    except SalesforceAuthenticationFailed:
        return jsonify({
            'success': False,
            'message': 'Failed to authenticate with Salesforce'
        }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

def sync_recent_salesforce_data():
    """Sync all data from Salesforce sequentially"""
    import_sequence = [
        ('/organizations/import-from-salesforce', 'Organizations'),
        ('/management/import-schools', 'Schools'),
        ('/management/import-classes', 'Classes'),
        ('/volunteers/import-from-salesforce', 'Volunteers'),
        ('/organizations/import-affiliations-from-salesforce', 'Affiliations'),
        ('/events/import-from-salesforce', 'Events'),
        ('/history/import-from-salesforce', 'History')
    ]
    
    success_count = 0
    error_count = 0
    results = []
    
    for route, name in import_sequence:
        try:
            # Create a request context since we're in a background task
            with current_app.test_client() as client:
                response = client.post(route)
                data = response.get_json()
                
                if data.get('success'):
                    success_count += 1
                    results.append(f"Successfully imported {name}")
                else:
                    error_count += 1
                    results.append(f"Failed to import {name}: {data.get('error', 'Unknown error')}")
        except Exception as e:
            error_count += 1
            results.append(f"Error importing {name}: {str(e)}")
    
    return {
        'success': error_count == 0,
        'success_count': success_count,
        'error_count': error_count,
        'details': results
    }

@upcoming_events_bp.route('/sync_recent_salesforce_data', methods=['POST'])
@login_required
def sync_recent_salesforce_data_endpoint():
    """HTTP endpoint for full data sync trigger"""
    result = sync_recent_salesforce_data()
    return jsonify(result)

# Function to register all blueprints
def init_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upcoming_events_bp, url_prefix='/events')