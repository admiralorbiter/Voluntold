from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from models import db
from models.user import User, SecurityLevel
from functools import wraps
import logging
from datetime import datetime, timezone, timedelta

# Create a blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Create a logger for API actions
logger = logging.getLogger('api')

def token_required(f):
    """Decorator to check if API token is valid"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({'error': 'API token is missing'}), 401
        
        user = User.find_by_api_token(token)
        if not user or not user.check_api_token(token):
            return jsonify({'error': 'Invalid or expired API token'}), 401
        
        return f(user, *args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @token_required
    def decorated(user, *args, **kwargs):
        if not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(user, *args, **kwargs)
    return decorated

@api_bp.route('/token', methods=['POST'])
def generate_token():
    """Generate an API token"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # This should use your actual authentication logic
    # For demonstration purposes only
    from werkzeug.security import check_password_hash
    
    user = User.find_by_username_or_email(username)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = user.generate_api_token()
    return jsonify({
        'token': token,
        'expires_at': user.token_expiry.isoformat()
    }), 200

@api_bp.route('/token/revoke', methods=['POST'])
@token_required
def revoke_token(user):
    """Revoke the current API token"""
    user.revoke_api_token()
    return jsonify({'message': 'Token revoked successfully'}), 200

@api_bp.route('/token/refresh', methods=['POST'])
@token_required
def refresh_token(user):
    """Refresh the current API token"""
    token = user.generate_api_token()
    return jsonify({
        'token': token,
        'expires_at': user.token_expiry.isoformat()
    }), 200

@api_bp.route('/users/sync', methods=['GET'])
@token_required
def sync_users(user):
    """
    Get all users for synchronization.
    Only admin users can access all user data.
    """
    if not user.has_permission_level(SecurityLevel.ADMIN):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user, user_id):
    """Get a specific user by ID"""
    target_user = User.query.get(user_id)
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions - only allow if the requesting user:
    # 1. Is requesting their own data, or
    # 2. Has permission to manage the target user
    if user.id != target_user.id and not user.can_manage_user(target_user):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    return jsonify(target_user.to_dict()), 200

@api_bp.route('/users/update', methods=['POST'])
@token_required
def update_users(user):
    """
    Update or create users from sync data.
    Only admins can perform this operation.
    """
    if not user.has_permission_level(SecurityLevel.ADMIN):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    if not data or not isinstance(data.get('users'), list):
        return jsonify({'error': 'Invalid request format'}), 400
    
    user_data_list = data.get('users')
    results = {
        'created': 0,
        'updated': 0,
        'failed': 0,
        'errors': []
    }
    
    for user_data in user_data_list:
        try:
            # Ensure required fields are present
            if not all(key in user_data for key in ('username', 'email')):
                results['failed'] += 1
                results['errors'].append(f"Missing required fields for user: {user_data.get('username', 'unknown')}")
                continue
            
            # Check if user exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            
            if existing_user:
                # Update existing user
                for key, value in user_data.items():
                    if key != 'password_hash' and hasattr(existing_user, key):
                        setattr(existing_user, key, value)
                results['updated'] += 1
            else:
                # Create new user
                new_user = User(**user_data)
                db.session.add(new_user)
                results['created'] += 1
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(str(e))
    
    db.session.commit()
    return jsonify(results), 200 

@api_bp.route('/test/events', methods=['GET'])
def test_events():
    """Test API endpoint with static event data for development/testing"""
    
    # Get query parameters for testing different scenarios
    event_count = request.args.get('count', 5, type=int)
    days_ahead = request.args.get('days_ahead', 30, type=int)
    district_name = request.args.get('district', 'Test School District', type=str)
    
    # Generate test events with various dates
    test_events = []
    base_date = datetime.now(timezone.utc)
    
    event_types = ['Reading Session', 'Math Tutoring', 'Science Lab', 'Art Workshop', 'PE Activity']
    event_names = [
        'Elementary Reading Help',
        'Middle School Math Support',
        'High School Science Lab',
        'Creative Arts Workshop',
        'Physical Education Support',
        'Library Organization',
        'Computer Lab Assistance',
        'Music Room Help',
        'Cafeteria Support',
        'Playground Supervision'
    ]
    
    for i in range(min(event_count, 20)):  # Cap at 20 events
        # Generate dates spread across the next N days
        days_offset = (i * days_ahead) // event_count
        event_date = base_date + timedelta(days=days_offset)
        
        # Create event data matching your UpcomingEvent model structure
        event_data = {
            'id': f'test_{i+1}',
            'Id': f'test_sf_{i+1:06d}',  # Fake Salesforce ID
            'Name': event_names[i % len(event_names)],
            'Available_Slots__c': 5 + (i % 10),  # 5-14 slots
            'Filled_Volunteer_Jobs__c': i % 3,   # 0-2 filled
            'Date_and_Time_for_Cal__c': f"{event_date.strftime('%m/%d/%Y')} 9:00 AM to 11:00 AM",
            'Session_Type__c': event_types[i % len(event_types)],
            'Registration_Link__c': f'https://example.com/register/test-event-{i+1}',
            'Display_on_Website__c': True,
            'Start_Date__c': event_date.isoformat(),
            'note': f'Test event #{i+1} for {district_name}',
            'districts': [district_name]
        }
        
        test_events.append(event_data)
    
    # Add some events with different statuses for testing
    if event_count > 5:
        # Add a past event
        past_event = {
            'id': 'test_past',
            'Id': 'test_sf_past',
            'Name': 'Past Test Event',
            'Available_Slots__c': 3,
            'Filled_Volunteer_Jobs__c': 2,
            'Date_and_Time_for_Cal__c': f"{(base_date - timedelta(days=5)).strftime('%m/%d/%Y')} 2:00 PM to 4:00 PM",
            'Session_Type__c': 'Past Session',
            'Registration_Link__c': 'https://example.com/register/past-event',
            'Display_on_Website__c': False,
            'Start_Date__c': (base_date - timedelta(days=5)).isoformat(),
            'note': 'This is a past test event',
            'districts': [district_name]
        }
        test_events.append(past_event)
    
    return jsonify({
        'message': 'Test events generated successfully',
        'district': district_name,
        'total_events': len(test_events),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'events': test_events
    })

@api_bp.route('/test/districts', methods=['GET'])
def test_districts():
    """Test API endpoint that returns fake district data"""
    
    test_districts = [
        {
            'name': 'Test School District',
            'event_count': 15,
            'visible_event_count': 12
        },
        {
            'name': 'Fake Academy District',
            'event_count': 8,
            'visible_event_count': 6
        },
        {
            'name': 'Mock Charter School District',
            'event_count': 22,
            'visible_event_count': 18
        }
    ]
    
    return jsonify({
        'message': 'Test districts generated successfully',
        'districts': test_districts,
        'total_districts': len(test_districts)
    })

@api_bp.route('/test/events/<string:district_name>', methods=['GET'])
def test_district_events(district_name):
    """Test API endpoint that mimics the district events endpoint with fake data"""
    
    # Get query parameters
    event_count = request.args.get('count', 8, type=int)
    days_ahead = request.args.get('days_ahead', 60, type=int)
    
    # Generate test events for the specific district
    test_events = []
    base_date = datetime.now(timezone.utc)
    
    event_types = ['Reading Session', 'Math Tutoring', 'Science Lab', 'Art Workshop', 'PE Activity']
    event_names = [
        f'{district_name} Reading Help',
        f'{district_name} Math Support',
        f'{district_name} Science Lab',
        f'{district_name} Art Workshop',
        f'{district_name} PE Support',
        f'{district_name} Library Help',
        f'{district_name} Computer Lab',
        f'{district_name} Music Room'
    ]
    
    for i in range(min(event_count, 20)):
        days_offset = (i * days_ahead) // event_count
        event_date = base_date + timedelta(days=days_offset)
        
        event_data = {
            'id': f'test_{district_name.lower().replace(" ", "_")}_{i+1}',
            'Id': f'test_sf_{district_name.lower().replace(" ", "_")}_{i+1:06d}',
            'Name': event_names[i % len(event_names)],
            'Available_Slots__c': 3 + (i % 8),
            'Filled_Volunteer_Jobs__c': i % 4,
            'Date_and_Time_for_Cal__c': f"{event_date.strftime('%m/%d/%Y')} 9:00 AM to 11:00 AM",
            'Session_Type__c': event_types[i % len(event_types)],
            'Registration_Link__c': f'https://example.com/register/{district_name.lower().replace(" ", "-")}-event-{i+1}',
            'Display_on_Website__c': True,
            'Start_Date__c': event_date.isoformat(),
            'note': f'Test event #{i+1} for {district_name}',
            'districts': [district_name]
        }
        
        test_events.append(event_data)
    
    return jsonify(test_events) 