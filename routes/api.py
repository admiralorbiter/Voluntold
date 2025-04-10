from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from models import db
from models.user import User, SecurityLevel
from functools import wraps
import logging

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