from flask import Blueprint, jsonify, render_template
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from config import Config
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


@dia_events_bp.route('/dia_events_api')
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
            AND Session_Type__c LIKE '%DIA%'
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