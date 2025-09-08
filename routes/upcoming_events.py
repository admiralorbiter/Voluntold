from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, jsonify, request, render_template
from flask_login import login_required
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from sqlalchemy import or_
from config import Config
from models import db
from models.upcoming_event import UpcomingEvent
from models.school_mapping import SchoolMapping

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
        
        # Archive events that are actually full (have filled jobs but no available slots)
        archived_count = UpcomingEvent.query.filter(
            UpcomingEvent.available_slots == 0,
            UpcomingEvent.filled_volunteer_jobs > 0
        ).update({'status': 'archived'})
        
        # Only delete events that are past their start date
        deleted_count = UpcomingEvent.query.filter(
            UpcomingEvent.start_date < yesterday
        ).delete()
        
        db.session.commit()
        print(f"Archived {archived_count} full events")
        print(f"Deleted {deleted_count} past events")

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
        
        # Get all salesforce IDs from the query results
        salesforce_ids = {event['Id'] for event in events}
        
        # Delete events that are no longer in Salesforce results
        additional_deleted = UpcomingEvent.query.filter(
            ~UpcomingEvent.salesforce_id.in_(salesforce_ids)
        ).delete()
        db.session.commit()
        print(f"Deleted {additional_deleted} events that are no longer in Salesforce")
        
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
            'deleted_count': deleted_count + additional_deleted,
            'archived_count': archived_count
        }
    except Exception as e:
        print(f"Scheduler sync error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@upcoming_events_bp.route('/volunteer_signup')
def volunteer_signup():
    # Get initial events from database where display_on_website is True and status is active, ordered by date
    # Only return Salesforce events (in-person events) for volunteer signup
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(
        display_on_website=True, 
        status='active',
        source='salesforce'  # Only Salesforce events for volunteer signup
    ).order_by(UpcomingEvent.start_date).all()]
    return render_template('signup.html', initial_events=events)

@upcoming_events_bp.route('/volunteer_signup_api')
def volunteer_signup_api():
    # Get initial events from database where display_on_website is True and status is active, ordered by date
    # Only return Salesforce events (in-person events) for volunteer signup
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(
        display_on_website=True, 
        status='active',
        source='salesforce'  # Only Salesforce events for volunteer signup
    ).order_by(UpcomingEvent.start_date).all()]

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
        
        event = UpcomingEvent.query.filter_by(salesforce_id=str(event_id)).first()
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
    # Get initial events from database and convert to dict (active events only)
    events = [event.to_dict() for event in UpcomingEvent.query.filter_by(status='active').order_by(UpcomingEvent.start_date).all()]
    return render_template('events/upcoming_event_management.html', initial_events=events)

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

@upcoming_events_bp.route('/displayed_events_api')
def displayed_events_api():
    try:
        # Get events from database where display_on_website is True, ordered by date
        events = UpcomingEvent.query.filter_by(display_on_website=True)\
            .order_by(UpcomingEvent.start_date)\
            .all()

        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        print(f"Error in displayed_events_api: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@upcoming_events_bp.route('/api/events/<int:event_id>/schools', methods=['GET', 'POST'])
@login_required
def manage_event_schools(event_id):
    print(f"Received request for event {event_id}")  # Debug log
    event = UpcomingEvent.query.get_or_404(event_id)
    
    if request.method == 'POST':
        data = request.get_json()
        school_ids = data.get('school_ids', [])
        
        # Get existing schools and add new ones
        existing_schools = set(school.id for school in event.schools)
        new_school_ids = [id for id in school_ids if id not in existing_schools]
        
        # Add new schools to existing ones
        new_schools = SchoolMapping.query.filter(SchoolMapping.id.in_(new_school_ids)).all()
        event.schools.extend(new_schools)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schools': [school.to_dict() for school in event.schools]
        })
    
    return jsonify({
        'schools': [school.to_dict() for school in event.schools]
    })

@upcoming_events_bp.route('/api/schools/search')
@login_required
def search_schools():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    schools = SchoolMapping.query.filter(
        db.or_(
            SchoolMapping.name.ilike(f'%{query}%'),
            SchoolMapping.district.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([school.to_dict() for school in schools])

@upcoming_events_bp.route('/api/events/<int:event_id>/schools/<int:school_id>', methods=['DELETE'])
@login_required
def remove_school_from_event(event_id, school_id):
    event = UpcomingEvent.query.get_or_404(event_id)
    school = SchoolMapping.query.get_or_404(school_id)
    
    if school in event.schools:
        event.schools.remove(school)
        db.session.commit()
        
    return jsonify({
        'success': True,
        'schools': [school.to_dict() for school in event.schools]
    })

@upcoming_events_bp.route('/api/events/<string:event_id>/note', methods=['PUT'])
@login_required
def update_event_note(event_id):
    try:
        print(f"Updating note for event: {event_id}")  # Debug log
        event = UpcomingEvent.query.filter_by(salesforce_id=event_id).first()
        
        if not event:
            print(f"Event not found with salesforce_id: {event_id}")
            return jsonify({'error': 'Event not found'}), 404
            
        data = request.get_json()
        note = data.get('note', '').strip()
        print(f"New note content: {note}")  # Debug log
        
        event.note = note if note else None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'note': event.note,
            'html': render_template('events/_note_display.html', note=event.note)
        })
            
    except Exception as e:
        print(f"Error updating note: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@upcoming_events_bp.route('/api/events/<string:event_id>/note', methods=['DELETE'])
@login_required
def delete_event_note(event_id):
    try:
        print(f"Deleting note for event: {event_id}")  # Debug log
        event = UpcomingEvent.query.filter_by(salesforce_id=event_id).first()
        
        if not event:
            print(f"Event not found with salesforce_id: {event_id}")
            return jsonify({'error': 'Event not found'}), 404
            
        event.note = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'html': render_template('events/_note_display.html', note=None)
        })
            
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500